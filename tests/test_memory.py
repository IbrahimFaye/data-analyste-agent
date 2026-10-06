import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.agent.loop import run_agent


def test_conversation():
    print("=" * 70)
    print("TEST MÉMOIRE : conversation multi-tours")
    print("=" * 70)
    
    history = []
    
    print("\n>>> Question 1 : CA total 2024")
    r1 = run_agent("Quel est le chiffre d'affaires total en 2024 ?", history=history)
    print(f"\n💬 {r1['answer'][:300]}")
    history = r1["history"]
    
    print("\n>>> Question 2 : Et en 2023 ? (suivi)")
    r2 = run_agent("Et en 2023 ?", history=history)
    print(f"\n💬 {r2['answer'][:300]}")
    history = r2["history"]
    
    print("\n>>> Question 3 : Compare les deux (suivi)")
    r3 = run_agent("Compare les deux années.", history=history)
    print(f"\n💬 {r3['answer'][:400]}")
    history = r3["history"]
    
    print("\n>>> Question 4 : Fais-moi un graphique (suivi)")
    r4 = run_agent("Fais-moi un graphique comparatif.", history=history)
    print(f"\n💬 {r4['answer'][:400]}")
    
    print("\n" + "=" * 70)
    print("VÉRIFICATIONS")
    print("=" * 70)
    print(f"✓ Nombre total de messages dans l'historique final : {len(history)}")
    print(f"✓ Historique contient bien des rôles user/assistant uniquement : "
          f"{set(m['role'] for m in history) <= {'user', 'assistant'}}")


if __name__ == "__main__":
    test_conversation()