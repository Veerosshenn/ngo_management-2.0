import sqlite3
conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()
print('columns:')
for row in cur.execute("PRAGMA table_info('ngo_activity')"):
    print(row)
conn.close()