import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 기본 설정
st.set_page_config(page_title="🍎 안동청과 사과 시세 트래커", layout="wide")

st.title("🍎 안동청과 사과 일일 시세 트래커")
st.markdown("매일 업데이트되는 사과 품종별/등급별 가격 동향을 확인하세요.")

# 데이터 불러오기
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('apple_prices.csv')
        # 날짜 컬럼을 datetime 형식으로 변환하여 정렬
        df['날짜'] = pd.to_datetime(df['날짜'], format='%Y년 %m월 %d일')
        df = df.sort_values('날짜')
        
        # 년도와 월 컬럼을 새로 만들어주기 (검색 필터용)
        df['년도'] = df['날짜'].dt.year
        df['월'] = df['날짜'].dt.month
        return df
    except FileNotFoundError:
        return None

df = load_data()

if df is not None and not df.empty:
    # 사이드바 (필터링 옵션)
    st.sidebar.header("검색 옵션 🔍")
    
    # 1. 년도 선택
    years = sorted(df['년도'].unique().tolist(), reverse=True)
    selected_year = st.sidebar.selectbox("📅 년도 선택", years)
    
    year_df = df[df['년도'] == selected_year]
    
    # 2. 월 선택 ('전체' 옵션 추가)
    months = sorted(year_df['월'].unique().tolist())
    month_options = ["전체"] + [f"{m}월" for m in months]
    selected_month_str = st.sidebar.selectbox("📆 월 선택", month_options)
    
    # 월 필터링 적용
    if selected_month_str == "전체":
        month_df = year_df  # 전체를 선택하면 년도 데이터 그대로 사용
        period_text = f"{selected_year}년 전체"
    else:
        # 바로 이 부분입니다! 
        selected_month = int(selected_month_str.replace("월", ""))
        month_df = year_df[year_df['월'] == selected_month]
        period_text = f"{selected_year}년 {selected_month}월"
        
    if month_df.empty:
        st.warning("해당 기간에 데이터가 없습니다.")
    else:
        # 3. 품종 선택
        varieties = month_df['품종'].unique().tolist()
        selected_variety = st.sidebar.selectbox("🍎 품종 선택", varieties)
        
        # 4. 등급 선택
        grades = month_df[month_df['품종'] == selected_variety]['등급'].unique().tolist()
        selected_grade = st.sidebar.selectbox("⭐ 등급 선택", grades)
        
        # 최종 필터링
        filtered_df = month_df[(month_df['품종'] == selected_variety) & (month_df['등급'] == selected_grade)]
        
        st.subheader(f"📈 {selected_variety} ({selected_grade}) 가격 추이 - [{period_text}]")
        
        if not filtered_df.empty:
            # Plotly를 이용한 상호작용형 그래프 그리기
            fig = px.line(filtered_df, x='날짜', y=['최고가', '평균단가', '최저가'], 
                          markers=True, 
                          title=f"{selected_variety} - {selected_grade} 시세 변동",
                          labels={'value': '가격(원)', 'variable': '구분'})
            
            # 그래프 X축(날짜) 보기 좋게 다듬기
            fig.update_xaxes(dtick="D1", tickformat="%m-%d")
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 하단에 데이터 표 보여주기
            st.subheader("📋 상세 데이터")
            display_df = filtered_df.copy()
            display_df['날짜'] = display_df['날짜'].dt.strftime('%Y-%m-%d')
            
            # 숫자에 콤마 찍기
            for col in ['최고가', '최저가', '평균단가']:
                display_df[col] = display_df[col].apply(lambda x: f"{int(x):,}")
                
            st.dataframe(display_df[['날짜', '품종', '등급', '최고가', '최저가', '평균단가']], use_container_width=True)
        else:
            st.warning("해당 조건의 데이터가 없습니다.")
        
else:
    st.info("데이터 파일(apple_prices.csv)이 없습니다. 먼저 크롤러를 실행해 데이터를 수집해주세요.")