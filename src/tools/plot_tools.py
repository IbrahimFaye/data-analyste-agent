
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import uuid
from pathlib import Path

from src.tools.sql_tools import get_last_result

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)
_GENERATED_CHARTS: list[str] = []

def get_generated_charts() -> list[str]:
    """Retourne la liste des graphiques générés depuis le dernier reset."""
    return list(_GENERATED_CHARTS)

def reset_generated_charts():
    """Vide le registre (à appeler au début de chaque run_agent)."""
    _GENERATED_CHARTS.clear()


def plot_chart(kind: str, x: str, y: str, title: str = "") -> str:
    """
    Génère un graphique à partir du DERNIER résultat de run_sql.
    
    Args:
        kind:  'bar', 'line', 'pie', 'scatter'
        x:     nom de la colonne pour l'axe X (ou labels pour pie)
        y:     nom de la colonne pour l'axe Y (ou valeurs pour pie)
        title: titre du graphique (optionnel)
    
    Returns:
        Un message texte décrivant le graphique (chemin + résumé).
    """
    df = get_last_result()
    if df is None:
        return "❌ Aucune donnée disponible. Appelle run_sql d'abord."
    
    if x not in df.columns:
        return f"❌ Colonne '{x}' introuvable. Colonnes dispo : {list(df.columns)}"
    if y not in df.columns:
        return f"❌ Colonne '{y}' introuvable. Colonnes dispo : {list(df.columns)}"
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    try:
        if kind == "bar":
            ax.bar(df[x].astype(str), df[y])
            ax.tick_params(axis="x", rotation=45)
        elif kind == "line":
            ax.plot(df[x], df[y], marker="o")
            ax.tick_params(axis="x", rotation=45)
        elif kind == "pie":
            ax.pie(df[y], labels=df[x].astype(str), autopct="%1.1f%%")
        elif kind == "scatter":
            ax.scatter(df[x], df[y])
        else:
            plt.close(fig)
            return f"❌ Type '{kind}' non supporté. Utilise : bar, line, pie, scatter."
    except Exception as e:
        plt.close(fig)
        return f"❌ Erreur lors du tracé : {e}"
    
    if title:
        ax.set_title(title)
    ax.set_xlabel(str(x))
    ax.set_ylabel(str(y))
    plt.tight_layout()
    
    filename = f"chart_{uuid.uuid4().hex[:8]}.png"
    filepath = OUTPUT_DIR / filename
    fig.savefig(filepath, dpi=100)
    plt.close(fig)
   
    _GENERATED_CHARTS.append(str(filepath))

    return (
        f"✅ Graphique '{kind}' généré : {filepath}\n"
        f"   Axe X : {x} | Axe Y : {y} | {len(df)} points | Titre : {title or '(aucun)'}"
    )


PLOT_TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "plot_chart",
            "description": (
                "Génère un graphique à partir du résultat du DERNIER run_sql. "
                "À utiliser après avoir obtenu des données numériques via run_sql. "
                "Types disponibles : 'bar' (catégories), 'line' (séries temporelles), "
                "'pie' (parts), 'scatter' (corrélation)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "kind": {
                        "type": "string",
                        "enum": ["bar", "line", "pie", "scatter"],
                        "description": "Type de graphique.",
                    },
                    "x": {
                        "type": "string",
                        "description": "Nom de la colonne pour l'axe X (ou les labels pour un pie).",
                    },
                    "y": {
                        "type": "string",
                        "description": "Nom de la colonne pour l'axe Y (ou les valeurs pour un pie).",
                    },
                    "title": {
                        "type": "string",
                        "description": "Titre du graphique (optionnel mais recommandé).",
                    },
                },
                "required": ["kind", "x", "y"],
            },
        },
    },
]