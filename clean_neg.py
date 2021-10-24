import sqlite3

conn = sqlite3.connect('database.db')
conn.row_factory = sqlite3.Row

table = conn.execute('SELECT * FROM items WHERE lowprice < 0').fetchall()