
import duckdb
from pathlib import Path

DB_PATH = (Path(__file__).parent.parent.parent / "data" / "sales.duckdb").resolve()

def _connect():
    """Ouvre une connexion read-only à DuckDB."""
    return duckdb.connect(str(DB_PATH), read_only=True)

_LAST_RESULT = {"df": None, "sql": None}

def get_last_result():
    """Retourne le DataFrame du dernier run_sql réussi."""
    return _LAST_RESULT["df"]


def run_sql(query: str) -> str:
    """
    Exécute une requête SQL SELECT en lecture seule.
    Retourne un tableau formaté en texte (tronqué à 50 lignes).
    """
    query = query.strip().rstrip(";")
    
    if not query.lower().lstrip().startswith("select"):
        return "❌ Erreur : seules les requêtes SELECT sont autorisées."
    
    try:
        con = _connect()
        df = con.execute(query).fetchdf()
        con.close()
    except Exception as e:
        return f"❌ Erreur SQL : {e}"

    
    _LAST_RESULT["df"] = df
    _LAST_RESULT["sql"] = query

    if df.empty:
        return "Aucun résultat."
    
    truncated = df.head(50)
    header = " | ".join(str(c) for c in truncated.columns)
    sep = "-" * len(header)
    rows = "\n".join(
        " | ".join(str(v) for v in row)
        for row in truncated.itertuples(index=False)
    )
    
    result = f"{header}\n{sep}\n{rows}"
    if len(df) > 50:
        result += f"\n... ({len(df) - 50} lignes supplémentaires)"
    return result


def list_tables() -> str:
    """Liste les tables disponibles dans la base."""
    con = _connect()
    rows = con.execute("SHOW TABLES").fetchall()
    con.close()
    return "\n".join(r[0] for r in rows)


def describe_table(table_name: str) -> str:
    """Retourne le schéma d'une table (colonnes + types)."""
    con = _connect()
    try:
        rows = con.execute(f"DESCRIBE {table_name}").fetchall()
    except Exception as e:
        con.close()
        return f"❌ Table inconnue '{table_name}' : {e}"
    con.close()
    lines = [f"{r[0]} ({r[1]})" for r in rows]
    return "\n".join(lines)



TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "list_tables",
            "description": "Liste toutes les tables disponibles dans la base de données. À appeler en premier si tu ne connais pas le schéma.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "describe_table",
            "description": "Retourne les colonnes et types d'une table. À utiliser avant d'écrire du SQL si tu n'es pas sûr du schéma.",
            "parameters": {
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Nom exact de la table (ex: 'sales', 'products')."
                    }
                },
                "required": ["table_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_sql",
            "description": "Exécute une requête SQL SELECT en lecture seule et retourne les résultats. Utilise le dialecte DuckDB (compatible PostgreSQL).",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "La requête SQL SELECT. Ne pas inclure de point-virgule final."
                    }
                },
                "required": ["query"],
            },
        },
    },
]


def execute_tool(name: str, args: dict) -> str:
    if name == "list_tables":
        return list_tables()
    if name == "describe_table":
        return describe_table(**args)
    if name == "run_sql":
        return run_sql(**args)
    if name == "plot_chart":
        from src.tools.plot_tools import plot_chart
        return plot_chart(**args)
    if name == "analyze_series":
        from src.tools.analysis_tools import analyze_series
        return analyze_series(**args)
    return f"❌ Outil inconnu : {name}"