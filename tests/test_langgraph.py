import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.agent.loop import run_agent
from src.agent.graph import run_agent_langgraph
from pathlib import Path
from src.agent.graph import graph

def compare(question):
    print(f"\n{'='*70}\nQUESTION : {question}\n{'='*70}")
    
    print("\n--- Version MANUELLE ---")
    r1 = run_agent(question, verbose=False)
    print(f"Réponse : {r1['answer'][:300]}")
    print(f"Tours : {r1['turns']}")
    
    print("\n--- Version LANGGRAPH ---")
    r2 = run_agent_langgraph(question, verbose=False)
    print(f"Réponse : {r2['answer'][:300]}")
    print(f"Tours : {r2['turns']}")
   

    png = graph.get_graph().draw_mermaid_png()
    Path("agent_graph.png").write_bytes(png)
    print("\n📊 Graphe sauvegardé : agent_graph.png")

if __name__ == "__main__":
    compare("Quels sont les top 3 produits en 2024 ?")