from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Finnhub API Key (무료)
FINNHUB_API_KEY = "your_api_key_here"  # https://finnhub.io에서 무료 가입 후 복사

# 한국 상장기업 (국내 데이터 - Finnhub도 지원)
STOCKS = {
    '삼성전자': 'SSNLF',
    'SK하이닉스': 'HXSCF',
    'LG전자': 'LGECY',
    'NAVER': 'NAVER',
    'Kakao': 'KAKOF',
}

def get_finnhub_data(symbol):
    """Finnhub에서 실시간 주식 데이터"""
    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if 'c' not in data:
            return None
        
        return {
            'price': data.get('c', 0),
            'open': data.get('o', 0),
            'high': data.get('h', 0),
            'low': data.get('l', 0),
            'volume': data.get('v', 0),
            'timestamp': data.get('t', 0)
        }
    except:
        return None

@app.get("/", response_class=HTMLResponse)
async def root():
    stocks_json = json.dumps(STOCKS)
    
    return f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DART Pro Max - 실제 데이터</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header-card {{
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            margin-bottom: 30px;
        }}
        .header h1 {{ font-size: 36px; color: #333; margin-bottom: 10px; }}
        .header p {{ color: #666; font-size: 15px; }}
        .search-box {{
            display: flex;
            gap: 12px;
            margin-top: 30px;
        }}
        .search-box input {{
            flex: 1;
            padding: 14px 18px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
        }}
        .search-box button {{
            padding: 14px 40px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
        }}
        .quick-buttons {{
            display: flex;
            gap: 12px;
            margin-top: 20px;
            flex-wrap: wrap;
        }}
        .quick-btn {{
            padding: 10px 20px;
            background: #f0f0f0;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            cursor: pointer;
        }}
        .quick-btn:hover {{ background: #667eea; color: white; border-color: #667eea; }}
        .content {{
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
        }}
        .data-card {{
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            padding: 30px;
        }}
        .price {{ font-size: 48px; font-weight: 700; color: #667eea; }}
        .metric {{ display: inline-block; margin-right: 40px; margin-top: 20px; }}
        .metric-label {{ color: #888; font-size: 12px; text-transform: uppercase; }}
        .metric-value {{ font-size: 24px; font-weight: 700; }}
        .loading {{ text-align: center; padding: 60px 20px; }}
        .spinner {{
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }}
        @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header-card">
            <div class="header">
                <h1>📊 DART Pro Max</h1>
                <p>🔴 Finnhub 실제 주식 데이터 연동</p>
            </div>
            <div class="search-box">
                <input type="text" id="search-input" placeholder="회사명 검색" onkeypress="if(event.key==='Enter') search()">
                <button onclick="search()">검색</button>
            </div>
            <div class="quick-buttons">
                <button class="quick-btn" onclick="quickSearch('삼성전자')">삼성전자</button>
                <button class="quick-btn" onclick="quickSearch('SK하이닉스')">SK하이닉스</button>
                <button class="quick-btn" onclick="quickSearch('LG전자')">LG전자</button>
                <button class="quick-btn" onclick="quickSearch('NAVER')">NAVER</button>
            </div>
        </div>

        <div id="result"></div>
    </div>

    <script>
        const stocks = {stocks_json};

        function search() {{
            const name = document.getElementById('search-input').value.trim();
            if (!name) {{ alert('회사명을 입력하세요'); return; }}
            loadStock(name);
        }}

        function quickSearch(name) {{
            document.getElementById('search-input').value = name;
            loadStock(name);
        }}

        async function loadStock(name) {{
            if (!stocks[name]) {{
                document.getElementById('result').innerHTML = '<div class="content" style="color: red;">회사를 찾을 수 없습니다</div>';
                return;
            }}

            document.getElementById('result').innerHTML = '<div class="loading"><div class="spinner"></div><p>Finnhub에서 실시간 데이터 불러오는 중...</p></div>';

            try {{
                const symbol = stocks[name];
                const response = await fetch(`/api/stock/${{symbol}}`);
                const data = await response.json();

                if (!data || data.price === 0) {{
                    document.getElementById('result').innerHTML = '<div class="content" style="color: red;">데이터를 불러올 수 없습니다. API 키를 확인하세요.</div>';
                    return;
                }}

                let html = `
                <div class="content">
                    <h2>${{name}}</h2>
                    <div class="price">${{data.price ? '$' + data.price.toFixed(2) : 'N/A'}}</div>
                    
                    <div class="metric">
                        <div class="metric-label">오늘의 고가</div>
                        <div class="metric-value">${{data.high ? '$' + data.high.toFixed(2) : 'N/A'}}</div>
                    </div>
                    
                    <div class="metric">
                        <div class="metric-label">오늘의 저가</div>
                        <div class="metric-value">${{data.low ? '$' + data.low.toFixed(2) : 'N/A'}}</div>
                    </div>
                    
                    <div class="metric">
                        <div class="metric-label">거래량</div>
                        <div class="metric-value">${{data.volume ? data.volume.toLocaleString() : 'N/A'}}</div>
                    </div>
                    
                    <p style="color: #888; margin-top: 30px; font-size: 13px;">
                        ⏰ 마지막 업데이트: ${{new Date(data.timestamp * 1000).toLocaleString('ko-KR')}}
                    </p>
                </div>
                `;

                document.getElementById('result').innerHTML = html;
            }} catch (error) {{
                document.getElementById('result').innerHTML = '<div class="content" style="color: red;">❌ 데이터를 불러올 수 없습니다</div>';
            }}
        }}

        document.getElementById('result').innerHTML = '<div style="text-align:center;padding:60px;color:#666;">회사명을 입력하고 검색 버튼을 눌러주세요</div>';
    </script>
</body>
</html>
    """

@app.get("/api/stock/{symbol}")
async def get_stock(symbol: str):
    """Finnhub에서 주식 데이터 조회"""
    data = get_finnhub_data(symbol)
    
    if not data:
        return {"error": "데이터를 불러올 수 없습니다"}
    
    return data

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 DART Pro Max - Finnhub 실제 데이터 버전")
    print("="*60)
    print("\n📊 https://finnhub.io 에서 무료 API KEY 받기")
    print("🌐 브라우저: http://localhost:8000")
    print("✅ 준비 완료!\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
