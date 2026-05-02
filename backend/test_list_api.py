import requests

SERVICE_KEY = "f095a73a6d8ff681e2c7ab78b7488d895a91b64860bf8af230f64cd223257e45"
URL = f"http://apis.data.go.kr/B010003/OnbidMvastListSrvc2/getMvastCltrList2?serviceKey={SERVICE_KEY}"

def test_list_api():
    params = {
        "pageNo": 1,
        "numOfRows": 10,
        "prptDivCd": "0001,0002,0003,0004,0005", # 임의의 코드
        "pvctTrgtYn": "N",
        "onbidCltrNm": "노트북"
    }
    print(f"[*] Testing List API...")
    try:
        response = requests.get(URL, params=params, timeout=20)
        print(f"Status: {response.status_code}")
        print(response.text[:1000])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_list_api()
