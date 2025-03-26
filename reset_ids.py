import sqlite3

conn = sqlite3.connect("movies.db")
cursor = conn.cursor()

# Получаем имена столбцов таблицы movies
cursor.execute("PRAGMA table_info(movies)")
columns = [column[1] for column in cursor.fetchall()]

# Создаем временную таблицу со структурой оригинальной таблицы
cursor.execute("CREATE TABLE movies_temp AS SELECT * FROM movies LIMIT 0")

# Копируем данные во временную таблицу с новыми id
cursor.execute(f"""
INSERT INTO movies_temp 
SELECT NULL, {', '.join(col for col in columns if col != 'id')}
FROM movies 
LIMIT 2483
""")

# Удаляем оригинальную таблицу
cursor.execute("DROP TABLE movies")

# Переименовываем временную таблицу
cursor.execute("ALTER TABLE movies_temp RENAME TO movies")

# Обновляем id от 1 до 2483
rows = cursor.execute("SELECT rowid FROM movies ORDER BY rowid LIMIT 2483").fetchall()
valid_rowids = [r[0] for r in rows]
for new_id, r in enumerate(valid_rowids, start=1):
    cursor.execute("UPDATE movies SET id = ? WHERE rowid = ?", (new_id, r))
if valid_rowids:
    rowid_list_str = ",".join(str(r) for r in valid_rowids)
    cursor.execute(f"DELETE FROM movies WHERE rowid NOT IN ({rowid_list_str})")
else:
    cursor.execute("DELETE FROM movies")

conn.commit()
conn.close() 