import sqlite3
import os
import json

DB_PATH = os.path.join('data', 'pbid_local.db')

def peek_data():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 1. 카테고리별 매칭 확인
    print("--- 카테고리별 수집 현황 ---")
    cursor.execute("SELECT sub_category, COUNT(*) as cnt FROM onbid_items GROUP BY sub_category")
    for row in cursor.fetchall():
        print(f"[{row['sub_category']}]: {row['cnt']}건")
    
    # 2. '환금성자산' 중 유망해 보이는 데이터 추출
    print("\n--- 분석 유망 매물 (환금성자산) ---")
    cursor.execute("""
        SELECT onbid_cltr_nm, min_bid_prc, cltr_adr, sub_category, raw_data 
        FROM onbid_items 
        WHERE main_category = '환금성자산'
        ORDER BY min_bid_prc DESC
        LIMIT 30
    """)
    
    for i, row in enumerate(cursor.fetchall()):
        print(f"{i+1}. [{row['sub_category']}] {row['onbid_cltr_nm']}")
        print(f"   입찰가: {Number(row['min_bid_prc']):,}원 | 위치: {row['cltr_adr']}")
        print("-" * 50)
    
    conn.close()

def Number(s):
    try:
        return int(s.replace(',', ''))
    except:
        return 0

if __name__ == "__main__":
    peek_data()
