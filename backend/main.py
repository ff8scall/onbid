from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os
import json

app = FastAPI()

# CORS 설정 (프론트엔드 연동용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'pbid_local.db')

@app.get("/")
def read_root():
    return {"message": "Pbid API is running"}

@app.get("/items")
def get_items(category: str = None):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = 'SELECT "id", "pbanc_mng_no", "cltr_mng_no", "onbid_cltr_nm", "cltr_adr", "min_bid_prc", "main_category", "sub_category", "thumb_url", "ai_score", "ai_expected_profit", "ai_margin_percent", "ai_pickup_method", "ai_difficulty", "ai_curator_comment", "is_target_item", "raw_data", "created_at" FROM onbid_items WHERE main_category = "환금성자산" AND is_target_item = 1 AND is_substandard = 0'
    params = []
    
    if category:
        query += " AND sub_category = ?"
        params.append(category)
        
    query += " ORDER BY ai_score DESC, COALESCE(ai_expected_profit, 0) DESC, created_at DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    items = []
    for row in rows:
        item = dict(row)
        item['raw_data'] = json.loads(item['raw_data'])
        items.append(item)
        
    conn.close()
    return items

@app.get("/items/substandard")
def get_substandard_items():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = 'SELECT * FROM onbid_items WHERE is_substandard = 1 ORDER BY ai_score DESC, created_at DESC'
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    items = []
    for row in rows:
        item = dict(row)
        item['raw_data'] = json.loads(item['raw_data'])
        items.append(item)
        
    conn.close()
    return items

@app.get("/items/candidates")
def get_candidate_items():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Maverick은 통과했지만 아직 Flash 정밀 분석 전이거나 substandard가 아닌 것
    query = 'SELECT * FROM onbid_items WHERE is_maverick_selected = 1 AND is_target_item = 0 AND is_substandard = 0 ORDER BY ai_score DESC, created_at DESC'
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    items = []
    for row in rows:
        item = dict(row)
        item['raw_data'] = json.loads(item['raw_data'])
        items.append(item)
        
    conn.close()
    return items

@app.get("/items/{item_id}")
def get_item(item_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM onbid_items WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        item = dict(row)
        item['raw_data'] = json.loads(item['raw_data'])
        return item
    return {"error": "Item not found"}

@app.get("/categories")
def get_categories():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT sub_category FROM onbid_items WHERE main_category = '환금성자산' AND is_target_item = 1 AND is_substandard = 0")
    cats = [row[0] for row in cursor.fetchall()]
    conn.close()
    return cats

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
