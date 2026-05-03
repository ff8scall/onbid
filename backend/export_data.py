import sqlite3
import json
import os

# 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'pbid_local.db')
OUTPUT_DIR = os.path.join(BASE_DIR, 'frontend', 'src', 'data')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'items.json')

def export_to_json():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. 정예 매물 (Target)
    cursor.execute('SELECT * FROM onbid_items WHERE is_target_item = 1 AND is_substandard = 0 AND is_expired = 0 ORDER BY ai_score DESC')
    target_items = [dict(row) for row in cursor.fetchall()]
    
    # 2. 후보 매물 (Candidate)
    cursor.execute('SELECT * FROM onbid_items WHERE is_maverick_selected = 1 AND is_target_item = 0 AND is_substandard = 0 AND is_expired = 0 ORDER BY ai_score DESC')
    candidate_items = [dict(row) for row in cursor.fetchall()]
    
    # 3. 기준 미달 (Substandard)
    cursor.execute('SELECT * FROM onbid_items WHERE is_substandard = 1 AND is_expired = 0 ORDER BY ai_score DESC')
    substandard_items = [dict(row) for row in cursor.fetchall()]
    
    # 4. 지난 내역 (Expired)
    cursor.execute('SELECT * FROM onbid_items WHERE is_expired = 1 ORDER BY bid_end_date DESC')
    expired_items = [dict(row) for row in cursor.fetchall()]
    
    # JSON 데이터 파싱
    for items in [target_items, candidate_items, substandard_items, expired_items]:
        for item in items:
            if item.get('raw_data'):
                item['raw_data'] = json.loads(item['raw_data'])
    
    # 카테고리 추출 (정예 매물 기준)
    cursor.execute("SELECT DISTINCT sub_category FROM onbid_items WHERE main_category = '환금성자산' AND is_target_item = 1 AND is_substandard = 0 AND is_expired = 0")
    categories = [row[0] for row in cursor.fetchall()]
    
    data = {
        "target": target_items,
        "candidate": candidate_items,
        "substandard": substandard_items,
        "expired": expired_items,
        "categories": categories,
        "last_updated": sqlite3.connect(DB_PATH).execute("SELECT datetime('now', 'localtime')").fetchone()[0]
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Data export completed: {OUTPUT_FILE}")
    print(f"Stats: Target({len(target_items)}), Candidate({len(candidate_items)}), Substandard({len(substandard_items)})")

    conn.close()

if __name__ == "__main__":
    export_to_json()
