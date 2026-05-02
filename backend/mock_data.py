import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'pbid_local.db')

def insert_mock_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM onbid_items")
    
    # 온비드 실제 썸네일 URL 예시 (테스트용)
    real_thumb_url = "https://www.onbid.co.kr/op/cm/syc/filemng/filemngprcs/FileMngPrcsController/dnldFile.do?atchFileLstNo=16994712&atchSn=1&hashCrpsNo=LEMAABOEOAMJLGKCEDLNDMEPIAGKLJGBCNOLMCMDBMKEKGKMMLFHDAODBLPIGHBK&downloadImageKind=THNL_NM"
    
    mock_items = [
        {
            "pbanc_mng_no": "202605-00001-00",
            "cltr_mng_no": "2026-0001-001",
            "onbid_cltr_nm": "불용품 매각 (삼성 노트북 외 5종)",
            "cltr_adr": "서울특별시 서초구 ...",
            "min_bid_prc": 500000,
            "main_category": "IT/장비",
            "sub_category": "노트북",
            "thumb_url": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?q=80&w=1000&auto=format&fit=crop",
            "ai_score": 45,
            "ai_estimated_specs": "Intel Core i5 8세대 추정, RAM 8GB, SSD 256GB",
            "ai_reason": "연한 경과로 인한 불용품이며 대량 매각으로 개별 상태 확인 어려움.",
            "ai_recommendation": "Pass",
            "ai_catchphrase": "연식 있는 사무용 노트북, 부품용으로 적합",
            "ai_risk_factor": "배터리 수명 저하 예상, 외관 스크래치 다수",
            "ai_resale_value": 350000,
            "ai_is_pickup_friendly": 1,
            "is_ai_processed": 1,
            "orgNm": "서초구청"
        },
        {
            "pbanc_mng_no": "202605-00001-00",
            "cltr_mng_no": "2026-0001-002",
            "onbid_cltr_nm": "애플 아이폰 14 프로 256GB (중고)",
            "cltr_adr": "경기도 수원시 ...",
            "min_bid_prc": 800000,
            "main_category": "IT/장비",
            "sub_category": "휴대폰",
            "thumb_url": "https://images.unsplash.com/photo-1678685888221-cda773a3dcdb?q=80&w=1000&auto=format&fit=crop",
            "ai_score": 88,
            "ai_estimated_specs": "iPhone 14 Pro, 256GB, Space Black",
            "ai_reason": "압류 물품으로 연식 대비 최저가가 중고 시세보다 25% 저렴함. 상세 설명상 액정 깨끗함.",
            "ai_recommendation": "Strong Buy",
            "ai_catchphrase": "상태 좋은 14 프로, 중고 장터보다 저렴한 기회!",
            "ai_risk_factor": "구성품 없음 (본체 단품), iCloud 락 해제 여부 현장 확인 필요",
            "ai_resale_value": 1100000,
            "ai_is_pickup_friendly": 0,
            "is_ai_processed": 1,
            "orgNm": "수원지방법원"
        },
        {
            "pbanc_mng_no": "202605-00002-00",
            "cltr_mng_no": "2026-0002-001",
            "onbid_cltr_nm": "Dell Precision 워크스테이션 T7920 (Xeon 골드)",
            "cltr_adr": "대전광역시 유성구 ...",
            "min_bid_prc": 2500000,
            "main_category": "IT/장비",
            "sub_category": "데스크탑",
            "thumb_url": real_thumb_url,
            "ai_score": 95,
            "ai_estimated_specs": "Xeon Gold 6248R x2, 128GB RAM, RTX 3080 추정",
            "ai_reason": "국가 연구소 배출 매물로 관리 상태 최상. 상세 설명에 '정기 점검 완료' 명시됨.",
            "ai_recommendation": "Strong Buy",
            "ai_catchphrase": "연구소급 끝판왕 워크스테이션, 딥러닝 입문자 강추",
            "ai_risk_factor": "운영체제 미포함 (OS 직접 설치 필요), 무게가 매우 무거워 승용차 수령 권장",
            "ai_resale_value": 4500000,
            "ai_is_pickup_friendly": 0,
            "is_ai_processed": 1,
            "orgNm": "한국전자통신연구원"
        }
    ]
    
    for item in mock_items:
        raw_data = {k: v for k, v in item.items() if k not in ["ai_score", "ai_estimated_specs", "ai_reason", "ai_recommendation", "ai_catchphrase", "ai_risk_factor", "ai_resale_value", "ai_is_pickup_friendly", "is_ai_processed", "thumb_url"]}
        cursor.execute('''
            INSERT OR REPLACE INTO onbid_items (
                pbanc_mng_no, cltr_mng_no, onbid_cltr_nm, cltr_adr, 
                min_bid_prc, main_category, sub_category, thumb_url, raw_data,
                ai_score, ai_estimated_specs, ai_reason, ai_recommendation, ai_catchphrase,
                ai_risk_factor, ai_resale_value, ai_is_pickup_friendly, is_ai_processed
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item["pbanc_mng_no"],
            item["cltr_mng_no"],
            item["onbid_cltr_nm"],
            item["cltr_adr"],
            item["min_bid_prc"],
            item["main_category"],
            item["sub_category"],
            item["thumb_url"],
            json.dumps(raw_data, ensure_ascii=False),
            item["ai_score"],
            item["ai_estimated_specs"],
            item["ai_reason"],
            item["ai_recommendation"],
            item["ai_catchphrase"],
            item["ai_risk_factor"],
            item["ai_resale_value"],
            item["ai_is_pickup_friendly"],
            item["is_ai_processed"]
        ))
        
    conn.commit()
    conn.close()
    print("Mock data with Thumbnails and Deep Analysis results inserted.")

if __name__ == "__main__":
    insert_mock_data()
