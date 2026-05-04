import requests
import json
import sqlite3
import os
import xml.etree.ElementTree as ET
from datetime import datetime

# 설정
SERVICE_KEY = "f095a73a6d8ff681e2c7ab78b7488d895a91b64860bf8af230f64cd223257e45"
DETAIL_URL = "https://apis.data.go.kr/B010003/OnbidPbancCltrDtlSrvc2/getPbancCltrInf2"
LIST_URL = "https://apis.data.go.kr/B010003/OnbidMvastListSrvc2/getMvastCltrList2"
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'pbid_local.db')

# 분류 키워드
CATEGORIES = {
    '전자기기': ['컴퓨터', '데스크탑', '본체', '노트북', '랩탑', '맥북', '그램', '휴대폰', '스마트폰', '아이폰', '갤럭시', '태블릿', '아이패드', '모니터', 'GPU', '애플', 'APPLE'],
    '명품': ['가방', '시계', '롤렉스', '샤넬', '에르메스', '루이비통', '구찌', '프라다', 'ROLEX', 'CHANEL', '명품'],
    '귀금속': ['순금', '14K', '18K', '24K', '금반지', '금목걸이', '골드바', '다이아', '귀금속'],
    '상품권': ['상품권', '기프트카드', '문화상품권', '백화점상품권', '신세계', '롯데', '국민관광']
}

def classify_item(name):
    """물건명을 기반으로 카테고리 분류"""
    name_upper = name.upper()
    for cat, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw.upper() in name_upper:
                return "환금성자산", cat
    return "기타", "미분류"

def parse_xml_to_dict_list(xml_content):
    """XML 응답을 딕셔너리 리스트로 변환"""
    try:
        root = ET.fromstring(xml_content)
        items = []
        for item_node in root.findall('.//item'):
            item_dict = {}
            for child in item_node:
                item_dict[child.tag] = child.text
            items.append(item_dict)
        return items
    except Exception as e:
        print(f"[!] XML Parsing Error: {e}")
        return []

import time
from urllib.parse import quote

def search_it_items():
    """신규 동산 목록 API를 사용하여 타겟 매물 검색 및 저장"""
    search_keywords = ["노트북", "맥북", "아이폰", "아이패드", "갤럭시", "명품", "가방", "시계", "롤렉스", "샤넬", "순금", "14K", "18K", "골드바", "상품권"]
    
    conn = sqlite3.connect(DB_PATH, timeout=20) # DB Lock 방지 타임아웃 추가
    cursor = conn.cursor()
    total_new_saved = 0

    for keyword in search_keywords:
        print(f"[*] Searching for keyword: {keyword}")
        # 인증키 인코딩 이슈를 피하기 위해 URL에 직접 삽입
        url = f"http://apis.data.go.kr/B010003/OnbidMvastListSrvc2/getMvastCltrList2?serviceKey={SERVICE_KEY}"
        params = {
            "pageNo": 1,
            "numOfRows": 100,
            "prptDivCd": "0007,0010,0005,0004,0002,0003,0006,0008,0011,0013",
            "pvctTrgtYn": "N",
            "onbidCltrNm": keyword # requests가 인코딩하도록 둠
        }
        
        try:
            time.sleep(1) # TPS 제한 대응
            response = requests.get(url, params=params, timeout=30)
            if response.status_code != 200:
                print(f"[!] Error: Status code {response.status_code}")
                continue
                
            # XML 파싱
            items = parse_xml_to_dict_list(response.text)
            if not items:
                print(f"[*] No items found for '{keyword}'.")
                continue

            for item in items:
                cltr_nm = item.get('onbidCltrNm', '')
                main_cat, sub_cat = classify_item(cltr_nm)
                
                # 상세 정보 즉시 수집 시도
                pbanc_id = item.get('pbctNo') or item.get('pbancMngNo') or item.get('onbidPbancNo')
                cltr_id = item.get('cltrMngNo')
                detail_text = get_item_detail_text(pbanc_id, cltr_id) if pbanc_id else ""
                
                # 감정평가액 추출 및 정수 변환
                raw_apsl = item.get('apslEvlAmt', 0)
                try:
                    apsl_val = int(str(raw_apsl).replace(',', '')) if raw_apsl else 0
                except:
                    apsl_val = 0

                # 최저입찰가 정수 변환
                raw_min = item.get('lowstBidPrcIndctCont', 0)
                try:
                    min_val = int(str(raw_min).replace(',', '')) if raw_min else 0
                except:
                    min_val = 0

                try:
                    cursor.execute('''
                        INSERT INTO onbid_items (
                            pbanc_mng_no, cltr_mng_no, onbid_cltr_nm, cltr_adr, 
                            min_bid_prc, apsl_evl_amt, main_category, sub_category, thumb_url, bid_end_date, raw_data, detail_text
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(cltr_mng_no) DO UPDATE SET
                            is_ai_processed = CASE 
                                WHEN onbid_items.min_bid_prc <> excluded.min_bid_prc THEN 0 
                                ELSE onbid_items.is_ai_processed 
                            END,
                            pbanc_mng_no = excluded.pbanc_mng_no, -- 공고번호 업데이트
                            min_bid_prc = excluded.min_bid_prc,
                            apsl_evl_amt = excluded.apsl_evl_amt,
                            onbid_cltr_nm = excluded.onbid_cltr_nm,
                            cltr_adr = excluded.cltr_adr,
                            main_category = excluded.main_category,
                            sub_category = excluded.sub_category,
                            thumb_url = excluded.thumb_url,
                            bid_end_date = excluded.bid_end_date,
                            raw_data = excluded.raw_data,
                            detail_text = excluded.detail_text,
                            is_expired = 0 -- 재수집된 경우 만료 해제
                    ''', (
                        pbanc_id, 
                        cltr_id,
                        cltr_nm,
                        f"{item.get('lctnSdnm', '')} {item.get('lctnSggnm', '')} {item.get('lctnEmdNm', '')}",
                        min_val,
                        apsl_val,
                        main_cat,
                        sub_cat,
                        item.get('thnlImgUrlAdr'),
                        item.get('cltrBidEndDt'),
                        json.dumps(item, ensure_ascii=False),
                        detail_text
                    ))
                    total_new_saved += 1
                except Exception as e:
                    print(f"[!] DB Insert Error: {e}")
                    
        except Exception as e:
            print(f"[!] Connection Error for '{keyword}': {e}")
            
    conn.commit()
    conn.close()
    print(f"[*] Search completed. Total {total_new_saved} new items processed.")

def get_item_detail_text(pbanc_mng_no, cltr_mng_no):
    """특정 물건의 상세 설명(cltrDtlCont)을 가져옴 (JSON/XML 모두 시도)"""
    if not pbanc_mng_no: return ""
    
    params = {
        "serviceKey": SERVICE_KEY,
        "pageNo": 1,
        "numOfRows": 100, # 혹시 모르니 넉넉하게
        "resultType": "json",
        "pbancMngNo": pbanc_mng_no
    }
    
    try:
        # 1. JSON 시도
        response = requests.get(DETAIL_URL, params=params, timeout=15)
        if response.status_code == 200:
            try:
                data = response.json()
                items = data.get('body', {}).get('items', {}).get('item', [])
                if isinstance(items, dict): items = [items] # 단건 처리
                for item in items:
                    if str(item.get('cltrMngNo')) == str(cltr_mng_no):
                        return item.get('cltrDtlCont', "")
            except:
                pass # JSON 파싱 실패 시 XML 시도
        
        # 2. XML 시도 (JSON이 가끔 불안정함)
        params["resultType"] = "xml"
        response = requests.get(DETAIL_URL, params=params, timeout=15)
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            for item_node in root.findall('.//item'):
                c_mng = item_node.find('cltrMngNo')
                if c_mng is not None and str(c_mng.text) == str(cltr_mng_no):
                    dtl = item_node.find('cltrDtlCont')
                    return dtl.text if dtl is not None else ""
                    
    except Exception as e:
        print(f"[!] Detail API Error ({pbanc_mng_no}): {e}")
    return ""

def collect_details(pbanc_mng_no):
    """공고번호를 기준으로 상세 물건 정보 수집 (JSON 작동함)"""
    params = {
        "serviceKey": SERVICE_KEY,
        "pageNo": 1,
        "numOfRows": 100,
        "resultType": "json",
        "pbancMngNo": pbanc_mng_no
    }
    
    print(f"[*] Collecting details for announcement: {pbanc_mng_no}")
    try:
        response = requests.get(DETAIL_URL, params=params, timeout=30)
        if response.status_code != 200:
            print(f"[!] Error: Status code {response.status_code}")
            return
        
        data = response.json()
        items = data.get('body', {}).get('items', {}).get('item', [])
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        count = 0
        for item in items:
            cltr_nm = item.get('onbidCltrNm', '')
            main_cat, sub_cat = classify_item(cltr_nm)
            
            cursor.execute('''
                INSERT INTO onbid_items (
                    pbanc_mng_no, cltr_mng_no, onbid_cltr_nm, cltr_adr, 
                    min_bid_prc, main_category, sub_category, thumb_url, bid_end_date, raw_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(cltr_mng_no) DO UPDATE SET
                    is_ai_processed = CASE 
                        WHEN onbid_items.min_bid_prc <> excluded.min_bid_prc THEN 0 
                        ELSE onbid_items.is_ai_processed 
                    END,
                    pbanc_mng_no = excluded.pbanc_mng_no,
                    min_bid_prc = excluded.min_bid_prc,
                    onbid_cltr_nm = excluded.onbid_cltr_nm,
                    cltr_adr = excluded.cltr_adr,
                    main_category = excluded.main_category,
                    sub_category = excluded.sub_category,
                    thumb_url = excluded.thumb_url,
                    bid_end_date = excluded.bid_end_date,
                    raw_data = excluded.raw_data
            ''', (
                item.get('pbancMngNo'),
                item.get('cltrMngNo'),
                cltr_nm,
                item.get('cltrAdr'),
                item.get('lowstBidPrcIndctCont'),
                main_cat,
                sub_cat,
                item.get('thnlImgUrlAdr'),
                item.get('cltrBidEndDt'),
                json.dumps(item, ensure_ascii=False)
            ))
            count += 1
        
        conn.commit()
        conn.close()
        print(f"[*] Total {count} items processed for {pbanc_mng_no}.")
    except Exception as e:
        print(f"[!] Connection Error: {e}")

def mark_expired_items():
    """현재 시간 기준으로 입찰이 종료된 매물을 만료 처리"""
    now_str = datetime.now().strftime("%Y%m%d%H%M")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE onbid_items 
        SET is_expired = 1 
        WHERE bid_end_date IS NOT NULL 
          AND bid_end_date < ? 
          AND is_expired = 0
    ''', (now_str,))
    
    count = cursor.rowcount
    conn.commit()
    conn.close()
    if count > 0:
        print(f"[*] {count} items marked as expired.")

if __name__ == "__main__":
    search_it_items()
    mark_expired_items()
