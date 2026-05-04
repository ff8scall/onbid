import sqlite3
import os

DB_PATH = os.path.join(os.getcwd(), 'data', 'pbid_local.db')
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("[*] Starting DB Migration to fix duplication issue...")

# 1. 새 테이블 생성 (UNIQUE 제약 조건 변경: cltr_mng_no 단일키)
cursor.execute('''
    CREATE TABLE onbid_items_new (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pbanc_mng_no TEXT,
        cltr_mng_no TEXT,
        onbid_cltr_nm TEXT,
        cltr_adr TEXT,
        min_bid_prc INTEGER,
        main_category TEXT,
        sub_category TEXT,
        raw_data TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
        ai_score INTEGER, 
        ai_estimated_specs TEXT, 
        ai_reason TEXT, 
        ai_recommendation TEXT, 
        ai_catchphrase TEXT, 
        is_ai_processed INTEGER DEFAULT 0, 
        ai_risk_factor TEXT, 
        ai_resale_value INTEGER, 
        ai_is_pickup_friendly INTEGER DEFAULT 0, 
        thumb_url TEXT, 
        ai_expected_profit INTEGER DEFAULT 0, 
        ai_margin_percent REAL DEFAULT 0.0, 
        ai_pickup_method TEXT, 
        ai_difficulty TEXT, 
        ai_curator_comment TEXT, 
        is_target_item INTEGER DEFAULT 0, 
        is_substandard INTEGER DEFAULT 0, 
        is_maverick_selected INTEGER DEFAULT 0, 
        ai_deep_dive_report TEXT, 
        bid_end_date TEXT, 
        is_expired INTEGER DEFAULT 0, 
        detail_text TEXT, 
        apsl_evl_amt INTEGER DEFAULT 0,
        UNIQUE(cltr_mng_no)
    )
''')

# 2. 데이터 이전 (cltr_mng_no 기준 최신 데이터만 선택)
# pbanc_mng_no를 숫자로 변환하여 가장 큰(최신) 것을 선택
cursor.execute('''
    INSERT INTO onbid_items_new (
        pbanc_mng_no, cltr_mng_no, onbid_cltr_nm, cltr_adr, min_bid_prc, 
        main_category, sub_category, raw_data, created_at, ai_score, 
        ai_estimated_specs, ai_reason, ai_recommendation, ai_catchphrase, 
        is_ai_processed, ai_risk_factor, ai_resale_value, ai_is_pickup_friendly, 
        thumb_url, ai_expected_profit, ai_margin_percent, ai_pickup_method, 
        ai_difficulty, ai_curator_comment, is_target_item, is_substandard, 
        is_maverick_selected, ai_deep_dive_report, bid_end_date, is_expired, 
        detail_text, apsl_evl_amt
    )
    SELECT 
        pbanc_mng_no, cltr_mng_no, onbid_cltr_nm, cltr_adr, min_bid_prc, 
        main_category, sub_category, raw_data, created_at, ai_score, 
        ai_estimated_specs, ai_reason, ai_recommendation, ai_catchphrase, 
        is_ai_processed, ai_risk_factor, ai_resale_value, ai_is_pickup_friendly, 
        thumb_url, ai_expected_profit, ai_margin_percent, ai_pickup_method, 
        ai_difficulty, ai_curator_comment, is_target_item, is_substandard, 
        is_maverick_selected, ai_deep_dive_report, bid_end_date, is_expired, 
        detail_text, apsl_evl_amt
    FROM onbid_items
    GROUP BY cltr_mng_no
    HAVING MAX(CAST(pbanc_mng_no AS INTEGER))
''')

# 3. 테이블 교체
cursor.execute("DROP TABLE onbid_items")
cursor.execute("ALTER TABLE onbid_items_new RENAME TO onbid_items")

conn.commit()
print("[+] Migration completed. Duplicates removed based on cltr_mng_no.")

# 검증: 다시 중복 체크
cursor.execute('SELECT onbid_cltr_nm, COUNT(*) FROM onbid_items GROUP BY cltr_mng_no HAVING COUNT(*) > 1')
dups = cursor.fetchall()
if not dups:
    print("[V] Verification passed: No more duplicates in DB.")
else:
    print(f"[!] Warning: Still found {len(dups)} duplicates.")

conn.close()
