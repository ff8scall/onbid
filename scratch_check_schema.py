import sqlite3
import os

DB_PATH = os.path.join(os.getcwd(), 'data', 'pbid_local.db')
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='onbid_items';")
print(cursor.fetchone()[0])
conn.close()
