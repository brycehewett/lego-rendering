import sqlite3

def get_parts(part_count = 10, db_path = "lego_parts.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = "SELECT part_name FROM parts_popular LIMIT ?"
    cursor.execute(query, (part_count,))
    result = cursor.fetchall()
    conn.close()
    return [row[0] for row in result]

def get_random_color_for_part(part_num, db_path = "lego_parts.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = """
            SELECT c.rgb, c.is_trans
            FROM elements e
                     JOIN colors c ON e.color_id = c.id
            WHERE e.part_num = ?
            GROUP BY c.rgb
            ORDER BY RANDOM()
                LIMIT 1; \
            """
    cursor.execute(query, (part_num,))
    result = cursor.fetchone()
    conn.close()
    return result

def get_canonical_part_num(part_num, db_path = "lego_parts.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = """
            WITH RECURSIVE variant_chain(child, parent) AS (
                SELECT child_part_num, parent_part_num
                FROM part_relationships
                WHERE child_part_num = ? AND rel_type IN ('P', 'M', 'T', 'A')

                UNION

                SELECT r.child_part_num, r.parent_part_num
                FROM part_relationships r
                         JOIN variant_chain vc ON vc.parent = r.child_part_num
                WHERE r.rel_type IN ('P', 'M', 'T', 'A')
            )
            SELECT COALESCE(MAX(parent), ?) AS canonical_part_num
            FROM variant_chain; \
            """
    cursor.execute(query, (part_num, part_num))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else part_num