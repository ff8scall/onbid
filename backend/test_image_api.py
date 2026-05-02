import requests

SERVICE_KEY = "f095a73a6d8ff681e2c7ab78b7488d895a91b64860bf8af230f64cd223257e45"
URL = "https://apis.data.go.kr/B010003/OnbidPbancCltrImgSrvc2/getPbancCltrImgInfor2"

def test_image_api(pbanc_mng_no, cltr_mng_no):
    params = {
        "serviceKey": SERVICE_KEY,
        "pageNo": 1,
        "numOfRows": 10,
        "resultType": "json",
        "pbancMngNo": pbanc_mng_no,
        "cltrMngNo": cltr_mng_no
    }
    
    print(f"[*] Testing Image API for {cltr_mng_no}...")
    try:
        response = requests.get(URL, params=params, timeout=20)
        print(f"Status: {response.status_code}")
        print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # 실제 관리번호 사용
    test_image_api("884045", "2026-0400-021612")
