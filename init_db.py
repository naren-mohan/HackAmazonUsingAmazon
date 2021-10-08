import sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO posts (title, url, content) VALUES (?, ?, ?)",
            ('First Post', 'www.google.com', 'Content for the first post')
            )

cur.execute("INSERT INTO posts (title, url, content) VALUES (?, ?, ?)",
            ('Second Post', 'www.amazon.com', 'Content for the second post')
            )

connection.commit()
connection.close()
