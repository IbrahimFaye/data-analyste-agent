
import duckdb
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42) 

DB_PATH = Path("data/sales.duckdb")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

START_DATE = date(2023, 1, 1)
END_DATE = date(2026, 10, 6)

CATEGORIES = ["Electronics", "Clothing", "Home", "Sports"]

PRODUCTS = [
    ("Laptop Pro",       "Electronics", 1200.0, 1.25),
    ("Wireless Mouse",   "Electronics",   35.0, 1.10),
    ("4K Monitor",       "Electronics",  450.0, 1.35),  
    ("USB-C Hub",        "Electronics",   60.0, 0.90),
    ("Smartphone X",     "Electronics",  900.0, 1.05),
    ("T-Shirt Basic",    "Clothing",      25.0, 0.85),  
    ("Jeans Slim",       "Clothing",      80.0, 1.00),
    ("Hoodie Premium",   "Clothing",      95.0, 1.15),
    ("Sneakers Run",     "Clothing",     140.0, 1.20),
    ("Jacket Winter",    "Clothing",     180.0, 0.95),
    ("Coffee Maker",     "Home",         150.0, 1.08),
    ("Blender Pro",      "Home",         120.0, 0.92),
    ("Air Purifier",     "Home",         250.0, 1.40),  
    ("Desk Lamp",        "Home",          45.0, 1.00),
    ("Vacuum Cleaner",   "Home",         300.0, 1.12),
    ("Yoga Mat",         "Sports",        40.0, 1.18),
    ("Dumbbell Set",     "Sports",       120.0, 1.05),
    ("Bike Helmet",      "Sports",        85.0, 0.88),
    ("Tennis Racket",    "Sports",       160.0, 1.10),
    ("Water Bottle",     "Sports",        25.0, 1.30),
]

COUNTRIES = ["France", "Germany", "Spain", "Italy", "UK"]
SEGMENTS = ["Retail", "Wholesale", "VIP"]

FIRST_NAMES = ["Alice", "Bob", "Claire", "David", "Emma", "Frank",
               "Grace", "Hugo", "Iris", "Jack", "Kate", "Leo",
               "Mia", "Noah", "Olivia", "Paul", "Quinn", "Rose",
               "Sam", "Tina"]
LAST_NAMES = ["Martin", "Bernard", "Dubois", "Thomas", "Robert",
              "Petit", "Durand", "Leroy", "Moreau", "Simon",
              "Laurent", "Lefebvre", "Michel", "Garcia", "David"]

def seasonal_factor(d: date) -> float:
    month = d.month
    if month in (11, 12):
        return 1.6      
    if month == 6:
        return 1.2     
    if month in (1, 2):
        return 0.75    
    return 1.0


def growth_factor(d: date, trend: float) -> float:
    total_days = (END_DATE - START_DATE).days
    elapsed = (d - START_DATE).days
    progress = elapsed / total_days
    return 1.0 + (trend - 1.0) * progress


con = duckdb.connect(str(DB_PATH))

con.execute("DROP TABLE IF EXISTS sales")
con.execute("DROP TABLE IF EXISTS products")
con.execute("DROP TABLE IF EXISTS customers")

con.execute("""
CREATE TABLE products (
    product_id   INTEGER PRIMARY KEY,
    name         VARCHAR NOT NULL,
    category     VARCHAR NOT NULL,
    unit_price   DOUBLE  NOT NULL
)
""")

con.execute("""
CREATE TABLE customers (
    customer_id  INTEGER PRIMARY KEY,
    name         VARCHAR NOT NULL,
    country      VARCHAR NOT NULL,
    segment      VARCHAR NOT NULL
)
""")

con.execute("""
CREATE TABLE sales (
    sale_id      INTEGER PRIMARY KEY,
    product_id   INTEGER NOT NULL,
    customer_id  INTEGER NOT NULL,
    date         DATE    NOT NULL,
    quantity     INTEGER NOT NULL,
    revenue      DOUBLE  NOT NULL
)
""")

product_rows = []
for pid, (name, cat, price, _trend) in enumerate(PRODUCTS, start=1):
    product_rows.append((pid, name, cat, price))

con.executemany(
    "INSERT INTO products VALUES (?, ?, ?, ?)",
    product_rows,
)

customer_rows = []
for cid in range(1, 201):
    name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
    country = random.choice(COUNTRIES)
    segment = random.choices(SEGMENTS, weights=[0.7, 0.25, 0.05])[0]
    customer_rows.append((cid, name, country, segment))

con.executemany(
    "INSERT INTO customers VALUES (?, ?, ?, ?)",
    customer_rows,
)

customer_weights = []
for cid in range(1, 201):
    seg = customer_rows[cid - 1][3]
    if seg == "VIP":
        customer_weights.append(5.0)
    elif seg == "Wholesale":
        customer_weights.append(2.5)
    else:
        customer_weights.append(1.0)

anomaly_dates = {
    date(2023, 7, 15),
    date(2024, 3, 22),
    date(2025, 8, 10),   
    date(2026, 2, 14), 
}

BASE_SALES_PER_DAY = 7  

sales_rows = []
sale_id = 1

current = START_DATE
while current <= END_DATE:
    n_sales = BASE_SALES_PER_DAY
    n_sales = int(n_sales * seasonal_factor(current))
    n_sales = random.randint(max(1, n_sales - 3), n_sales + 3)

    if current in anomaly_dates:
        n_sales *= 5

    for _ in range(n_sales):
        weights = [
            growth_factor(current, trend)
            for (_n, _c, _p, trend) in PRODUCTS
        ]
        pid = random.choices(range(1, len(PRODUCTS) + 1), weights=weights)[0]
        product = PRODUCTS[pid - 1]
        unit_price = product[2]

        cid = random.choices(range(1, 201), weights=customer_weights)[0]

        quantity = random.choices([1, 2, 3, 4, 5], weights=[5, 3, 1, 1, 0.5])[0]

        revenue = quantity * unit_price * random.uniform(0.9, 1.1)

        sales_rows.append((
            sale_id,
            pid,
            cid,
            current,
            quantity,
            round(revenue, 2),
        ))
        sale_id += 1

    current += timedelta(days=1)

con.executemany(
    "INSERT INTO sales VALUES (?, ?, ?, ?, ?, ?)",
    sales_rows,
)

con.close()

print(f"✅ Base créée : {DB_PATH}")
print(f"   - {len(product_rows)} produits")
print(f"   - {len(customer_rows)} clients")
print(f"   - {len(sales_rows)} ventes")