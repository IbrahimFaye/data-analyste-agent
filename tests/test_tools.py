import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.tools.sql_tools import run_sql, list_tables, describe_table


def test_list_tables():
    print("=== TEST list_tables ===")
    print(list_tables())
    print()


def test_describe():
    print("=== TEST describe_table('sales') ===")
    print(describe_table("sales"))
    print()


def test_sql_simple():
    print("=== TEST run_sql : count ===")
    print(run_sql("SELECT COUNT(*) AS nb FROM sales"))
    print()


def test_sql_groupby():
    print("=== TEST run_sql : top 3 produits ===")
    print(run_sql("""
        SELECT p.name, ROUND(SUM(s.revenue), 2) AS ca
        FROM sales s JOIN products p USING (product_id)
        GROUP BY p.name ORDER BY ca DESC LIMIT 3
    """))
    print()


def test_sql_error():
    print("=== TEST run_sql : requête invalide (doit renvoyer l'erreur proprement) ===")
    print(run_sql("SELECT * FROM table_qui_existe_pas"))
    print()


def test_sql_blocked():
    print("=== TEST run_sql : tentative DROP (doit être refusé) ===")
    print(run_sql("DROP TABLE sales"))
    print()


if __name__ == "__main__":
    test_list_tables()
    test_describe()
    test_sql_simple()
    test_sql_groupby()
    test_sql_error()
    test_sql_blocked()