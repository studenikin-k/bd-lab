import sqlite3

conn = sqlite3.connect("movies.db")
cursor = conn.cursor()
cursor.execute('DELETE FROM movies WHERE rowid NOT IN (SELECT MIN(rowid) FROM movies GROUP BY "id")')
cursor.execute('DELETE FROM movies WHERE id > 2483')
conn.commit()
conn.close() 