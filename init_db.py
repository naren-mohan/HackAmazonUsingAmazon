import sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO items (title, url, notes) VALUES (?, ?, ?)",
            ('First Post', 'www.google.com', 'notes for the first post')
            )

cur.execute("INSERT INTO items (title, url, notes) VALUES (?, ?, ?)",
            ('Second Post', 'www.amazon.com', 'notes for the second post')
            )

connection.commit()
connection.close()
