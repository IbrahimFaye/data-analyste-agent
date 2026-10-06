"""
Boucle agentique ReAct avec mémoire conversationnelle.
C'est ici que tout se joue : le LLM décide, les tools exécutent, on boucle.
"""

import json
from src.llm.client import chat
from src.llm.prompts import SYSTEM_PROMPT
from src.tools import ALL_TOOLS
from src.tools.sql_tools import execute_tool
from src.tools.plot_tools import reset_generated_charts, get_generated_charts

MAX_TURNS = 20


def run_agent(
    user_question: str,
    history: list[dict] | None = None,
    verbose: bool = True,
) -> dict:

    """
    Exécute l'agent sur une question, avec mémoire conversationnelle optionnelle.

    Args:
        user_question: la question de l'utilisateur (langage naturel)
        history: liste de messages précédents (role user/assistant UNIQUEMENT).
                 À passer au tour suivant pour que l'agent "se souvienne".
        verbose: afficher les tools appelés au fur et à mesure

    Returns:
        {
            "answer":   str,         # réponse finale en langage naturel
            "messages": list[dict],  # historique COMPLET de ce tour (debug)
            "history":  list[dict],  # historique ÉPURÉ à passer au tour suivant
            "turns":    int,         # nombre de tours LLM consommés
        }
    """
    reset_generated_charts()
    if history is None:
        history = []

    # ============================================================
    # 1. Construction des messages
    #    [system] + [historique passé] + [nouvelle question]
    # ============================================================
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *history,                                          # <-- la mémoire
        {"role": "user",   "content": user_question},
    ]

    # ============================================================
    # 2. Boucle ReAct
    # ============================================================
    response = None   # pour le cas MAX_TURNS atteint sans réponse

    for turn in range(1, MAX_TURNS + 1):
        if verbose:
            print(f"\n--- Tour {turn} ---")

        # 2.1 — On demande au LLM ce qu'il veut faire
        response = chat(messages, tools=ALL_TOOLS)

        # 2.2 — Cas 1 : le LLM a fini (pas de tool_call)
        if not response.tool_calls:
            if verbose:
                print(f"✅ Fin de la boucle au tour {turn}.")

            # On enrichit l'historique conversationnel :
            # on n'ajoute QUE la question et la réponse finale (pas les tools)
            new_history = history + [
                {"role": "user",      "content": user_question},
                {"role": "assistant", "content": response.content},
            ]

            return {
                "answer":   response.content,
                "messages": messages,      # tout le tour (debug)
                "history":  new_history,   # version épurée (pour la suite)
                "turns":    turn,
                "artifacts": get_generated_charts(),
            }

        # 2.3 — Cas 2 : le LLM veut appeler des outils
        # 2.3a — Ajouter la réponse de l'assistant (avec tool_calls) à l'historique
        messages.append({
            "role": "assistant",
            "content": response.content,   # souvent None quand il y a des tools
            "tool_calls": [
                {
                    "id":   tc.id,
                    "type": "function",
                    "function": {
                        "name":      tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in response.tool_calls
            ],
        })

        # 2.3b — Exécuter chaque tool et ajouter le résultat
        for tool_call in response.tool_calls:
            name     = tool_call.function.name
            raw_args = tool_call.function.arguments
            args     = json.loads(raw_args) if raw_args else {}

            if verbose:
                print(f"🔧 Tool: {name}({args})")

            try:
                result = execute_tool(name, args)
            except Exception as e:
                # On ne laisse JAMAIS une exception casser la boucle.
                # On renvoie l'erreur au LLM pour qu'il s'adapte.
                result = f"❌ Erreur d'exécution du tool '{name}': {e}"

            if verbose:
                preview = result[:200] + ("..." if len(result) > 200 else "")
                print(f"   └─ Résultat: {preview}")

            messages.append({
                "role":         "tool",
                "tool_call_id": tool_call.id,
                "content":      str(result),
            })

    # ============================================================
    # 3. Sécurité : MAX_TURNS atteint sans conclusion
    # ============================================================
    fallback_answer = (
        f"⚠️ L'agent n'a pas conclu en {MAX_TURNS} tours. "
        f"Dernier message : {response.content if response and response.content else '(vide)'}"
    )
    new_history = history + [
        {"role": "user",      "content": user_question},
        {"role": "assistant", "content": fallback_answer},
    ]
    return {
        "answer":   fallback_answer,
        "messages": messages,
        "history":  new_history,
        "turns":    MAX_TURNS,
        "artifacts": get_generated_charts(),
    }