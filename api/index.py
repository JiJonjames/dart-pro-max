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
    '삼성전자': {'symbol': 'SSNLF', 'code': '005930'},
    'SK하이닉스': {'symbol': 'HXSCF', 'code': '000660'},
    'LG전자': {'symbol': 'LGECY', 'code': '066570'},
    'NAVER': {'symbol': 'NAVER', 'code': '035420'},
    'Kakao': {'symbol': 'KAKOF', 'code': '035720'},
}

def get_financial_statements(code):
    """한국 기업 재무제표 데이터"""
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
        },
        '000660': {
            'company': 'SK하이닉스',
            'income_statement': [
                {'period': '2024년', 'revenue': 95000, 'operating_profit': 8500, 'net_income': 7500},
                {'period': '2023년', 'revenue': 92000, 'operating_profit': 7000, 'net_income': 6000},
                {'period': '2022년', 'revenue': 88000, 'operating_profit': 5000, 'net_income': 3500},
            ],
            'balance_sheet': [
                {'period': '2024년', 'assets': 150000, 'liabilities': 90000, 'equity': 60000},
                {'period': '2023년', 'assets': 140000, 'liabilities': 85000, 'equity': 55000},
                {'period': '2022년', 'assets': 130000, 'liabilities': 80000, 'equity': 50000},
            ],
            'cash_flow': [
                {'period': '2024년', 'operating': 12000, 'investing': -8000, 'financing': -2000},
                {'period': '2023년', 'operating': 10000, 'investing': -7000, 'financing': -1500},
                {'period': '2022년', 'operating': 8000, 'investing': -6000, 'financing': -1000},
            ]
        },
        '035420': {
            'company': 'NAVER',
            'income_statement': [
                {'period': '2024년', 'revenue': 45000, 'operating_profit': 6700, 'net_income': 5200},
                {'period': '2023년', 'revenue': 42000, 'operating_profit': 6200, 'net_income': 4800},
                {'period': '2022년', 'revenue': 38000, 'operating_profit': 5800, 'net_income': 4500},
            ],
            'balance_sheet': [
                {'period': '2024년', 'assets': 85000, 'liabilities': 25000, 'equity': 60000},
                {'period': '2023년', 'assets': 80000, 'liabilities': 22000, 'equity': 58000},
                {'period': '2022년', 'assets': 75000, 'liabilities': 20000, 'equity': 55000},
            ],
            'cash_flow': [
                {'period': '2024년', 'operating': 8500, 'investing': -3000, 'financing': -1500},
                {'period': '2023년', 'operating': 8000, 'investing': -2800, 'financing': -1200},
                {'period': '2022년', 'operating': 7500, 'investing': -2500, 'financing': -1000},
            ]
        }
    }
    
    return statements.get(code)

def calculate_ratios(statements):
    """재무비율 계산"""
    if not statements:
        return None
    
    latest_income = statements['income_statement'][0]
    latest_balance = statements['balance_sheet'][0]
    latest_cash = statements['cash_flow'][0]
    
    revenue = latest_income['revenue']
    net_income = latest_income['net_income']
    assets = latest_balance['assets']
    equity = latest_balance['equity']
    operating_cf = latest_cash['operating']
    
    ratios = {
        'profit_margin': (net_income / revenue * 100) if revenue > 0 else 0,
        'roe': (net_income / equity * 100) if equity > 0 else 0,
        'roa': (net_income / assets * 100) if assets > 0 else 0,
        'debt_ratio': (latest_balance['liabilities'] / assets * 100) if assets > 0 else 0,
        'current_ratio': (assets / latest_balance['liabilities'] * 100) if latest_balance['liabilities'] > 0 else 0,
        'operating_cf_to_net_income': (operating_cf / net_income * 100) if net_income > 0 else 0,
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
    <title>DART Pro Max - 재무제표 분석</title>
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
        .tabs {{
            display: flex;
            gap: 10px;
            margin-top: 30px;
            flex-wrap: wrap;
        }}
        .tab-btn {{
            padding: 12px 24px;
            background: #f0f0f0;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
        }}
        .tab-btn.active {{
            background: #667eea;
            color: white;
            border-color: #667eea;
        }}
        .search-box {{
            display: flex;
            gap: 12px;
            margin-top: 20px;
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
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
        .table-section {{
            margin-bottom: 40px;
        }}
        .table-section h3 {{
            font-size: 20px;
            margin-bottom: 20px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .financial-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}
        .financial-table th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        .financial-table td {{
            padding: 12px;
            border-bottom: 1px solid #e0e0e0;
        }}
        .financial-table tr:hover {{ background: #f8f9fa; }}
        .ratio-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .ratio-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid #667eea;
        }}
        .ratio-label {{ color: #888; font-size: 12px; text-transform: uppercase; margin-bottom: 10px; }}
        .ratio-value {{ font-size: 28px; font-weight: 700; color: #667eea; }}
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
                <p>재무제표 상세 분석</p>
            </div>
            
            <div class="tabs">
                <button class="tab-btn active" data-tab="overview">📈 개요</button>
                <button class="tab-btn" data-tab="income">💰 손익계산서</button>
                <button class="tab-btn" data-tab="balance">🏦 대차대조표</button>
                <button class="tab-btn" data-tab="cashflow">💵 현금흐름</button>
                <button class="tab-btn" data-tab="ratios">📊 재무비율</button>
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

        function switchTab(tabName) {{
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            
            document.getElementById(tabName + '-content').classList.add('active');
            event.target.classList.add('active');
        }}

        document.querySelectorAll('.tab-btn').forEach(btn => {{
            btn.addEventListener('click', function() {{
                const tabName = this.getAttribute('data-tab');
                switchTab(tabName);
            }});
        }});

        function search() {{
            const name = document.getElementById('search-input').value.trim();
            if (!name) {{ alert('회사명을 입력하세요'); return; }}
            loadCompany(name);
        }}

        function quickSearch(name) {{
            document.getElementById('search-input').value = name;
            loadCompany(name);
        }}

        async function loadCompany(name) {{
            if (!stocks[name]) {{
                document.getElementById('result').innerHTML = '<div class="content" style="color: red;">회사를 찾을 수 없습니다</div>';
                return;
            }}

            document.getElementById('result').innerHTML = '<div class="loading"><div class="spinner"></div><p>재무제표 분석 중...</p></div>';

            try {{
                const code = stocks[name].code;
                const response = await fetch(`/api/financial/${{code}}`);
                const data = await response.json();

                if (!data) {{
                    document.getElementById('result').innerHTML = '<div class="content" style="color: red;">데이터를 불러올 수 없습니다</div>';
                    return;
                }}

                renderFinancialAnalysis(name, data);
            }} catch (error) {{
                document.getElementById('result').innerHTML = '<div class="content" style="color: red;">❌ 분석에 실패했습니다</div>';
            }}
        }}

        function renderFinancialAnalysis(name, data) {{
            let html = `
            <div class="content">
                <h2>${{name}} - 재무제표 분석</h2>
                
                <div id="overview-content" class="tab-content active">
                    <div class="ratio-grid">
                        <div class="ratio-card">
                            <div class="ratio-label">순이익률</div>
                            <div class="ratio-value">${{data.ratios.profit_margin.toFixed(2)}}%</div>
                        </div>
                        <div class="ratio-card">
                            <div class="ratio-label">ROE</div>
                            <div class="ratio-value">${{data.ratios.roe.toFixed(2)}}%</div>
                        </div>
                        <div class="ratio-card">
                            <div class="ratio-label">ROA</div>
                            <div class="ratio-value">${{data.ratios.roa.toFixed(2)}}%</div>
                        </div>
                        <div class="ratio-card">
                            <div class="ratio-label">부채비율</div>
                            <div class="ratio-value">${{data.ratios.debt_ratio.toFixed(2)}}%</div>
                        </div>
                    </div>
                </div>

                <div id="income-content" class="tab-content">
                    <div class="table-section">
                        <h3>📈 손익계산서 (단위: 십억원)</h3>
                        <table class="financial-table">
                            <thead>
                                <tr>
                                    <th>기간</th>
                                    <th>매출액</th>
                                    <th>영업이익</th>
                                    <th>순이익</th>
                                </tr>
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

                <div id="balance-content" class="tab-content">
                    <div class="table-section">
                        <h3>🏦 대차대조표 (단위: 십억원)</h3>
                        <table class="financial-table">
                            <thead>
                                <tr>
                                    <th>기간</th>
                                    <th>자산</th>
                                    <th>부채</th>
                                    <th>자본</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${{data.statements.balance_sheet.map(row => `
                                <tr>
                                    <td><strong>${{row.period}}</strong></td>
                                    <td>${{row.assets.toLocaleString()}}</td>
                                    <td>${{row.liabilities.toLocaleString()}}</td>
                                    <td>${{row.equity.toLocaleString()}}</td>
                                </tr>
                                `).join('')}}
                            </tbody>
                        </table>
                    </div>
                </div>

                <div id="cashflow-content" class="tab-content">
                    <div class="table-section">
                        <h3>💵 현금흐름표 (단위: 십억원)</h3>
                        <table class="financial-table">
                            <thead>
                                <tr>
                                    <th>기간</th>
                                    <th>영업활동</th>
                                    <th>투자활동</th>
                                    <th>재무활동</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${{data.statements.cash_flow.map(row => `
                                <tr>
                                    <td><strong>${{row.period}}</strong></td>
                                    <td style="color: #4CAF50;">${{row.operating.toLocaleString()}}</td>
                                    <td style="color: #f44336;">${{{row.investing.toLocaleString()}}</td>
                                    <td>${{{row.financing.toLocaleString()}}</td>
                                </tr>
                                `).join('')}}
                            </tbody>
                        </table>
                    </div>
                </div>

                <div id="ratios-content" class="tab-content">
                    <div class="ratio-grid">
                        <div class="ratio-card">
                            <div class="ratio-label">현금흐름배수</div>
                            <div class="ratio-value">${{{data.ratios.operating_cf_to_net_income.toFixed(2)}}}%</div>
                        </div>
                        <div class="ratio-card">
                            <div class="ratio-label">유동비율</div>
                            <div class="ratio-value">${{{data.ratios.current_ratio.toFixed(2)}}}%</div>
                        </div>
                    </div>
                </div>
            </div>
            `;
            
            document.getElementById('result').innerHTML = html;
        }}

        document.getElementById('result').innerHTML = '<div style="text-align:center;padding:60px;color:#666;">회사명을 입력하고 검색 버튼을 눌러주세요</div>';
    </script>
</body>
</html>
    """

@app.get("/api/financial/{code}")
async def get_financial(code: str):
    statements = get_financial_statements(code)
    
    if not statements:
        return {"error": "데이터를 찾을 수 없습니다"}
    
    ratios = calculate_ratios(statements)
    
    return {
        'statements': statements,
        'ratios': ratios
    }

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 DART Pro Max - 재무제표 분석")
    print("="*60)
    print("\n📊 http://localhost:8000")
    print("✅ 준비 완료!\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
