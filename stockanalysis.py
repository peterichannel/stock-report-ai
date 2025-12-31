import streamlit as st
import google.generativeai as genai
import re

# 1. 페이지 설정
st.set_page_config(page_title="AI 주식 분석 리포트", layout="wide")

# 2. 디자인 CSS (글씨 크기 및 스타일 강제 통일)
st.markdown("""
    <style>
    /* 전체 배경 및 기본 폰트 색상 */
    html, body, [data-testid="stAppViewContainer"] { background-color: #0E1117 !important; }
    h1, h2, h3, h4, h5, h6, p, span, div, label, li, .stMarkdown { color: #FFFFFF !important; }
    
    /* 앱 제목 스타일 */
    .title-text { text-align: center; font-size: 3.0rem !important; font-weight: 800; padding-top: 30px; margin-bottom: 20px; }
    
    /* 입력창 및 버튼 스타일 */
    div[data-testid="stTextInput"] input { 
        text-align: center !important; font-size: 1.2rem !important; height: 50px !important;
        background-color: #262730 !important; color: white !important; 
    }
    button[kind="primary"] { 
        width: 100% !important; height: 50px !important; font-size: 1.3rem !important; 
        background-color: #FF4B4B !important; font-weight: bold !important; 
    }
    
    /* --- 리포트 본문 스타일 완벽 고정 --- */
    .report-text h3 {
        color: #4A9EFF !important; font-size: 1.5rem !important; font-weight: 700 !important;
        margin-top: 30px !important; margin-bottom: 15px !important;
        border-bottom: 1px solid #333; padding-bottom: 5px; line-height: 1.4 !important;
    }
    .report-text p, .report-text li {
        font-size: 1.15rem !important; line-height: 1.8 !important; color: #E2E8F0 !important;
        margin-bottom: 8px !important;
    }
    .report-text strong { color: #FFD700 !important; font-weight: 700 !important; }
    .report-text ul { margin-left: 20px !important; padding-left: 0px !important; }
    
    /* 면책 조항 스타일 */
    .disclaimer-box {
        background-color: #1A1C24; border: 1px solid #444; border-radius: 8px;
        padding: 15px; margin-top: 40px; text-align: center;
    }
    .disclaimer-box p, .disclaimer-box strong { font-size: 0.9rem !important; color: #888 !important; }
    
    /* 대기 안내 메시지 박스 스타일 */
    .wait-box {
        background-color: #2D3748; border: 2px solid #F6E05E; border-radius: 10px;
        padding: 30px; text-align: center; margin-top: 20px;
    }
    .wait-box h3 { color: #F6E05E !important; font-size: 1.5rem !important; margin-bottom: 10px !important; }
    .wait-box p { font-size: 1.2rem !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

# 3. 화면 UI
st.markdown('<div class="title-text">AI 주식 분석 리포트 📈</div>', unsafe_allow_html=True)

# API 키 처리 로직
api_key = st.secrets.get("GEMINI_API_KEY", None)

with st.form(key='search_form'):
    if not api_key:
        api_key_input = st.text_input("🔑 Google API Key 입력", type="password")
    
    ticker = st.text_input("ticker_input", placeholder="종목명 입력 후 엔터 (예: 삼성전자, 테슬라)", label_visibility="collapsed")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_button = st.form_submit_button("🔍 분석 시작", type="primary", use_container_width=True)

# 4. 분석 로직
if analyze_button:
    if not api_key and 'api_key_input' in locals():
        api_key = api_key_input

    if not api_key:
        st.warning("⚠️ API 키가 필요합니다.")
        st.stop()

    if ticker:
        try:
            genai.configure(api_key=api_key)
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            target_model = next((m for m in available_models if 'flash' in m), available_models[0])
            model = genai.GenerativeModel(target_model)
            
            with st.spinner(f"🤖 AI가 {ticker} 핵심 요약 리포트를 작성 중입니다..."):
                prompt = f"""
                주식 애널리스트로서 '{ticker}'에 대한 '1페이지 핵심 요약 보고서'를 작성하라.
                
                **[디자인 및 형식 규칙 - 엄수]**
                1. **목차 제목:** 모든 12개 목차 앞에는 반드시 '### ' (헤더3)를 붙여라. 
                2. **본문:** 무조건 '불렛 포인트(•)' 리스트로 작성하라.
                3. **어조:** "~함", "~임" 체로 간결하게.
                
                **[필수 목차 (12개)]**
                1. 기업 개요
                2. CEO
                3. 주주 구성
                4. 사업 비중
                5. 산업 전망
                6. 경쟁 구도
                7. 경제적 해자
                8. 리스크 요인
                9. 재무 현황
                10. 밸류에이션 (가격 수치 제외)
                11. 기술적 분석 (가격 수치 제외)
                12. 최종 결론
                """

                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.5,
                        max_output_tokens=8192, 
                    )
                )
                
                final_text = response.text
                final_text = re.sub(r"(### \d+\..+?)(\s+\*)", r"\1\n\n*", final_text)

                st.markdown("---")
                st.markdown(f"## 📊 {ticker} 핵심 투자 요약")
                st.markdown(f'<div class="report-text">{final_text}</div>', unsafe_allow_html=True)
                
                st.markdown("""
                    <div class="disclaimer-box">
                        <p>⚠️ <strong>투자 유의사항</strong><br>
                        이 리포트는 AI가 학습된 데이터를 바탕으로 생성하므로, 실시간 정보와 차이가 있을 수 있습니다.<br>
                        <strong>투자의 책임은 전적으로 본인에게 있습니다.</strong></p>
                    </div>
                """, unsafe_allow_html=True)

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg:
                st.markdown("""
                    <div class="wait-box">
                        <h3>🚦 접속자가 많아 분석이 지연되고 있습니다!</h3>
                        <p>현재 너무 많은 요청이 몰려 AI가 잠시 숨을 고르고 있습니다.<br>
                        <strong>약 1분 뒤에 다시 시도해 주시면 감사하겠습니다. 🙏</strong></p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.error(f"❌ 에러 발생: {error_msg}")

    elif not ticker:
        st.warning("⚠️ 종목명을 입력해주세요.")
