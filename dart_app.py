from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

STOCKS = {
    '삼성전자': {'symbol': 'SSNLF', 'code': '005930'},
    'SK하이닉스': {'symbol': 'HXSCF', 'code': '000660'},
    'LG전자': {'symbol': 'LGECY', 'code': '066570'},
    'NAVER': {'symbol': 'NAVER', 'code': '035420'},
    'Kakao': {'symbol': 'KAKOF', 'code': '035720'},
}

def get_financial_statements(code):
    statements = {
        '005930': {
            'company': '삼성전자',
            'income_statement': [
                {'period': '2024년', 'revenue': 302000, 'operating_profit': 37750, 'net_income': 38200},
                {'period': '2023년', 'revenue': 280000, 'operating_profit': 35000, 'net_income': 36000},
                {'period': '2022년', 'revenue': 268000, 'operating_profit': 32000, 'net_income': 33000},
            ],
            'balance_sheet': [
                {'period': '2024년', 'assets': 450000, 'liabilities': 200000, 'equity': 250000},
                {'period': '2023년', 'assets': 420000, 'liabilities': 180000, 'equity': 240000},
                {'period': '2022년', 'assets': 400000, 'liabilities': 160000, 'equity': 240000},
            ],
            'cash_flow': [
                {'period': '2024년', 'operating': 45000, 'investing': -12000, 'financing': -8000},
                {'period': '2023년', 'operating': 42000, 'investing': -10000, 'financing': -7000},
                {'period': '2022년', 'operating': 38000, 'investing': -9000, 'financing': -6000},
            ]
        }
    }
    return statements.get(code)

def calculate_ratios(statements):
    if not statements:
        return None
    latest_income = statements['income_statement'][0]
    latest_balance = statements['balance_sheet'][0]
    latest_cash = statements['cash_flow'][0]
    
    revenue = latest_income['revenue']
    net_income = latest_income['net_income']
    assets = latest_balance['assets']
    equity = latest_balance['equity']
    
    ratios = {
        'profit_margin': (net_income / revenue * 100) if revenue > 0 else 0,
        'roe': (net_income / equity * 100) if equity > 0 else 0,
        'roa': (net_income / assets * 100) if assets > 0 else 0,
        'debt_ratio': (latest_balance['liabilities'] / assets * 100) if assets > 0 else 0,
    }
    return ratios

@app.get("/", response_class=HTMLResponse)
async def root():
    stocks_json = json.dumps(STOCKS)
    
    return f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DART Pro Max</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: white; border-radius: 16px; padding: 40px; margin-bottom: 30px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }}
        .header h1 {{ font-size: 36px; margin-bottom: 20px; }}
        .search-box {{ display: flex; gap: 12px; margin-top: 20px; }}
        .search-box input {{ flex: 1; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; }}
        .search-box button {{ padding: 12px 30px; background: #667eea; color: white; border: none; border-radius: 8px; cursor: pointer; }}
        .quick-btns {{ display: flex; gap: 10px; margin-top: 15px; flex-wrap: wrap; }}
        .quick-btns button {{ padding: 8px 16px; background: #f0f0f0; border: 2px solid #e0e0e0; border-radius: 8px; cursor: pointer; }}
        .quick-btns button:hover {{ background: #667eea; color: white; }}
        .content {{ background: white; border-radius: 16px; padding: 40px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }}
        .ratio-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 30px; }}
        .ratio-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #667eea; }}
        .ratio-label {{ color: #888; font-size: 12px; text-transform: uppercase; margin-bottom: 10px; }}
        .ratio-value {{ font-size: 28px; font-weight: 700; color: #667eea; }}
        .table-section {{ margin-top: 40px; }}
        .table-section h3 {{ font-size: 20px; margin-bottom: 20px; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        table th {{ background: #667eea; color: white; padding: 12px; text-align: left; }}
        table td {{ padding: 12px; border-bottom: 1px solid #e0e0e0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 DART Pro Max</h1>
            <p>재무제표 분석</p>
            <div class="search-box">
                <input type="text" id="search" placeholder="회사명 검색">
                <button onclick="search()">검색</button>
            </div>
            <div class="quick-btns">
                <button onclick="quickSearch('삼성전자')">삼성전자</button>
                <button onclick="quickSearch('SK하이닉스')">SK하이닉스</button>
                <button onclick="quickSearch('NAVER')">NAVER</button>
            </div>
        </div>
        <div id="result"></div>
    </div>

    <script>
        const stocks = {stocks_json};
        
        function search() {{
            const name = document.getElementById('search').value;
            if (!name) return;
            loadCompany(name);
        }}
        
        function quickSearch(name) {{
            document.getElementById('search').value = name;
            loadCompany(name);
        }}
        
        async function loadCompany(name) {{
            if (!stocks[name]) {{
                document.getElementById('result').innerHTML = '<div class="content" style="color: red;">회사를 찾을 수 없습니다</div>';
                return;
            }}
            
            const code = stocks[name].code;
            try {{
                const res = await fetch(`/api/financial/${{code}}`);
                const data = await res.json();
                
                const latest = data.statements.income_statement[0];
                const ratios = data.ratios;
                
                let html = `
                <div class="content">
                    <h2>${{name}}</h2>
                    <div class="ratio-grid">
                        <div class="ratio-card">
                            <div class="ratio-label">순이익률</div>
                            <div class="ratio-value">${{ratios.profit_margin.toFixed(2)}}%</div>
                        </div>
                        <div class="ratio-card">
                            <div class="ratio-label">ROE</div>
                            <div class="ratio-value">${{ratios.roe.toFixed(2)}}%</div>
                        </div>
                        <div class="ratio-card">
                            <div class="ratio-label">ROA</div>
                            <div class="ratio-value">${{ratios.roa.toFixed(2)}}%</div>
                        </div>
                        <div class="ratio-card">
                            <div class="ratio-label">부채비율</div>
                            <div class="ratio-value">${{ratios.debt_ratio.toFixed(2)}}%</div>
                        </div>
                    </div>
                    
                    <div class="table-section">
                        <h3>손익계산서 (단위: 십억원)</h3>
                        <table>
                            <thead>
                                <tr><th>기간</th><th>매출액</th><th>영업이익</th><th>순이익</th></tr>
                            </thead>
                            <tbody>
                                ${{data.statements.income_statement.map(row => `
                                <tr>
                                    <td><strong>${{row.period}}</strong></td>
                                    <td>${{row.revenue.toLocaleString()}}</td>
                                    <td>${{row.operating_profit.toLocaleString()}}</td>
                                    <td>${{row.net_income.toLocaleString()}}</td>
                                </tr>
                                `).join('')}}
                            </tbody>
                        </table>
                    </div>
                </div>
                `;
                document.getElementById('result').innerHTML = html;
            }} catch (e) {{
                document.getElementById('result').innerHTML = '<div class="content" style="color: red;">에러: ' + e.message + '</div>';
            }}
        }}
    </script>
</body>
</html>
    """

@app.get("/api/financial/{code}")
async def get_financial(code: str):
    statements = get_financial_statements(code)
    if not statements:
        return {"error": "데이터 없음"}
    ratios = calculate_ratios(statements)
    return {'statements': statements, 'ratios': ratios}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
