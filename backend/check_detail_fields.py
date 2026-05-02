import requests
import json

SERVICE_KEY = "f095a73a6d8ff681e2c7ab78b7488d895a91b64860bf8af230f64cd223257e45"
DETAIL_URL = "https://apis.data.go.kr/B010003/OnbidPbancCltrDtlSrvc2/getPbancCltrInf2"

def check_detail_fields(pbanc_mng_no):
    params = {
        "serviceKey": SERVICE_KEY,
        "pageNo": 1,
        "numOfRows": 10,
        "resultType": "json",
        "pbancMngNo": pbanc_mng_no
    }
    
    try:
        response = requests.get(DETAIL_URL, params=params, timeout=20)
        print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_detail_fields("884045")
