import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.llm.client import chat


def test_simple():
    print("=" * 60)
    print("TEST 1 : appel simple")
    print("=" * 60)

    messages = [
        {"role": "system", "content": "Tu réponds en une phrase maximum."},
        {"role": "user",   "content": "Qu'est-ce qu'un data analyst ?"},
    ]

    response = chat(messages)
    print(f"Réponse : {response.content}")
    print()


def test_system_prompt():
    print("=" * 60)
    print("TEST 2 : system prompt en JSON")
    print("=" * 60)

    messages = [
        {"role": "system", "content":
            "Tu réponds UNIQUEMENT en JSON valide. "
            "Format : {\"answer\": \"...\", \"confidence\": 0-1}"},
        {"role": "user", "content": "Paris est la capitale de quel pays ?"},
    ]

    response = chat(messages, temperature=0)
    print(f"Réponse : {response.content}")
    print()


def test_multi_turn():
    print("=" * 60)
    print("TEST 3 : conversation multi-tours")
    print("=" * 60)

    messages = [
        {"role": "system", "content": "Tu es un assistant concis."},
        {"role": "user",   "content": "Mon produit préféré est 'Air Purifier'."},
    ]
    r1 = chat(messages)
    print(f"Assistant 1 : {r1.content}")

    messages.append({"role": "assistant", "content": r1.content})
    messages.append({"role": "user", "content": "Quel est mon produit préféré ?"})

    r2 = chat(messages)
    print(f"Assistant 2 : {r2.content}")
    print()


if __name__ == "__main__":
    test_simple()
    test_system_prompt()
    test_multi_turn()