#uv run streamlit run app.py
import streamlit as st
import google.generativeai as genai
import re
import os
import json
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
import koreanize_matplotlib
from dotenv import load_dotenv

# .env 파일 로드 (API 키 관리)
load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="Mermaid & Data LLM Dashboard",
    page_icon="🧞‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS (Rich Aesthetics 적용)
st.markdown("""
    <style>
    /* 외부 폰트 의존성 제거 (보안을 위해 시스템 폰트 스택 사용) */
    .stApp {
        background: radial-gradient(circle at top right, #1e293b, #0f172a);
        color: #f1f5f9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
    }
    
    /* 사이드바 스타일링 */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.8);
        backdrop-filter: blur(12px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* 채팅 메시지 컨테이너 공통 스타일 */
    .stChatMessage {
        background-color: rgba(30, 41, 59, 0.5) !important;
        backdrop-filter: blur(10px);
        border-radius: 20px !important;
        padding: 20px !important;
        margin-bottom: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    /* 텍스트 시인성 강화 (가장 중요) */
    .stChatMessage p, .stChatMessage li, .stChatMessage div {
        color: #f1f5f9 !important;
        font-size: 1.05rem;
        line-height: 1.6;
        font-weight: 400;
    }
    
    .stChatMessage h1, .stChatMessage h2, .stChatMessage h3 {
        color: #60a5fa !important;
        margin-top: 10px;
        margin-bottom: 10px;
        font-family: inherit;
    }

    /* 사용자 메시지 차별화 (더 밝고 푸른 느낌) */
    [data-testid="chatAvatarIcon-user"] {
        background-color: #3b82f6;
    }
    
    /* 어시스턴트 메시지 차별화 (은은한 보라빛 배경) */
    [data-testid="stChatMessage"] {
        /* 기본적으로 어시스턴트용 */
    }

    /* 타이틀 애니메이션 */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .main-title {
        animation: fadeIn 1s ease-out;
        background: linear-gradient(to right, #60a5fa, #a78bfa, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3.5rem;
        margin-bottom: 0.2rem;
        font-family: inherit;
    }
    
    /* 코드 블록 스타일 */
    code {
        color: #fca5a5 !important;
        background-color: rgba(0, 0, 0, 0.3) !important;
        padding: 2px 6px !important;
        border-radius: 4px;
    }
    
    /* 버튼 스타일 */
    .stButton>button {
        border-radius: 12px;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        color: white;
        border: none;
        font-weight: 600;
        padding: 0.5rem 1.5rem;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .stButton>button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 10px 20px rgba(59, 130, 246, 0.3);
        color: white;
    }

    /* 입력창 스타일 커스텀 */
    .stChatFloatingInputContainer {
        background-color: rgba(15, 23, 42, 0.9) !important;
        backdrop-filter: blur(10px);
        padding: 10px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# 타이틀 출력
title_col1, title_col2 = st.columns([0.1, 0.9])
with title_col1:
    st.image("Mermaid_icon.svg", width=80)
with title_col2:
    st.markdown('<h1 class="main-title">Mermaid & Data LLM</h1>', unsafe_allow_html=True)
st.caption("지능형 다이어그램 생성 및 데이터 시각화 도구 (보안 최적화 로컬 버전)")

# 로컬 Mermaid JS 파일 로드
mermaid_js_path = os.path.join(os.getcwd(), "mermaid.min.js")
if os.path.exists(mermaid_js_path):
    with open(mermaid_js_path, "r", encoding="utf-8") as f:
        mermaid_js_content = f.read()
else:
    st.error("mermaid.min.js 파일을 찾을 수 없습니다. 루트 디렉토리에 파일이 있는지 확인하세요.")
    st.stop()

# 사이드바 설정
with st.sidebar:
    
    st.image("hero-chart-dark.svg", width=300)
        
    st.header("⚙️ 프로젝트 설정")
    
    # API 키 처리 (환경변수 또는 사용자 입력)
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        api_key = st.text_input("Gemini API Key를 입력하세요", type="password", help="Google AI Studio에서 발급받은 API 키를 입력하세요.")
    else:
        st.success("✅ API Key 로드 완료")
    
    st.divider()
    st.markdown("""
    ### 🛠 사용 가능 기능
    - **Mermaid 다이어그램**: 플로우차트, 시퀀스, 간트 차트 등
    - **Plotly 시각화**: 막대, 선, 파이 차트 등 데이터 기반 시각화
    - **한글 자동 최적화**: 차트 내 한글 폰트 완벽 지원
    """)
    
    if st.button("대화 기록 초기화"):
        st.session_state.messages = []
        st.rerun()

# API 키 유효성 검사
if not api_key:
    st.warning("⚠️ 서비스를 이용하려면 사이드바에 Gemini API 키를 입력해야 합니다.")
    st.stop()

# Gemini 모델 초기화
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-3-flash-preview')
except Exception as e:
    st.error(f"❌ 모델 초기화 중 오류 발생: {e}")
    st.stop()

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 대화 렌더링
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Mermaid 렌더링 (저장된 코드가 있는 경우)
        if "mermaid_code" in message and message["mermaid_code"]:
            html_code = f"""
            <div style="background-color: white; padding: 20px; border-radius: 10px;">
                <pre class="mermaid">{message['mermaid_code']}</pre>
                <script>{mermaid_js_content}mermaid.initialize({{ startOnLoad: true, theme: 'default' }});</script>
            </div>
            """
            st.components.v1.html(html_code, height=500, scrolling=True)
            
        # Plotly 렌더링 (저장된 피규어 데이터가 있는 경우)
        if "plotly_fig" in message and message["plotly_fig"]:
            st.plotly_chart(message["plotly_fig"], use_container_width=True, key=f"plotly_history_{idx}")

# 사용자 입력 처리
if prompt := st.chat_input("메시지를 입력하세요 (예: 서비스 아키텍처 그려줘, 최근 3년 수익 변화를 차트로 보여줘)"):
    # 사용자 메시지 저장 및 표시
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 시스템 프롬프트 구성 (다이어그램 및 시각화 지침 강화)
    system_prompt = """
    당신은 시스템 아키텍처 설계와 데이터 시각화 전문가입니다.
    사용자의 요청에 따라 다음 두 가지 중 적절한 방식으로 응답하세요:

    1. **Mermaid 다이어그램**: 구조적 설계가 필요한 경우
       - 반드시 ```mermaid 와 ``` 블록을 사용하세요.
       - 한국어 주석과 레이블을 적극적으로 사용하세요.

    2. **Plotly 시각화**: 수치 데이터 시각화가 필요한 경우
       - 수치 데이터를 시각화할 때는 반드시 Plotly Express(px) 또는 Graph Objects(go)를 사용하세요.
       - 응답에 ```python 블록을 포함하고, 그 안에 'fig = px.line(...)'와 같이 시뮬레이션 데이터를 포함한 코드를 작성하세요.
       - 최종적으로 'st.plotly_chart(fig)'를 실행할 수 있도록 코드를 구성하세요.

    항상 한국어로 친절하게 설명하고, 결과물에 대한 상세한 분석도 곁들여주세요.
    """

    # 대화 기록 포함 프롬프트
    messages_history = [{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages]
    
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        with st.spinner("생각 중..."):
            try:
                # 스트리밍은 복잡성을 위해 일반 생성 후 처리
                response = model.generate_content([system_prompt] + [m["content"] for m in st.session_state.messages])
                full_response = response.text
                response_placeholder.markdown(full_response)
                
                # Mermaid 코드 추출 및 렌더링
                mermaid_match = re.search(r'```mermaid\n(.*?)\n```', full_response, re.DOTALL)
                current_mermaid = None
                if mermaid_match:
                    current_mermaid = mermaid_match.group(1).strip()
                    html_code = f"""
                    <div style="background-color: white; padding: 20px; border-radius: 10px; margin-top: 10px;">
                        <pre class="mermaid">{current_mermaid}</pre>
                        <script>{mermaid_js_content}mermaid.initialize({{ startOnLoad: true, theme: 'default' }});</script>
                    </div>
                    """
                    st.components.v1.html(html_code, height=500, scrolling=True)

                # Plotly 코드 추출 및 실행
                plotly_match = re.search(r'```python\n(.*?)\n```', full_response, re.DOTALL)
                current_fig = None
                if plotly_match:
                    python_code = plotly_match.group(1).strip()
                    # 보안을 위해 'fig' 객체가 생성되는지 확인하는 안전한 실행 시도 (데모 목적)
                    try:
                        # 로컬 네임스페이스 준비
                        local_ns = {"px": px, "go": go, "pd": None} # pandas는 필요시 추가
                        exec(python_code, {}, local_ns)
                        if "fig" in local_ns:
                            current_fig = local_ns["fig"]
                            st.plotly_chart(current_fig, use_container_width=True, key=f"plotly_current_{len(st.session_state.messages)}")
                    except Exception as e:
                        st.error(f"시각화 코드 실행 중 오류 발생: {e}")

                # 세션 데이터 저장
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": full_response,
                    "mermaid_code": current_mermaid,
                    "plotly_fig": current_fig
                })

            except Exception as e:
                st.error(f"⚠️ 응답 생성 중 오류 발생: {e}")
