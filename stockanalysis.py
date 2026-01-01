import streamlit as st
import google.generativeai as genai
import re
import textwrap

# 1. 페이지 설정
st.set_page_config(page_title="AI 종목 분석기", page_icon="📈", layout="wide")

# 2. CSS 스타일 (왼쪽 벽에 밀착)
st.markdown(textwrap.dedent("""
    <style>
    .stApp { background-color: #020617 !important; }
    h1, h2, h3, h4, h5, h6, p, div, span, label, .stMarkdown { color: #f1f5f9 !important; font-family: sans-serif !important; }
    
    /* 네비게이션 바 */
    .navbar { display: flex; align-items: center; padding: 1rem 0; border-bottom: 1px solid #1e293b; margin-bottom: 3rem; }
    .nav-logo { width: 36px; height: 36px; background: linear-gradient(to bottom, #334155, #0f172a); border: 1px solid #475569; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 800; color: white; margin-right: 1rem; cursor: pointer; text-decoration: none; }
    .nav-title { font-size: 1.125rem; font-weight: 500; color: #94a3b8; border-left: 1px solid #334155; padding-left: 1rem; cursor: pointer; }
    
    /* 검색창 & 버튼 */
    div[data-testid="stTextInput"] input { background-color: #0f172a !important; border: 1px solid #334155 !important; color: white !important; border-radius: 0.75rem !important; height: 3.5rem !important; }
    div[data-testid="stFormSubmitButton"] button { background-color: #2563eb !important; color: white !important; border: none !important; border-radius: 0.5rem !important; height: 3.5rem !important; width: 100% !important; }
    
    /* 뉴스레터 카드 (수정됨) */
    .newsletter-card { background-color: #0f172a; border: 1px solid #1e293b; border-radius: 1rem; padding: 1.25rem; display: flex; align-items: center; gap: 1.25rem; text-decoration: none !important; margin-top: 2rem; }
    .newsletter-card:hover { background-color: #1e293b; border-color: #334155; }
    
    /* 로고 & 텍스트 스타일 */
    .logo-m { width: 4rem; height: 4rem; background-color: #355e3b; border-radius: 0.75rem; display: flex; align-items: center; justify-content: center; font-family: serif; font-size: 2.25rem; color: white; font-style: italic; flex-shrink: 0; }
    
    /* 🚨 핵심 수정: 제목 줄바꿈 금지 (nowrap) 추가 */
    .card-text h3 { margin: 0; font-size: 1.125rem; font-weight: 700; color: #e2e8f0; white-space: nowrap; }
    .card-text p { margin: 0; font-size: 0.875rem; color: #64748b; margin-top: 0.25rem; }

    /* 리포트 본문 스타일 */
    .report-content h3 { color: #60a5fa !important; margin-top: 2.5rem !important; border-bottom: 1px solid #1e293b; }
    
    /* 헤더/푸터 숨김 */
    header, footer { visibility: hidden; }
    </style>
"""), unsafe_allow_html=True)

# 3. 상태 관리
if 'page_state' not in st.session_state: st.session_state.page_state = 'home'
if 'report_data' not in st.session_state: st.session_state.report_data = ""
if 'current_ticker' not in st.session_state: st.session_state.current_ticker = ""

# 4. 네비게이션 바
st.markdown(textwrap.dedent("""
    <div class="navbar">
        <a href="https://litt.ly/peterich" target="_blank" class="nav-logo">주피터</a>
        <div class="nav-title" onclick="window.location.reload()">AI 종목 분석기</div>
    </div>
"""), unsafe_allow_html=True)

# --- 분석 함수 ---
def run_analysis(ticker_name):
    api_key = st.secrets.get("GEMINI_API_KEY", None)
    if not api_key: return "ERROR_KEY"
    try:
        genai.configure(api_key=api_key)
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        model_name = next((m for m in models if 'flash' in m), 'models/gemini-pro')
        model = genai.GenerativeModel(model_name)
        prompt = f"주식 애널리스트로서 '{ticker_name}'에 대한 핵심 요약 보고서를 작성하라. 목차는 '### '사용, 본문은 불렛포인트 사용. 필수목차: 1.기업개요 2.CEO 3.주주구성 4.사업비중 5.산업전망 6.경쟁구도 7.경제적해자 8.리스크 9.재무현황 10.밸류에이션 11.기술적분석 12.최종결론"
        response = model.generate_content(prompt)
        return re.sub(r"(### \d+\..+?)(\s+\*)", r"\1\n\n*", response.text)
    except Exception as e:
        return "ERROR_429" if "429" in str(e) else f"ERROR: {str(e)}"

# --- 메인 화면 ---
if st.session_state.page_state == 'home':
    _, col_center, _ = st.columns([1, 6, 1])
    with col_center:
        st.markdown(textwrap.dedent("""
            <h1 style='text-align: center; font-size: 3.5rem; font-weight: 800; margin-bottom: 0.5rem;'>
                주식 분석을 <br><span style='color: #3b82f6;'>단 몇 초 만에</span>
            </h1>
            <p style='text-align: center; color: #94a3b8; font-size: 1.2rem; margin-bottom: 3rem;'>
                종목명을 입력하면 종합 투자 보고서를 AI가 즉시 생성합니다.
            </p>
        """), unsafe_allow_html=True)
        
        with st.form("search_form"):
            c1, c2 = st.columns([3, 1])
            with c1: ticker_input = st.text_input("ticker", placeholder="예: 테슬라", label_visibility="collapsed")
            with c2: submit = st.form_submit_button("🔍 분석 시작")
        
        if submit and ticker_input:
            st.session_state.current_ticker = ticker_input
            with st.spinner("분석 중..."):
                res = run_analysis(ticker_input)
                if res.startswith("ERROR"): st.error(res)
                else:
                    st.session_state.report_data = res
                    st.session_state.page_state = 'report'
                    st.rerun()

        st.markdown(textwrap.dedent("""
            <div style='display: flex; justify-content: center; gap: 10px; margin-top: 20px; color: #64748b;'>
                <span>추천: 삼성전자</span><span>추천: 테슬라</span><span>추천: 엔비디아</span>
            </div>
        """), unsafe_allow_html=True)

        # 🚨 핵심 수정: max-width를 400px -> 600px로 변경하여 공간 확보
        st.markdown(textwrap.dedent("""
            <div style='margin-top: 6rem; text-align: center;'>
                <a href="https://litt.ly/peterich" target="_blank" style="text-decoration: none;">
                    <div style='width: 100px; height: 100px; background: linear-gradient(to bottom, #1e293b, #000); border-radius: 30px; margin: 0 auto 20px auto; border: 1px solid #334155; display: flex; align-items: center; justify-content: center;'>
                        <span style='font-size: 1.5rem; font-weight: 800; color: white;'>주피터</span>
                    </div>
                </a>
                <h2 style='font-size: 1.5rem; margin-bottom: 0.5rem;'>주식하는 피터</h2>
                <p style='color: #94a3b8; line-height: 1.6;'>
                    불안함이 확신이 될 수 있도록<br>연 20% 수익의 현실적인 '생존투자'<br>주식 초보만을 위한 무료 뉴스레터 구독 👇
                </p>
                <a href="https://tally.so/r/GxKGXe" target="_blank" class="newsletter-card" style='max-width: 600px; margin: 2rem auto 0 auto;'>
                    <div class="logo-m">m</div>
                    <div class="card-text" style='text-align: left;'>
                        <h3>주식하는 피터의 뉴스레터</h3>
                        <p>(매주 월요일 새벽 발송)</p>
                    </div>
                </a>
            </div>
        """), unsafe_allow_html=True)

# --- 리포트 화면 ---
elif st.session_state.page_state == 'report':
    if st.button("← 돌아가기"):
        st.session_state.page_state = 'home'
        st.rerun()
    st.markdown(f"# 📊 {st.session_state.current_ticker} 분석 리포트")
    st.markdown("---")
    st.markdown(textwrap.dedent(f"""<div class="report-content">{st.session_state.report_data}</div>"""), unsafe_allow_html=True)
    st.markdown(textwrap.dedent("""<div style='background-color: #1e293b; padding: 20px; border-radius: 10px; margin-top: 50px; text-align: center; color: #94a3b8;'>⚠️ AI 생성 정보입니다. 투자 책임은 본인에게 있습니다.</div>"""), unsafe_allow_html=True)
