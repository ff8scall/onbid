import sqlite3
import os
import json

DB_PATH = os.path.join('data', 'pbid_local.db')

def debug_item():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # IWC 매물 찾기
    cursor.execute("SELECT * FROM onbid_items WHERE onbid_cltr_nm LIKE '%IWC%' LIMIT 1")
    row = cursor.fetchone()
    
    if row:
        print(f"--- DEBUG: {row['onbid_cltr_nm']} ---")
        raw = json.loads(row['raw_data'])
        
        # 가격 관련 모든 필드 출력
        print(f"Min Bid Price (Field): {row['min_bid_prc']}")
        print(f"lowstBidPrcIndctCont: {raw.get('lowstBidPrcIndctCont')}")
        print(f"dpslPrcIndctCont (감정가 가능성): {raw.get('dpslPrcIndctCont')}")
        print(f"pbctCdtnNo: {raw.get('pbctCdtnNo')}")
        print(f"cltrMngNo: {row['cltr_mng_no']}")
        
        # 링크 테스트용 URL 생성 시뮬레이션
        cltrMngNo = row['cltr_mng_no']
        pbctCdtnNo = raw.get('pbctCdtnNo')
        url = f"https://www.onbid.co.kr/op/cta/cltrdtl/collateralDetailInfo.do?cltrMngNo={cltrMngNo}&pbctCdtnNo={pbctCdtnNo}"
        print(f"Generated URL: {url}")
        
        print("\nFull Raw Data:")
        print(json.dumps(raw, indent=2, ensure_ascii=False))
    else:
        print("Item not found.")
    
    conn.close()

if __name__ == "__main__":
    debug_item()
