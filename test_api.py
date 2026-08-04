import requests
import os
from dotenv import load_dotenv

load_dotenv()
DART_API_KEY = os.getenv('DART_API_KEY')

print(f"API KEY: {DART_API_KEY}")

if DART_API_KEY:
    response = requests.get("https://opendart.fss.or.kr/api/corpSearch.json", params={
        'crtfc_key': DART_API_KEY,
        'corp_name': '삼성전자'
    })
    print(f"상태: {response.status_code}")
    print(f"응답: {response.json()}")
else:
    print("KEY 없음!")
