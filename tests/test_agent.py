import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.agent.loop import run_agent


def test_simple():
    print("=" * 70)
    print("TEST : question simple")
    print("=" * 70)
    result = run_agent("Combien de ventes y a-t-il au total ?")
    print(f"\n📝 RÉPONSE FINALE :\n{result['answer']}")
    print(f"\n(tours: {result['turns']})")


def test_complex():
    print("\n" + "=" * 70)
    print("TEST : question complexe (nécessite exploration + analyse)")
    print("=" * 70)
    result = run_agent(
        "Quels sont les 3 produits qui ont généré le plus de revenus "
        "sur les 6 derniers mois de 2024 ?"
    )
    print(f"\n📝 RÉPONSE FINALE :\n{result['answer']}")
    print(f"\n(tours: {result['turns']})")


if __name__ == "__main__":
    #test_simple()
    test_complex()   