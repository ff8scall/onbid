import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'pbid_local.db')

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS onbid_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pbanc_mng_no TEXT,
            cltr_mng_no TEXT,
            onbid_cltr_nm TEXT,
            cltr_adr TEXT,
            min_bid_prc INTEGER,
            main_category TEXT,
            sub_category TEXT,
            thumb_url TEXT,
            raw_data TEXT,
            ai_score INTEGER,
            ai_estimated_specs TEXT,
            ai_reason TEXT,
            ai_recommendation TEXT,
            ai_catchphrase TEXT,
            ai_risk_factor TEXT,
            ai_resale_value INTEGER,
            ai_is_pickup_friendly INTEGER DEFAULT 0,
            is_ai_processed INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(pbanc_mng_no, cltr_mng_no)
        )
    ''')
    
    # 2. Migration (새로 추가된 컬럼들)
    columns_to_add = [
        ("ai_score", "INTEGER"),
        ("ai_estimated_specs", "TEXT"),
        ("ai_reason", "TEXT"),
        ("ai_recommendation", "TEXT"),
        ("ai_catchphrase", "TEXT"),
        ("ai_risk_factor", "TEXT"),
        ("ai_resale_value", "INTEGER"),
        ("ai_is_pickup_friendly", "INTEGER DEFAULT 0"),
        ("is_ai_processed", "INTEGER DEFAULT 0"),
        ("thumb_url", "TEXT")
    ]
    
    cursor.execute("PRAGMA table_info(onbid_items)")
    existing_columns = [col[1] for col in cursor.fetchall()]
    
    for col_name, col_type in columns_to_add:
        if col_name not in existing_columns:
            print(f"[*] Adding column {col_name} to onbid_items")
            cursor.execute(f"ALTER TABLE onbid_items ADD COLUMN {col_name} {col_type}")
    
    conn.commit()
    conn.close()
    print(f"Database initialized and migrated at {DB_PATH}")

if __name__ == "__main__":
    init_db()
