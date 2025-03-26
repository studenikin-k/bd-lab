import sqlite3

conn = sqlite3.connect("movies.db")
cursor = conn.cursor()

cursor.execute('SELECT id FROM movies')
rows = cursor.fetchall()

for row in rows:
    movie_id = int(row[0])
    if movie_id > 2483:
        cursor.execute('DELETE FROM movies WHERE id = ?', (movie_id,))

conn.commit()
conn.close() 