import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.agent.loop import run_agent


def test_analysis():
    print("=" * 70)
    print("TEST : analyse avec détection d'anomalies")
    print("=" * 70)
    
    result = run_agent(
        "Analyse l'évolution du chiffre d'affaires mensuel en 2024. "
        "Y a-t-il des mois anormaux ? Donne-moi une tendance."
    )
    
    print(f"\n📝 RÉPONSE FINALE :\n{result['answer']}")
    print(f"\n(tours: {result['turns']})")
    print(f"\n--- Tools utilisés ---")
    for msg in result["messages"]:
        if msg["role"] == "assistant" and msg.get("tool_calls"):
            for tc in msg["tool_calls"]:
                print(f"  • {tc['function']['name']}")


if __name__ == "__main__":
    test_analysis()