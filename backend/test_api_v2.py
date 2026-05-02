import requests
import json
from urllib.parse import unquote

def test_api():
    # 사용자가 제공한 키 (이미 인코딩된 것인지 디코딩된 것인지 모름)
    service_key = "f095a73a6d8ff681e2c7ab78b7488d895a91b64860bf8af230f64cd223257e45"
    
    # 1. 디코딩된 키 시도
    decoded_key = unquote(service_key)
    
    url_dtl = "https://apis.data.go.kr/B010003/OnbidPbancCltrDtlSrvc2/getPbancCltrInf"
    
    params = {
        "serviceKey": decoded_key,
        "pageNo": 1,
        "numOfRows": 1,
        "resultType": "json",
        "pbancMngNo": "202406-21411-00"
    }
    
    print(f"Testing with decoded key... (Timeout 30s)")
    try:
        response = requests.get(url_dtl, params=params, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:1000]}")
    except Exception as e:
        print(f"Decoded Key Error: {e}")

    # 2. 인코딩된 키를 쿼리 스트링에 직접 박아서 시도 (requests의 자동 인코딩 방지)
    print(f"\nTesting with raw key in URL...")
    raw_url = f"{url_dtl}?serviceKey={service_key}&pageNo=1&numOfRows=1&resultType=json&pbancMngNo=202406-21411-00"
    try:
        response = requests.get(raw_url, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:1000]}")
    except Exception as e:
        print(f"Raw Key Error: {e}")

if __name__ == "__main__":
    test_api()
