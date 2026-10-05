"""
Test v2 : on force le LLM à recevoir un FAUX schéma.
Cette fois on vérifie qu'il (1) détecte l'incohérence, (2) corrige,
(3) EXÉCUTE le SQL, (4) donne les CHIFFRES.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import src.llm.prompts as prompts

FAKE_SCHEMA_PROMPT = """Tu es un data analyst expert qui interroge une base de données DuckDB.

## Contexte de la base
- `sales_data` : les transactions (sale_id, product_id, customer_id, date, quantity, revenue)
- `product_catalog` : les produits (product_id, name, category, unit_price)

## RÈGLE ABSOLUE
**Tu ne réponds JAMAIS sans avoir exécuté `run_sql` et obtenu un résultat chiffré.**
Écrire une requête n'est PAS une réponse. La réponse = les CHIFFRES.

## Méthode
1. Explore le schéma si nécessaire (`list_tables`, `describe_table`).
2. Écris du SQL et **exécute-le via `run_sql`**.
3. Donne les chiffres à l'utilisateur.

## Gestion des erreurs
Si un tool retourne "❌", lis l'erreur, corrige et réexécute. Ne réponds
à l'utilisateur qu'avec un résultat valide.
"""

prompts.SYSTEM_PROMPT = FAKE_SCHEMA_PROMPT

from src.agent.loop import run_agent


def test_self_healing_v2():
    print("=" * 70)
    print("TEST AUTO-CORRECTION v2 : faux schéma + exigence de chiffres")
    print("=" * 70)
    
    result = run_agent(
        "Quels sont les 3 produits qui ont le plus de revenus en 2024 ?"
    )
    
    print(f"\n📝 RÉPONSE FINALE :\n{result['answer']}")
    print(f"\n(tours: {result['turns']})")
    print(f"\n--- Historique des tools ---")
    for msg in result["messages"]:
        if msg["role"] == "assistant" and msg.get("tool_calls"):
            for tc in msg["tool_calls"]:
                print(f"  • {tc['function']['name']}({tc['function']['arguments'][:100]})")
    
    # Vérification automatique
    print(f"\n--- Vérification ---")
    tools_used = [
        tc["function"]["name"]
        for msg in result["messages"]
        if msg["role"] == "assistant" and msg.get("tool_calls")
        for tc in msg["tool_calls"]
    ]
    has_run_sql = "run_sql" in tools_used
    print(f"  ✓ run_sql exécuté : {has_run_sql}")
    print(f"  ✓ Chiffres dans la réponse : {'Laptop' in result['answer'] or '199' in result['answer'] or '€' in result['answer']}")


if __name__ == "__main__":
    test_self_healing_v2()