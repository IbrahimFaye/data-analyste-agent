import duckdb
con = duckdb.connect("data/sales.duckdb")

print("--- Nb ventes ---")
print(con.execute("SELECT COUNT(*) FROM sales").fetchall())

print("--- CA par mois ---")
print(con.execute("""
    SELECT strftime(date, '%Y-%m') AS mois, ROUND(SUM(revenue), 2) AS ca
    FROM sales GROUP BY mois ORDER BY mois
""").fetchdf())

print("--- Top 5 produits ---")
print(con.execute("""
    SELECT p.name, ROUND(SUM(s.revenue), 2) AS ca
    FROM sales s JOIN products p USING (product_id)
    GROUP BY p.name ORDER BY ca DESC LIMIT 5
""").fetchdf())