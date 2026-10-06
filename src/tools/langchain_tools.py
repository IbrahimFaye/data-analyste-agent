"""
Wrappers LangChain des tools existants.
"""

from langchain_core.tools import tool

from src.tools.sql_tools import (
    run_sql as _run_sql,
    list_tables as _list_tables,
    describe_table as _describe_table,
)
from src.tools.plot_tools import plot_chart as _plot_chart
from src.tools.analysis_tools import analyze_series as _analyze_series


@tool
def list_tables() -> str:
    """Liste toutes les tables disponibles dans la base de données.

    À appeler en premier si tu ne connais pas le schéma.
    """
    return _list_tables()


@tool
def describe_table(table_name: str) -> str:
    """Retourne les colonnes et types d'une table.

    À utiliser avant d'écrire du SQL si tu n'es pas sûr du schéma.

    Args:
        table_name: Nom exact de la table (ex: 'sales', 'products').
    """
    return _describe_table(table_name)


@tool
def run_sql(query: str) -> str:
    """Exécute une requête SQL SELECT en lecture seule sur DuckDB.

    Utilise le dialecte DuckDB (compatible PostgreSQL).
    Ne pas inclure de point-virgule final.

    Args:
        query: La requête SQL SELECT à exécuter.
    """
    return _run_sql(query)


@tool
def plot_chart(kind: str, x: str, y: str, title: str = "") -> str:
    """Génère un graphique à partir du résultat du DERNIER run_sql.

    À utiliser après avoir obtenu des données numériques via run_sql.

    Args:
        kind: Type de graphique : 'bar' (classements), 'line' (séries temporelles),
              'pie' (parts), 'scatter' (corrélation).
        x: Nom de la colonne pour l'axe X (ou les labels pour un pie).
        y: Nom de la colonne pour l'axe Y (ou les valeurs pour un pie).
        title: Titre du graphique (optionnel mais recommandé).
    """
    return _plot_chart(kind=kind, x=x, y=y, title=title)


@tool
def analyze_series(value_column: str, label_column: str,
                   anomaly_threshold: float = 2.0) -> str:
    """Analyse statistique d'une colonne numérique issue du DERNIER run_sql.

    Calcule moyenne, médiane, écart-type, min, max, variations vs moyenne,
    détecte les anomalies (points au-delà de N écarts-types) et la tendance.

    À utiliser SYSTÉMATIQUEMENT après un run_sql quand la question porte sur
    une évolution, une comparaison ou une détection d'anomalie.

    Args:
        value_column: Nom de la colonne numérique à analyser (ex: 'revenue').
        label_column: Nom de la colonne de labels (ex: 'month', 'name').
        anomaly_threshold: Seuil d'anomalie en écarts-types (défaut 2.0).
    """
    return _analyze_series(
        value_column=value_column,
        label_column=label_column,
        anomaly_threshold=anomaly_threshold,
    )


LANGCHAIN_TOOLS = [
    list_tables,
    describe_table,
    run_sql,
    plot_chart,
    analyze_series,
]