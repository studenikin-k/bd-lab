import csv
import sqlite3

conn = sqlite3.connect("movies.db")
cursor = conn.cursor()

with open("top_rated_movies.csv", "r", encoding="utf-8") as file:
    reader = csv.reader(file)
    header = next(reader)
    columns_definition = ", ".join([f'"{col}" TEXT' for col in header])
    unique_constraint = ", UNIQUE(" + ", ".join([f'"{col}"' for col in header]) + ")"
    cursor.execute(f'CREATE TABLE IF NOT EXISTS movies ({columns_definition}{unique_constraint})')
    placeholders = ", ".join(["?"] * len(header))
    for row in reader:
        cursor.execute(f'INSERT OR IGNORE INTO movies VALUES ({placeholders})', row)
conn.commit()
conn.close()
