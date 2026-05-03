import sqlite3
import os
import json
import sys

# Set encoding for Windows terminal
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DB_PATH = os.path.join('data', 'pbid_local.db')

def analyze_promising_items():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 191개 매물 중 키워드로 알짜 찾기
    keywords = ['IWC', 'HERMES', '샤넬', '24K', '금', '노트북', '아이폰']
    
    print("=" * 60)
    print("OnBid Arbitrage Master - Manual Analysis Report (Real Data)")
    print("=" * 60)
    
    for kw in keywords:
        cursor.execute("SELECT * FROM onbid_items WHERE onbid_cltr_nm LIKE ?", (f'%{kw}%',))
        rows = cursor.fetchall()
        for row in rows:
            try:
                raw = json.loads(row['raw_data'])
                price_str = raw.get('lowstBidPrcIndctCont', '0')
                
                print(f"\n[Item]: {row['onbid_cltr_nm']}")
                print(f"[Category]: {row['sub_category']} | [Location]: {row['cltr_adr']}")
                print(f"[Min Bid Price]: {price_str}")
                print(f"[Agency]: {raw.get('orgNm', 'N/A')}")
                
                name_upper = row['onbid_cltr_nm'].upper()
                if 'IWC' in name_upper:
                    print(">> Analysis: IWC Luxury watches sell for 5M~15M KRW. If bid is low, Strong Buy.")
                elif 'HERMES' in name_upper:
                    print(">> Analysis: Hermes items have top liquidity. Market price 2M~8M KRW.")
                elif '금' in row['onbid_cltr_nm'] or '24K' in name_upper:
                    print(">> Analysis: Precious metals can be cashed out immediately based on weight. Priority 0.")
                
                print("-" * 40)
            except Exception as e:
                continue

    conn.close()

if __name__ == "__main__":
    analyze_promising_items()
