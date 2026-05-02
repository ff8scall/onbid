import requests
import json
from urllib.parse import unquote

def test_endpoints():
    service_key = "f095a73a6d8ff681e2c7ab78b7488d895a91b64860bf8af230f64cd223257e45"
    decoded_key = unquote(service_key)
    
    endpoints = [
        # 사용자가 준 상세 API
        "https://apis.data.go.kr/B010003/OnbidPbancCltrDtlSrvc2/getPbancCltrInf",
        # 사용자가 준 상세 API v2?
        "https://apis.data.go.kr/B010003/OnbidPbancCltrDtlSrvc2/getPbancCltrInf2",
        # 일반적인 물건 목록 API
        "https://apis.data.go.kr/B010003/OnbidCltrInfoSrvc/getOnbidCltrList",
        # 일반적인 공고 목록 API
        "https://apis.data.go.kr/B010003/OnbidPbancInfoSrvc/getOnbidPbancList"
    ]
    
    for url in endpoints:
        print(f"\n--- Testing Endpoint: {url} ---")
        params = {
            "serviceKey": decoded_key,
            "pageNo": 1,
            "numOfRows": 5,
            "resultType": "json"
        }
        # 상세 API인 경우 샘플 번호 추가
        if "getPbancCltrInf" in url:
            params["pbancMngNo"] = "202406-21411-00"
            
        try:
            # 타임아웃을 15초로 줄이고 여러개 테스트
            response = requests.get(url, params=params, timeout=15)
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                print(f"Response (first 500 chars): {response.text[:500]}")
            else:
                print(f"Error Body: {response.text[:200]}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_endpoints()
