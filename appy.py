import streamlit as st
import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt

# KRX ETF 정보 데이터 불러오기
def load_krx_etf_data():
    url = "http://data.krx.co.kr/comm/fileDn/downloadExcel.do?key=3BDD2F5006134A0E81FEF61721358426AFFB1DFC"  # 실제 KRX API 또는 데이터 파일 URL 입력
    df = pd.read_excel(url)
    return df

def get_etf_info_from_krx(df, etf_name):
    """
    KRX 데이터에서 특정 ETF 정보를 검색하는 함수
    """
    etf_data = df[df["ETF명"].str.contains(etf_name, na=False)]
    if etf_data.empty:
        return None
    return etf_data.iloc[0]

def fetch_etf_market_data(etf_code):
    """
    ETF 시장 데이터 (총 자산, 총 발행 주식 수, 시장 가격) 가져오기
    """
    api_url = f"https://api.example.com/etf/{etf_bydd_trd}"  # 실제 API 엔드포인트 입력
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    return None

def fetch_etf_historical_returns(etf_code):
    """
    ETF의 과거 수익률 데이터 가져오기
    """
    api_url = f"https://api.example.com/etf/etf_bydd_trd/returns"  # 실제 API 엔드포인트 입력
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    return None

def calculate_nav(total_assets, total_shares):
    return total_assets / total_shares

def calculate_premium_discount(etf_price, nav):
    return ((etf_price - nav) / nav) * 100

def calculate_tracking_error(etf_returns, benchmark_returns):
    differences = np.array(etf_returns) - np.array(benchmark_returns)
    return np.std(differences)

# Streamlit UI
st.title("ETF 정보 검색기")

etf_names = st.text_input("ETF 이름을 입력하세요 (여러 개 입력 시 쉼표로 구분):")

if etf_names:
    with st.spinner("ETF 정보를 불러오는 중..."):
        df = load_krx_etf_data()
        etf_list = [name.strip() for name in etf_names.split(",")][:3]  # 최대 3개 ETF 지원
        
        for etf_name in etf_list:
            etf_info = get_etf_info_from_krx(df, etf_name)
            
            if etf_info is not None:
                etf_code = etf_info.get("ETF 코드", "")  # ETF 코드가 필요한 경우 사용
                market_data = fetch_etf_market_data(etf_code)
                historical_returns = fetch_etf_historical_returns(etf_code)
                
                if market_data:
                    total_assets = market_data.get("total_assets", 0)
                    total_shares = market_data.get("total_shares", 1)
                    etf_price = market_data.get("market_price", 0)
                else:
                    total_assets = total_shares = etf_price = 0
                
                st.write(f"## {etf_name} ETF 정보")
                st.write(f"**유형:** {etf_info.get('유형', '정보 없음')}")
                st.write(f"**펀드보수:** {etf_info.get('펀드보수', '정보 없음')}%")
                st.write(f"**자산운용사:** {etf_info.get('자산운용사', '정보 없음')}")
                
                if "PDF 링크" in etf_info:
                    st.write(f"[ETF 운용사 PDF 보기]({etf_info['PDF 링크']})")
                
                st.write("### 추가 정보")
                st.write(f"**총 자산:** {total_assets:,.2f} 원")
                st.write(f"**총 발행 주식 수:** {total_shares:,} 주")
                st.write(f"**ETF 시장 가격:** {etf_price:,.2f} 원")
                
                if total_assets and total_shares:
                    nav = calculate_nav(total_assets, total_shares)
                    st.write(f"**NAV:** {nav:.2f} 원")
                    
                    if etf_price:
                        premium_discount = calculate_premium_discount(etf_price, nav)
                        st.write(f"**괴리율:** {premium_discount:.2f}%")
                
                if historical_returns:
                    st.write("### 과거 수익률")
                    st.write(f"**1년 수익률:** {historical_returns.get('1y', '정보 없음')}%")
                    st.write(f"**5년 수익률:** {historical_returns.get('5y', '정보 없음')}%")
                    st.write(f"**10년 수익률:** {historical_returns.get('10y', '정보 없음')}%")
                    
                    # 그래프 표시
                    st.write("#### 수익률 그래프")
                    years = ["1년", "5년", "10년"]
                    returns = [historical_returns.get('1y', 0), historical_returns.get('5y', 0), historical_returns.get('10y', 0)]
                    fig, ax = plt.subplots()
                    ax.bar(years, returns, color=['blue', 'green', 'red'])
                    ax.set_ylabel("수익률 (%)")
                    st.pyplot(fig)
                    
                    # 더보기 기능
                    if st.button(f"{etf_name} 수익률 더보기"):
                        st.write(historical_returns)
            else:
                st.warning(f"{etf_name} ETF 정보를 찾을 수 없습니다.")
else:
    st.warning("ETF 이름을 입력하세요.")
