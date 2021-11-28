import sqlite3

conn = sqlite3.connect('database.db')
conn.row_factory = sqlite3.Row

conn.execute('UPDATE items SET lowprice = latestprice \
    WHERE lowprice IS NULL')

conn.commit()
conn.close()
