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
    
    query = 'SELECT "id", "pbanc_mng_no", "cltr_mng_no", "onbid_cltr_nm", "cltr_adr", "min_bid_prc", "main_category", "sub_category", "thumb_url", "ai_score", "raw_data", "created_at" FROM onbid_items WHERE main_category = "IT/장비"'
    params = []
    
    if category:
        query += " AND sub_category = ?"
        params.append(category)
        
    query += " ORDER BY COALESCE(ai_score, 0) DESC, created_at DESC"
    
    cursor.execute(query, params)
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
    cursor.execute("SELECT DISTINCT sub_category FROM onbid_items WHERE main_category = 'IT/장비'")
    cats = [row[0] for row in cursor.fetchall()]
    conn.close()
    return cats
