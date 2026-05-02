import requests
import json

SERVICE_KEY = "f095a73a6d8ff681e2c7ab78b7488d895a91b64860bf8af230f64cd223257e45"
URL = "http://apis.data.go.kr/B010003/OnbidMvastListSrvc2/getMvastCltrDtl2"

def check_mvast_detail(cltr_mng_no):
    params = {
        "serviceKey": SERVICE_KEY,
        "pageNo": 1,
        "numOfRows": 10,
        "resultType": "json",
        "cltrMngNo": cltr_mng_no
    }
    
    print(f"[*] Checking Mvast Detail for {cltr_mng_no}...")
    try:
        response = requests.get(URL, params=params, timeout=20)
        print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_mvast_detail("2026-0400-021612")
