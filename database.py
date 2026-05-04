import sqlite3
import os

DB_PATH = 'database.db'

def get_db_connection():
    """建立並回傳與 SQLite 的連線，設定 row_factory 使回傳資料可以像字典一樣操作。"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """初始化資料庫。如果 database.db 不存在，則讀取 schema.sql 並執行。"""
    if not os.path.exists(DB_PATH):
        print("Initializing database...")
        conn = get_db_connection()
        with open('schema.sql', 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()
        print("Database initialized successfully.")
    else:
        print("Database already exists. Skipping initialization.")

if __name__ == '__main__':
    # 允許直接執行此腳本來手動初始化資料庫
    init_db()
