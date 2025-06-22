import sqlite3
import csv
import os

def insert_csv(csv_path, table_name, db_path):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        table_columns = get_table_columns(cursor, table_name)

        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            clear_table(table_name, db_path)

            reader = csv.DictReader(csvfile)
            filtered_headers = [h for h in reader.fieldnames if h in table_columns]

            placeholders = ','.join(['?'] * len(filtered_headers))
            insert_sql = f'INSERT INTO {table_name} ({",".join(filtered_headers)}) VALUES ({placeholders})'

            for row in reader:
                try:
                    values = [row[h] for h in filtered_headers]
                    cursor.execute(insert_sql, values)
                except sqlite3.IntegrityError as e:
                    print(f"⚠️ IntegrityError on row {row}: {e}")
                except Exception as e:
                    print(f"⚠️ Error on row {row}: {e}")

        conn.commit()

def get_table_columns(cursor, table_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [row[1] for row in cursor.fetchall()]  # column names

def clear_table(table_name, db_path):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {table_name}")
        conn.commit()
            
csv_folder = './temp/rebrickable'
db_path = "./lego_parts.db"

# Maps CSV file names to their matching SQLite table names
csv_table_map = {
    'themes.csv': 'themes',
    'colors.csv': 'colors',
    'part_categories.csv': 'part_categories',
    'parts.csv': 'parts',
    'part_relationships.csv': 'part_relationships',
    'elements.csv': 'elements',
    'sets.csv': 'sets',
    'minifigs.csv': 'minifigs',
}

# Connect to SQLite
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Create tables
cur.execute("""CREATE TABLE IF NOT EXISTS themes (
    id INTEGER PRIMARY KEY,                                                              
    name TEXT NOT NULL,
    parent_id INTEGER,
    FOREIGN KEY (parent_id) REFERENCES themes(id))""")

cur.execute("""CREATE TABLE IF NOT EXISTS colors (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    rgb TEXT NOT NULL,
    is_trans BOOLEAN NOT NULL,
    num_parts INTEGER NOT NULL,
    num_sets INTEGER NOT NULL,
    y1 INTEGER NOT NULL,
    y2 INTEGER NOT NULL)""")

cur.execute("""CREATE TABLE IF NOT EXISTS part_categories (
   id INTEGER PRIMARY KEY,
   name TEXT NOT NULL)""")

cur.execute("""CREATE TABLE IF NOT EXISTS parts (
    part_num TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    part_cat_id INTEGER,
    part_material TEXT,
    FOREIGN KEY (part_cat_id) REFERENCES part_categories(id))""")

cur.execute("""CREATE TABLE IF NOT EXISTS part_relationships (
    rel_type TEXT NOT NULL,
    child_part_num TEXT NOT NULL,
    parent_part_num TEXT NOT NULL,
    FOREIGN KEY (child_part_num) REFERENCES parts(part_num),
    FOREIGN KEY (parent_part_num) REFERENCES parts(part_num))""")

cur.execute("""CREATE TABLE IF NOT EXISTS elements (
    element_id TEXT PRIMARY KEY,
    part_num TEXT NOT NULL,
    color_id INTEGER NOT NULL,
    design_id INTEGER,
    FOREIGN KEY (part_num) REFERENCES parts(part_num),
    FOREIGN KEY (color_id) REFERENCES colors(id))""")

cur.execute("""CREATE TABLE IF NOT EXISTS sets (
    set_num TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    year INTEGER NOT NULL,
    theme_id INTEGER NOT NULL,
    num_parts INTEGER NOT NULL,
    FOREIGN KEY (theme_id) REFERENCES themes(id))""")

cur.execute("""CREATE TABLE IF NOT EXISTS minifigs (
    fig_num TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    num_parts INTEGER NOT NULL)""")

# Insert data
for csv_file, table_name in csv_table_map.items():
    print(f"📥 Importing {csv_file} → {table_name}")
    insert_csv(os.path.join(csv_folder, csv_file), table_name, db_path)
    
# Done
conn.commit()
conn.close()

print("✅ Database created: lego_parts.db")

