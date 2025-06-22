import sqlite3
import pandas as pd

# File paths
themes_csv = "./temp/themes.csv"
colors_csv = "./temp/colors.csv"
part_categories_csv = "./temp/part_categories.csv"
parts_csv = "./temp/parts.csv"
part_relationships_csv = "./temp/part_relationships.csv"
elements_csv = "./temp/elements.csv"
sets_csv = "./temp/sets.csv"
minifigs_csv = "./temp/minifigs.csv"

db_path = "./lego_parts.db"

# Load CSVs
themes = pd.read_csv(themes_csv)
colors = pd.read_csv(colors_csv)
part_categories = pd.read_csv(part_categories_csv)
parts = pd.read_csv(parts_csv)
part_relationships = pd.read_csv(part_relationships_csv)
elements = pd.read_csv(elements_csv)
sets = pd.read_csv(sets_csv)
minifigs = pd.read_csv(minifigs_csv)

# Connect to SQLite
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Create tables
cur.execute("""
            CREATE TABLE IF NOT EXISTS part_categories (
                                                           id INTEGER PRIMARY KEY,
                                                           name TEXT NOT NULL
            )
            """)

cur.execute("""
            CREATE TABLE IF NOT EXISTS parts (
                                                 part_num TEXT PRIMARY KEY,
                                                 name TEXT NOT NULL,
                                                 part_cat_id INTEGER,
                                                 part_material TEXT,
                                                 part_type TEXT,
                                                 FOREIGN KEY (part_cat_id) REFERENCES part_categories(id)
                )
            """)

# Insert data
categories.to_sql("part_categories", conn, if_exists="replace", index=False)
parts.to_sql("parts", conn, if_exists="replace", index=False)

# Done
conn.commit()
conn.close()

print("✅ Database created: lego_parts.db")
