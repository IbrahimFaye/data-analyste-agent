import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.agent.loop import run_agent


def test_chart():
    print("=" * 70)
    print("TEST : génération de graphique")
    print("=" * 70)
    
    result = run_agent(
        "Montre-moi l'évolution du chiffre d'affaires par mois en 2024 "
        "avec un graphique en ligne."
    )
    
    print(f"\n📝 RÉPONSE FINALE :\n{result['answer']}")
    print(f"\n(tours: {result['turns']})")
    
    # Vérifier qu'un fichier a bien été créé
    outputs = list(Path("outputs").glob("*.png"))
    print(f"\n📁 Graphiques présents dans outputs/ : {len(outputs)}")
    for f in outputs:
        print(f"   • {f.name}  ({f.stat().st_size // 1024} Ko)")


if __name__ == "__main__":
    test_chart()