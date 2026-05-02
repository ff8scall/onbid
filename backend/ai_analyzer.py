import os
import json
import sqlite3
import time
import re
from collector import get_item_detail_text

# google-generativeai 라이브러리 체크
try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

# 설정 로드
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'pbid_local.db')

# Gemini 초기화
model = None
if HAS_GENAI and GEMINI_API_KEY and GEMINI_API_KEY != "your_api_key_here":
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
    except:
        model = None
else:
    model = None

def pre_filter(item):
    name = item['onbid_cltr_nm']
    black_list = ['폐기물', '매각불가', '변압기', 'PCBs', '폐유']
    for kw in black_list:
        if kw in name: return False, f"필터링 ({kw})"
    return True, "통과"

def local_heuristic_analysis(item, detail_text):
    name = item['onbid_cltr_nm']
    raw_data = json.loads(item['raw_data'])
    org = raw_data.get('orgNm', '알 수 없는 기관')
    
    score = 80 # 기본 점수
    if any(kw in org for kw in ['연구', '교육', '법원', '검찰']): score += 10
    if any(kw in name.upper() for kw in ['APPLE', '애플', 'SAMSUNG', '삼성', 'LG', 'DELL']): score += 5
    
    # 수량 감점
    try:
        qnty_str = str(raw_data.get('qntyCont', '1'))
        qnty_match = re.search(r'\d+', qnty_str)
        qnty = int(qnty_match.group()) if qnty_match else 1
        if qnty > 1: score -= min(30, qnty * 0.5)
    except: pass

    # 가격 파싱
    try:
        price = int(item['min_bid_prc'])
    except:
        price = 0

    final_score = max(5, min(99, score))
    
    return {
        "score": final_score,
        "final_spec": name[:100],
        "reason": f"{org} 배출 매물. 기본 가성비 분석 완료.",
        "recommendation": "Strong Buy" if final_score >= 80 else "Watch",
        "catchphrase": f"실제 온비드 매물입니다! ({org})",
        "risk_factor": "상세 설명 및 현장 실물 확인을 권장합니다.",
        "estimated_resale_value": int(price * 1.1),
        "is_pickup_friendly": 1 if '서울' in item['cltr_adr'] else 0
    }

def analyze_items():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM onbid_items WHERE is_ai_processed = 0")
    rows = cursor.fetchall()
    
    if not rows:
        print("[*] 분석할 새로운 매물이 없습니다.")
        return

    print(f"[*] {len(rows)}건 실시간 매물 분석 중...")
    for row in rows:
        passed, reason = pre_filter(row)
        if not passed:
            cursor.execute("UPDATE onbid_items SET is_ai_processed = 1, ai_recommendation = 'Pass' WHERE id = ?", (row['id'],))
            conn.commit()
            continue
            
        analysis = local_heuristic_analysis(row, "")
        
        cursor.execute("""
            UPDATE onbid_items SET
                ai_score = ?, ai_estimated_specs = ?, ai_reason = ?,
                ai_recommendation = ?, ai_catchphrase = ?, ai_risk_factor = ?,
                ai_resale_value = ?, ai_is_pickup_friendly = ?, is_ai_processed = 1
            WHERE id = ?
        """, (
            analysis['score'], analysis['final_spec'], analysis['reason'],
            analysis['recommendation'], analysis['catchphrase'], analysis['risk_factor'],
            analysis['estimated_resale_value'], analysis['is_pickup_friendly'], row['id']
        ))
        conn.commit()
    conn.close()
    print("[*] 분석 완료!")

if __name__ == "__main__":
    analyze_items()
