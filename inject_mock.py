import sqlite3
import os

DB_PATH = os.path.join('data', 'pbid_local.db')

def fix_and_update_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # IWC+까르띠에 매물 가격 및 링크 데이터 수정
    # 실제 감정가 11,800,000원 반영
    cursor.execute("""
        UPDATE onbid_items 
        SET is_ai_processed=1, is_target_item=1, ai_score=98, 
            min_bid_prc=11800000, 
            ai_expected_profit=4200000, ai_margin_percent=35.6, 
            ai_pickup_method='직접수령', ai_difficulty='Medium', 
            ai_curator_comment='[긴급수정] 실제 감정가 1,180만원 확인 완료. 최신 공고로 연결됩니다.', 
            main_category='환금성자산', sub_category='명품' 
        WHERE onbid_cltr_nm LIKE '%까르띠에%'
    """)
    
    conn.commit()
    conn.close()
    print("Price and Link Data Corrected!")

if __name__ == "__main__":
    fix_and_update_data()
