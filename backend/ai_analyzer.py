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
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'pbid_local.db')

# 모델 설정: AI Engine (NVIDIA NIM) - Maverick & Flash 모두 Llama 3.1 8B로 단일화
MAVERICK_MODEL = "meta/llama-3.1-8b-instruct"
FLASH_MODEL = "meta/llama-3.1-8b-instruct"

# NVIDIA NIM 클라이언트 초기화
step_client = None
if NVIDIA_API_KEY:
    try:
        step_client = OpenAI(api_key=NVIDIA_API_KEY, base_url=NVIDIA_BASE_URL)
    except Exception as e:
        print(f"[!] NVIDIA NIM Init Error: {e}")

def clean_text(text):
    """HTML 태그 제거 및 불필요한 공백 정리"""
    if not text: return ""
    # HTML 태그 제거
    clean = re.compile('<.*?>')
    text = re.sub(clean, '', text)
    # 특수문자 및 과도한 공백 정리
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def classify_item_type(item, detail_text):
    """매물의 유형을 판별 (단건 vs 일괄 vs 정보부족)"""
    name = item['onbid_cltr_nm']
    
    # 1. 일괄 매각 판별 (정규식)
    # '외 N건', '일체', '등 N점', 'N개', 'N대', 'N종', 'N세트', 'N식' (N > 1)
    bundle_patterns = [
        r'외\s*\d+\s*[건대종점개]', 
        r'일체', 
        r'\d+\s*[건대종점개세트식set]{1,2}',
        r'일괄'
    ]
    
    is_bundle = False
    for p in bundle_patterns:
        if re.search(p, name):
            # 단건인 경우(1개, 1대, 1점 등)는 제외
            if re.search(r'1\s*[건대종점개세트식]{1,2}', name):
                continue
            is_bundle = True
            break
            
    # 2. 정보 부족 판별
    is_missing_info = False
    clean_detail = clean_text(detail_text)
    
    # 감정가가 있는 귀금속/명품은 상세 텍스트가 부족해도 '분석 적합'으로 간주
    is_high_value = item['sub_category'] in ['귀금속', '명품']
    has_appraisal = int(item['apsl_evl_amt'] or 0) > 0
    
    if is_high_value and has_appraisal:
        is_missing_info = False # 강제 통과
    else:
        if not detail_text or len(clean_detail) < 30:
            is_missing_info = True
        elif '첨부파일' in detail_text or '공고문' in detail_text:
            if len(clean_detail) < 150: # 텍스트가 적으면서 첨부파일 언급 시
                is_missing_info = True
            
    if is_bundle: return "BUNDLE", "일괄 매각 매물 (정밀 시세 산출 어려움)"
    if is_missing_info: return "MISSING", "상세 설명 부족 (첨부파일 참조 매물)"
    return "SINGLE", "분석 적합 매물"

# Stage 1: Maverick Batch Prompt
MAVERICK_BATCH_PROMPT = """
**Role:** You are a strategic arbitrage filter engine for the OnBid auction market.
**Task:** Analyze the following list of auction items and identify "High-Potential" items for resale.

**Core Filtering Rules (Diversity is Key):**
1. **Electronics:** Brand new or high-demand models (Apple, Samsung, GPU, etc.).
2. **Luxury Goods:** Bags, watches, or accessories from reputable brands (Rolex, Chanel, Vuitton, Gucci, etc.).
3. **Precious Metals:** Gold (bars, rings, 14K/18K/24K), Silver, Diamonds.
4. **Gift Cards:** Department store or cultural gift cards with a clear discount potential.
5. **Miscellaneous:** Any item that clearly looks like a profitable resale opportunity.

**Selection Strategy:**
- Do NOT be too restrictive in Stage 1. If an item has ANY chance of being a luxury good or a popular electronic, SELECT it.
- Ensure you pick a balanced mix of categories if available.
- Exclude obvious trash (waste, broken furniture, scrap metal, used clothing with no brand).

**Input Items:**
{items_json}

**Output Format (Strictly JSON):**
Return a JSON object with a key "selected_ids" containing a list of objects.
{{
  "selected_ids": [
    {{ "id": 123, "reason_for_selection": "Rolex watch, high resale value expected." }},
    ...
  ]
}}
"""

# Stage 2: Flash Deep Dive Prompt
FLASH_DEEP_DIVE_PROMPT = """
**Role:** You are a senior investment analyst specializing in physical asset arbitrage.
**Task:** Perform a "Deep Dive" financial analysis on this SINGLE auction item and provide a KOREAN report.

**Item Data:**
- Name: {item_name}
- Appraisal Price: {appraisal_price} KRW (전문가 감정가)
- Min Bid Price: {min_bid_price} KRW
- Detail: {detail_text}
- Address: {address}

**Instructions:**
1. **Financial Logic (Crucial)**: 
   - Primary Reason for Margin: Compare "Appraisal Price" (Expert Value) vs "Min Bid Price".
   - If Min Bid Price is significantly lower than Appraisal Price, highlight the **Price Drop Ratio** (e.g., "70% discount from initial expert valuation due to repeated auction failures").
2. **Market Price Estimation**: Research the current resale value for this SPECIFIC model/brand.
3. **Price Gap Analysis (NO VAGUE REASONING)**:
   - **DO NOT** use vague regional reasons (e.g., "Shillim-dong has shops") or generic brand talk.
   - **DO** explain why the market price is higher than the current bid (e.g., "The model 'LV Keepall 50' sells for 2M KRW in used markets, but the current bid is only 0.75M KRW").
   - Mention the potential resale liquidity (how fast it sells).

**Output Format (Strictly a JSON object):**
{{
  "estimated_market_price": number,
  "estimated_costs": number,
  "break_even_price": number,
  "expected_profit": number,
  "margin_percent": number,
  "reason_for_price_gap": "LOGICAL financial explanation in KOREAN (Focus on price drop from appraisal and used market comparison)",
  "simple_summary": "ONE-LINE punchy catchphrase in KOREAN",
  "risk_factors": ["list", "of", "strings"],
  "three_line_summary": "string in KOREAN",
  "investment_score": number (0-100),
  "pickup_method": "Parcel" or "Visit",
  "pickup_difficulty": "Easy", "Medium", or "Hard"
}}
"""

def get_maverick_batch_analysis(items_list):
    """NVIDIA Llama 3.1 8B를 사용한 1차 대량 필터링"""
    if not step_client:
        print("[!] NIM Client not initialized. Bypassing...")
        return [{"id": it['id'], "reason_for_selection": "Bypass (Client Error)"} for it in items_list[:10]]

    # 단순화를 위해 ID와 이름, 가격만 포함
    minified_items = []
    for it in items_list:
        minified_items.append({
            "id": it['id'],
            "name": it['onbid_cltr_nm'],
            "price": it['min_bid_prc']
        })

    prompt = MAVERICK_BATCH_PROMPT.format(items_json=json.dumps(minified_items, ensure_ascii=False))
    
    try:
        response = step_client.chat.completions.create(
            model=MAVERICK_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0
        )
        res_json = json.loads(response.choices[0].message.content)
        return res_json.get("selected_ids", [])
    except Exception as e:
        print(f"[!] Maverick Batch Error: {e}")
        return []

def get_flash_deep_dive(item, detail_text, item_type, type_reason):
    """Llama 3.1 8B를 사용한 2차 정밀 분석"""
    fallback_res = {
        "investment_score": 0, "expected_profit": 0, "margin_percent": 0, 
        "pickup_method": "정보없음", "pickup_difficulty": "Unknown", 
        "three_line_summary": "분석 보류"
    }
    
    # 1. 분석 불가 항목 처리 (보류)
    if item_type in ["BUNDLE", "MISSING"]:
        fallback_res["pickup_difficulty"] = "Hold"
        fallback_res["three_line_summary"] = f"[{item_type}] {type_reason}"
        return fallback_res
    
    if not step_client: return fallback_res
    
    # 상세 설명이 없을 경우에 대한 처리 강화
    detail_content = clean_text(detail_text)[:4000] if detail_text else "상세 설명 데이터가 제공되지 않았습니다. 물건 명칭과 주소를 바탕으로 일반적인 가치를 추정하십시오."
    
    # 가격 하락폭 계산 (감정가 대비)
    appraisal = item['apsl_evl_amt'] or 0
    min_bid = item['min_bid_prc']
    drop_info = ""
    if appraisal > 0:
        drop_percent = int((1 - min_bid / appraisal) * 100)
        drop_info = f"\n- Price Drop: 감정가({appraisal:,.0f}원) 대비 {drop_percent}% 하락한 상태입니다. 유찰이 여러 번 진행되었을 가능성이 큽니다."

    prompt = FLASH_DEEP_DIVE_PROMPT.format(
        item_name=item['onbid_cltr_nm'],
        detail_text=detail_content + drop_info,
        appraisal_price=appraisal,
        min_bid_price=min_bid,
        address=item['cltr_adr']
    )
    
    try:
        response = step_client.chat.completions.create(
            model=FLASH_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0
        )
        text = response.choices[0].message.content
        # JSON 블록 추출 (마크다운 등 포함 대비)
        json_match = re.search(r'(\{.*\})', text, re.DOTALL)
        if json_match:
            text = json_match.group(1)
        return json.loads(text)
    except Exception as e:
        print(f"[!] Flash Deep Dive Error: {e}")
        # 실패 시 0점보다는 '분석 대기' 상태를 유지하거나 최소한의 긍정적 지표를 줌 (사용자 경험)
        fallback_res["investment_score"] = 50 
        fallback_res["three_line_summary"] = f"API 통신 일시적 오류로 기본 정보를 기반으로 평가되었습니다. (사유: {str(e)[:50]})"
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
    """Llama 3.1 8B 단일 모델 기반 깔때기형 파이프라인 실행"""
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
                reason = next((s.get('reason_for_selection', 'Bypass') for s in selected_ids if s['id'] == item['id']), "Bypass")
                cursor.execute("UPDATE onbid_items SET is_maverick_selected = 1, ai_curator_comment = ? WHERE id = ?", (reason, item['id']))
                selected_by_maverick.append(item)
            else:
                # Maverick 탈락 매물
                cursor.execute("UPDATE onbid_items SET is_substandard = 1, is_ai_processed = 1, ai_curator_comment = 'Maverick: Filtered out' WHERE id = ?", (item['id'],))
        conn.commit()
        time.sleep(6.5) # Rate limit 준수 (10 RPM)

    # Stage 2: Flash Deep Dive (정예 매물 대상)
    print(f"[*] {len(selected_by_maverick)}건 정예 매물 유형 분류 및 Deep Dive 가동...", flush=True)
    for item in selected_by_maverick:
        # DB에 미리 수집된 detail_text 활용
        detail_text = item['detail_text'] if 'detail_text' in item.keys() and item['detail_text'] else ""
        
        # 유형 판별
        item_type, type_reason = classify_item_type(item, detail_text)
        
        if item_type != "SINGLE":
            print(f"[-] Analysis Postponed ({item_type}): {item['onbid_cltr_nm']}")
            analysis = get_flash_deep_dive(item, detail_text, item_type, type_reason)
        else:
            print(f"[*] Deep Dive Starting (SINGLE): {item['onbid_cltr_nm']}")
            analysis = get_flash_deep_dive(item, detail_text, item_type, type_reason)
        
        if analysis:
            # 보류 매물은 is_target_item을 0으로 두거나 특정 처리를 할 수 있음
            # 여기서는 분석이 끝난 것으로 간주하되 점수는 0점으로 저장됨
            # 예상 수익 산출 (Break-even Price - Min Bid Price)
            # AI가 준 expected_profit을 우선 사용하되, 없을 경우 계산 시도
            raw_profit = analysis.get('expected_profit', 0)
            
            summary = analysis.get('three_line_summary', '')
            gap_reason = analysis.get('reason_for_price_gap', '')
            simple_sum = analysis.get('simple_summary', '')
            
            cursor.execute("""
                UPDATE onbid_items SET
                    ai_score = ?,
                    ai_expected_profit = ?,
                    ai_margin_percent = ?,
                    ai_pickup_method = ?,
                    ai_difficulty = ?,
                    ai_curator_comment = ?,
                    ai_deep_dive_report = ?,
                    ai_catchphrase = ?,
                    ai_reason = ?,
                    is_target_item = ?,
                    is_ai_processed = 1,
                    is_substandard = ?
                WHERE id = ?
            """, (
                analysis.get('investment_score', 0),
                raw_profit,
                analysis.get('margin_percent', 0.0),
                analysis.get('pickup_method', '정보없음'),
                analysis.get('pickup_difficulty', 'Unknown'),
                summary, 
                json.dumps(analysis, ensure_ascii=False),
                simple_sum,
                gap_reason,
                1 if analysis.get('investment_score', 0) >= 60 else 0,
                1 if analysis.get('investment_score', 0) < 60 else 0,
                item['id']
            ))
            conn.commit()
            if analysis.get('pickup_difficulty') != "Hold":
                print(f"[+] Deep Dive Completed: {item['onbid_cltr_nm']}")
        else:
            # 실패 시 나중에 재시도할 수 있도록 처리 (현재는 마크만 함)
            print(f"[!] Deep Dive Failed: {item['onbid_cltr_nm']}")
            
    conn.close()
    print("[*] 깔때기 분석 파이프라인 완료!", flush=True)

if __name__ == "__main__":
    run_pipeline()

