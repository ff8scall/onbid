import sqlite3
import os
import json

DB_PATH = os.path.join('data', 'pbid_local.db')

def debug_cartier_item():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # '까르띠에'가 포함된 매물 찾기
    cursor.execute("SELECT * FROM onbid_items WHERE onbid_cltr_nm LIKE '%까르띠에%' LIMIT 1")
    row = cursor.fetchone()
    
    if row:
        print(f"--- [DEBUG] {row['onbid_cltr_nm']} ---")
        raw = json.loads(row['raw_data'])
        
        print(f"감정평가액 (apslEvlAmt): {raw.get('apslEvlAmt')}")
        print(f"최저입찰가 (lowstBidPrcIndctCont): {raw.get('lowstBidPrcIndctCont')}")
        print(f"입찰가 (dpslPrcIndctCont): {raw.get('dpslPrcIndctCont')}")
        
        # 딥링크 파라미터 확인
        cltrMngNo = row['cltr_mng_no']
        pbctCdtnNo = raw.get('pbctCdtnNo')
        onbidCltrno = raw.get('onbidCltrno') # 온비드 물건번호
        
        print(f"cltrMngNo: {cltrMngNo}")
        print(f"pbctCdtnNo: {pbctCdtnNo}")
        print(f"onbidCltrno: {onbidCltrno}")
        
        # 동산(동산/기타자산)의 경우 다른 URL 패턴 시도
        # 1. 일반 패턴
        url1 = f"https://www.onbid.co.kr/op/cta/cltrdtl/collateralDetailInfo.do?cltrMngNo={cltrMngNo}&pbctCdtnNo={pbctCdtnNo}"
        # 2. 물건번호 기반 패턴
        url2 = f"https://www.onbid.co.kr/op/cta/cltrdtl/collateralDetailInfo.do?cltrMngNo={cltrMngNo}"
        
        print(f"\n[Generated URL 1]: {url1}")
        print(f"[Generated URL 2]: {url2}")
        
    else:
        print("까르띠에 매물을 찾을 수 없습니다. 키워드를 확인하세요.")
    
    conn.close()

if __name__ == "__main__":
    debug_cartier_item()
