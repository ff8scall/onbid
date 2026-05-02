import requests
import json

def test_api():
    service_key = "f095a73a6d8ff681e2c7ab78b7488d895a91b64860bf8af230f64cd223257e45"
    
    # 테스트 1: 사용자가 제공한 공고 상세 API (샘플 번호 사용)
    url_dtl = "https://apis.data.go.kr/B010003/OnbidPbancCltrDtlSrvc2/getPbancCltrInf"
    params = {
        "serviceKey": service_key,
        "pageNo": 1,
        "numOfRows": 10,
        "resultType": "json",
        "pbancMngNo": "202406-21411-00"
    }
    
    print(f"Testing Detail API: {url_dtl}")
    try:
        # requests will automatically encode the serviceKey if passed as a string. 
        # But for public data portal, sometimes we need the raw (already encoded) key.
        # Let's try simple way first.
        response = requests.get(url_dtl, params=params, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
