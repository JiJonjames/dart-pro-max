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

FINNHUB_API_KEY = "your_api_key_here"

STOCKS = {
    '삼성전자': 'SSNLF',
    'SK하이닉스': 'HXSCF',
    'LG전자': 'LGECY',
    'NAVER': 'NAVER',
    'Kakao': 'KAKOF',
}

def get_finnhub_data(symbol):
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

def analyze_company(symbol, price_data):
    """기업 성격 AI 분석"""
    if not price_data or price_data.get('price', 0) == 0:
        return None
    
    # 시뮬레이션 데이터 (실제로는 Finnhub Pro 데이터 사용)
    analysis = {
        'type': '',
        'rating': 0,
        'traits': [],
        'risk': '',
        'recommendation': '',
        'details': {}
    }
    
    # 예시 데이터로 분석
    if symbol in ['SSNLF', 'HXSCF']:  # 반도체
        analysis['type'] = '🚀 성장주'
        analysis['traits'] = ['높은 기술력', '글로벌 수요', '높은 부가가치']
        analysis['rating'] = 4.5
        analysis['risk'] = '🟡 중간'
        analysis['recommendation'] = '장기 보유 추천'
        analysis['details'] = {
            'growth': '높음',
            'profitability': '우수',
            'stability': '보통',
            'dividend': '낮음'
        }
    
    elif symbol == 'NAVER':  # IT/인터넷
        analysis['type'] = '💡 기술주'
        analysis['traits'] = ['높은 혁신성', '플랫폼 비즈니스', '구독형 수익']
        analysis['rating'] = 4
        analysis['risk'] = '🟡 중간'
        analysis['recommendation'] = '성장성 매력'
        analysis['details'] = {
            'growth': '높음',
            'profitability': '우수',
            'stability': '보통',
            'dividend': '낮음'
        }
    
    else:
        analysis['type'] = '📊 분석주'
        analysis['traits'] = ['추가 정보 필요']
        analysis['rating'] = 3
        analysis['risk'] = '🟠 주의'
        analysis['recommendation'] = '추가 조사 필요'
        analysis['details'] = {
            'growth': '보통',
            'profitability': '보통',
            'stability': '보통',
            'dividend': '보통'
        }
    
    return analysis

@app.get("/", response_class=HTMLResponse)
async def root():
    stocks_json = json.dumps(STOCKS)
    
    return f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DART Pro Max - AI 기업 분석</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
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
        .company-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }}
        @media (max-width: 1024px) {{
            .company-grid {{ grid-template-columns: 1fr; }}
        }}
        .card {{
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            padding: 25px;
        }}
        .price {{ font-size: 48px; font-weight: 700; color: #667eea; margin: 20px 0; }}
        .company-type {{
            font-size: 24px;
            font-weight: 700;
            margin: 20px 0;
            padding: 15px;
            background: #f0f0f0;
            border-radius: 8px;
        }}
        .rating {{
            font-size: 32px;
            margin: 20px 0;
        }}
        .traits {{
            margin: 20px 0;
        }}
        .trait {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            margin: 5px;
            font-size: 13px;
        }}
        .details-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin: 20px 0;
        }}
        .detail-item {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .detail-label {{ color: #888; font-size: 12px; text-transform: uppercase; }}
        .detail-value {{ font-size: 18px; font-weight: 700; margin-top: 5px; }}
        .recommendation {{
            background: #e3f2fd;
            border-left: 5px solid #2196F3;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            font-weight: 600;
            font-size: 16px;
        }}
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
        .risk-badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 8px;
            font-weight: 600;
            margin: 10px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header-card">
            <div class="header">
                <h1>📊 DART Pro Max AI</h1>
                <p>🤖 AI 기반 기업 성격 분석 + 실제 주가 데이터</p>
            </div>
            <div class="search-box">
                <input type="text" id="search-input" placeholder="회사명 검색" onkeypress="if(event.key==='Enter') search()">
                <button onclick="search()">검색</button>
            </div>
            <div class="quick-buttons">
                <button class="quick-btn" onclick="quickSearch('삼성전자')">삼성전자</button>
                <button class="quick-btn" onclick="quickSearch('SK하이닉스')">SK하이닉스</button>
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

            document.getElementById('result').innerHTML = '<div class="loading"><div class="spinner"></div><p>AI 분석 중...</p></div>';

            try {{
                const symbol = stocks[name];
                const response = await fetch(`/api/stock/${{symbol}}`);
                const data = await response.json();

                if (!data || data.price === 0) {{
                    document.getElementById('result').innerHTML = '<div class="content" style="color: red;">데이터를 불러올 수 없습니다</div>';
                    return;
                }}

                let html = `
                <div class="content">
                    <div class="company-grid">
                        <div class="card">
                            <h2>${{name}}</h2>
                            <div class="price">${{data.price ? '$' + data.price.toFixed(2) : 'N/A'}}</div>
                            
                            <div style="display: flex; gap: 10px;">
                                <div style="flex: 1;">
                                    <div class="detail-label">고가</div>
                                    <div style="font-size: 18px; font-weight: 700;">${{data.high ? '$' + data.high.toFixed(2) : 'N/A'}}</div>
                                </div>
                                <div style="flex: 1;">
                                    <div class="detail-label">저가</div>
                                    <div style="font-size: 18px; font-weight: 700;">${{data.low ? '$' + data.low.toFixed(2) : 'N/A'}}</div>
                                </div>
                            </div>
                        </div>

                        <div class="card">
                            <h3>🤖 AI 분석 결과</h3>
                            <div class="company-type">${{data.analysis.type}}</div>
                            <div class="rating">${{Array(Math.round(data.analysis.rating)).fill('⭐').join('')}}</div>
                            <div class="risk-badge">${{data.analysis.risk}}</div>
                            
                            <h4 style="margin-top: 20px; margin-bottom: 10px;">기업 특성:</h4>
                            <div class="traits">
                                ${{data.analysis.traits.map(t => `<span class="trait">${{t}}</span>`).join('')}}
                            </div>
                        </div>
                    </div>

                    <div class="recommendation">
                        💡 ${{data.analysis.recommendation}}
                    </div>

                    <h3 style="margin-bottom: 20px;">📊 재무 지표 평가</h3>
                    <div class="details-grid">
                        <div class="detail-item">
                            <div class="detail-label">성장성</div>
                            <div class="detail-value">${{data.analysis.details.growth}}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">수익성</div>
                            <div class="detail-value">${{data.analysis.details.profitability}}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">안정성</div>
                            <div class="detail-value">${{data.analysis.details.stability}}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">배당성</div>
                            <div class="detail-value">${{data.analysis.details.dividend}}</div>
                        </div>
                    </div>
                </div>
                `;

                document.getElementById('result').innerHTML = html;
            }} catch (error) {{
                document.getElementById('result').innerHTML = '<div class="content" style="color: red;">❌ 분석에 실패했습니다</div>';
            }}
        }}

        document.getElementById('result').innerHTML = '<div style="text-align:center;padding:60px;color:#666;">회사명을 입력하고 검색 버튼을 눌러주세요</div>';
    </script>
</body>
</html>
    """

@app.get("/api/stock/{symbol}")
async def get_stock(symbol: str):
    data = get_finnhub_data(symbol)
    
    if not data:
        return {"error": "데이터를 불러올 수 없습니다"}
    
    analysis = analyze_company(symbol, data)
    
    return {
        'price': data['price'],
        'high': data['high'],
        'low': data['low'],
        'volume': data['volume'],
        'analysis': analysis
    }

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 DART Pro Max - AI 기업 분석 버전")
    print("="*60)
    print("\n🌐 http://localhost:8000")
    print("🤖 AI 기반 기업 성격 분석")
    print("✅ 준비 완료!\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
