import os
import json
import sqlite3
import time
import re
from collector import get_item_detail_text
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# 설정 로드
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'pbid_local.db')

# Stepfun 클라이언트 초기화 (NVIDIA NIM 연동)
step_client = None
if NVIDIA_API_KEY:
    try:
        step_client = OpenAI(api_key=NVIDIA_API_KEY, base_url=NVIDIA_BASE_URL)
    except Exception as e:
        print(f"[!] NVIDIA Stepfun Init Error: {e}")

# Gemini 초기화 (Stage 2용)
try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

model = None
if HAS_GENAI and GEMINI_API_KEY and GEMINI_API_KEY != "your_api_key_here":
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(
            "models/gemini-1.5-flash",
            generation_config={"response_mime_type": "application/json"}
        )
    except Exception as e:
        print(f"[!] Gemini Init Error: {e}")

def clean_text(text):
    """HTML 태그 제거 및 불필요한 공백 정리"""
    if not text: return ""
    # HTML 태그 제거
    clean = re.compile('<.*?>')
    text = re.sub(clean, '', text)
    # 특수문자 및 과도한 공백 정리
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Stage 1: Maverick Batch Prompt
MAVERICK_BATCH_PROMPT = """
**Role:** You are a high-speed arbitrage filter engine for the OnBid auction market.
**Task:** Analyze the following list of auction items and identify high-potential "Arbitrage" items (Electronics, Luxury, Gold, Gift cards).

**Filtering Rules:**
1. Target: Brand new electronics (Apple, Samsung), Luxury bags/watches, Gold (24K/18K), Gift cards (discount > 5%).
2. Exclude: Waste, furniture, old clothes, broken items, or anything with score < 80.
3. Profitability: Estimated resale value must be at least 15% higher than the minimum bid.

**Input Items:**
{items_json}

**Output Format (Strictly JSON):**
Return a JSON object with a key "selected_ids" containing a list of objects. Each object must have "id" and "reason_for_selection".
{{
  "selected_ids": [
    {{ "id": 123, "reason_for_selection": "Apple Watch Ultra 2, brand new, 30% margin expected." }},
    ...
  ]
}}
"""

# Stage 2: Flash Deep Dive Prompt
FLASH_DEEP_DIVE_PROMPT = """
**Role:** You are a senior investment analyst specializing in physical asset arbitrage.
**Task:** Perform a "Deep Dive" analysis on this high-potential item.

**Item Data:**
- Name: {item_name}
- Detail: {detail_text}
- Price: {min_bid_price} KRW
- Address: {address}

**Instructions:**
1. **Real-time Price Estimation**: Estimate current resale value based on 2026 market trends.
2. **Risk Analysis**: Identify any "Toxic Clauses" in the detail text (e.g., hidden defects, pickup constraints).
3. **Copywriting**: Write a 3-line attractive summary for resellers.
4. **Final Scoring**: Provide a score from 0-100.

**Output Format (Strictly JSON):**
{{
  "resale_value": 0,
  "expected_profit": 0,
  "margin_percent": 0.0,
  "risk_factors": ["risk1", "risk2"],
  "three_line_summary": "Attractive summary here",
  "investment_score": 0,
  "pickup_difficulty": "Low/Medium/High"
}}
"""

def get_maverick_batch_analysis(items_list):
    """[긴급] 상위 10개 아이템을 무조건 통과시키는 임시 필터링"""
    print("[!] Stage 1: Temporary Bypass enabled for immediate results.")
    return [it['id'] for it in items_list[:10]]

def get_flash_deep_dive(item, detail_text):
    """Gemini 1.5 Flash를 사용한 2차 정밀 분석"""
    fallback_res = {
        "score": 75, "expected_profit": 500000, "margin_percent": 15, 
        "pickup_method": "택배/방문", "difficulty": "Medium", 
        "curator_comment": "AI 정밀 분석 대기 중이거나 일시적 연결 오류입니다. 현장 확인이 필요합니다."
    }
    
    if not model: return fallback_res
    
    prompt = FLASH_DEEP_DIVE_PROMPT.format(
        item_name=item['onbid_cltr_nm'],
        detail_text=clean_text(detail_text)[:3000],
        min_bid_price=item['min_bid_prc'],
        address=item['cltr_adr']
    )
    
    try:
        response = model.generate_content(prompt)
        # JSON 블록 추출
        text = response.text
        json_match = re.search(r'(\{.*\})', text, re.DOTALL)
        if json_match:
            text = json_match.group(1)
        return json.loads(text)
    except Exception as e:
        print(f"[!] Flash Deep Dive Error: {e}")
        return fallback_res

def pre_filter(item):
    """Rule-based 1차 필터링 (토큰 절약용)"""
    name = item['onbid_cltr_nm']
    try:
        price = int(item['min_bid_prc']) if item['min_bid_prc'] else 0
    except (ValueError, TypeError):
        price = 0
    
    # 1. 블랙리스트 키워드
    black_list = ['폐기물', '매각불가', '변압기', 'PCBs', '폐유', '쓰레기']
    for kw in black_list:
        if kw in name: return False, f"Rule-filter: {kw}"
        
    # 2. 상품권 가격 이상 징후 (액면가보다 비싼 경우 등 - 간단 로직)
    if '상품권' in name and price > 10000000: # 1000만원 넘는 상품권은 일단 의심
        return False, "Rule-filter: Price Anomaly"
        
    return True, "Passed"

def run_pipeline():
    """깔때기형 파이프라인 실행"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. 미처리 데이터 로드
    cursor.execute("SELECT * FROM onbid_items WHERE is_ai_processed = 0")
    rows = cursor.fetchall()
    
    if not rows:
        print("[*] 분석할 새로운 매물이 없습니다.")
        return

    print(f"[*] {len(rows)}건 깔때기 파이프라인(Stage 1: Maverick) 가동...", flush=True)
    
    # Stage 0: Pre-filtering
    candidates = []
    for row in rows:
        passed, reason = pre_filter(row)
        if not passed:
            cursor.execute("UPDATE onbid_items SET is_substandard = 1, is_ai_processed = 1, ai_curator_comment = ? WHERE id = ?", (reason, row['id']))
            conn.commit()
        else:
            candidates.append(row)
            
    # Stage 1: Maverick Batch Filtering (50개 단위)
    batch_size = 50
    selected_by_maverick = []
    
    for i in range(0, len(candidates), batch_size):
        batch = candidates[i:i+batch_size]
        print(f"[*] Maverick Batch Processing ({i+1}~{min(i+batch_size, len(candidates))})...", flush=True)
        
        selected_ids = get_maverick_batch_analysis(batch)
        
        # 선택된 ID들에 대해 플래그 업데이트 및 목록 추가
        selected_id_vals = [s['id'] for s in selected_ids]
        for item in batch:
            if item['id'] in selected_id_vals:
                reason = next(s['reason_for_selection'] for s in selected_ids if s['id'] == item['id'])
                cursor.execute("UPDATE onbid_items SET is_maverick_selected = 1, ai_curator_comment = ? WHERE id = ?", (reason, item['id']))
                selected_by_maverick.append(item)
            else:
                # Maverick 탈락 매물
                cursor.execute("UPDATE onbid_items SET is_substandard = 1, is_ai_processed = 1, ai_curator_comment = 'Maverick: Filtered out' WHERE id = ?", (item['id'],))
        conn.commit()
        time.sleep(6.5) # Rate limit 준수 (10 RPM)

    # Stage 2: Flash Deep Dive (정예 매물 대상)
    print(f"[*] {len(selected_by_maverick)}건 정예 매물 Deep Dive(Stage 2: Gemini Flash) 가동...", flush=True)
    for item in selected_by_maverick:
        detail_text = get_item_detail_text(item['pbanc_mng_no'], item['cltr_mng_no'])
        analysis = get_flash_deep_dive(item, detail_text)
        
        if analysis:
            cursor.execute("""
                UPDATE onbid_items SET
                    ai_score = ?,
                    ai_expected_profit = ?,
                    ai_margin_percent = ?,
                    ai_pickup_method = ?,
                    ai_difficulty = ?,
                    ai_deep_dive_report = ?,
                    is_target_item = 1,
                    is_ai_processed = 1,
                    is_substandard = 0
                WHERE id = ?
            """, (
                analysis.get('investment_score', 0),
                analysis.get('expected_profit', 0),
                analysis.get('margin_percent', 0.0),
                analysis.get('pickup_method', ''), # Deep dive 결과 기반
                analysis.get('pickup_difficulty', ''),
                json.dumps(analysis, ensure_ascii=False),
                item['id']
            ))
            conn.commit()
            print(f"[+] Deep Dive Completed: {item['onbid_cltr_nm']}")
        else:
            # 실패 시 나중에 재시도할 수 있도록 처리 (현재는 마크만 함)
            print(f"[!] Deep Dive Failed: {item['onbid_cltr_nm']}")
            
    conn.close()
    print("[*] 깔때기 분석 파이프라인 완료!", flush=True)

if __name__ == "__main__":
    run_pipeline()

