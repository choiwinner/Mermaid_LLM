#uv run streamlit run app_ollama.py
import streamlit as st
import ollama
import re
import os
import json
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
import koreanize_matplotlib
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="Mermaid & Data LLM (Ollama)",
    page_icon="🧞‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS (기존 스타일 유지)
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at top right, #1e293b, #0f172a);
        color: #f1f5f9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.8);
        backdrop-filter: blur(12px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    .stChatMessage {
        background-color: rgba(30, 41, 59, 0.7) !important;
        backdrop-filter: blur(10px);
        border-radius: 20px !important;
        padding: 20px !important;
        margin-bottom: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #f1f5f9 !important; /* 텍스트 색상 강제 지정 */
    }
    .stChatMessage p, .stChatMessage li, .stChatMessage div {
        color: #f1f5f9 !important;
    }
    .stChatMessage h1, .stChatMessage h2, .stChatMessage h3 {
        color: #60a5fa !important;
        font-family: inherit;
    }
    .main-title {
        background: linear-gradient(to right, #60a5fa, #a78bfa, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3.5rem;
        font-family: inherit;
    }
    /* 코드 블록 가독성 강화 */
    code {
        color: #fca5a5 !important;
        background-color: rgba(0, 0, 0, 0.4) !important;
        padding: 2px 6px !important;
        border-radius: 4px;
        font-weight: 600;
    }
    pre {
        background-color: #0f172a !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 15px !important;
    }
    pre code {
        color: #adbac7 !important;
        background-color: transparent !important;
        padding: 0 !important;
        font-weight: 400;
    }
    </style>
""", unsafe_allow_html=True)

# 타이틀 출력
title_col1, title_col2 = st.columns([0.1, 0.9])
with title_col1:
    st.image("Mermaid_icon.svg", width=80)
with title_col2:
    st.markdown('<h1 class="main-title">Mermaid & Data LLM</h1>', unsafe_allow_html=True)
st.caption("Ollama를 활용한 오프라인 지능형 다이어그램 생성 및 데이터 시각화 도구")

# 로컬 Mermaid JS 파일 로드
mermaid_js_path = os.path.join(os.getcwd(), "mermaid.min.js")
if os.path.exists(mermaid_js_path):
    with open(mermaid_js_path, "r", encoding="utf-8") as f:
        mermaid_js_content = f.read()
else:
    st.error("mermaid.min.js 파일을 찾을 수 없습니다.")
    st.stop()

# 사이드바 설정
with st.sidebar:
    st.image("hero-chart-dark.svg", width=300)
    st.header("⚙️ Ollama 설정")
    
    # Ollama 모델 목록 가져오기
    try:
        model_names = []
        models = ollama.list()
        # 모델 목록 출력하기
        for model in models['models']:
            model_names.append(model['model'])

        if not model_names:
            st.error("설치된 Ollama 모델이 없습니다. 'ollama pull llama3' 등을 실행하세요.")
            st.stop()
        selected_model = st.selectbox("사용할 모델을 선택하세요", model_names, index=0)
        st.success(f"✅ 모델 '{selected_model}' 준비 완료")
    except Exception as e:
        st.error(f"❌ Ollama 서비스에 연결할 수 없습니다: {e}")
        st.info("Ollama 서비스가 실행 중인지 확인하세요.")
        st.stop()
    
    st.divider()
    if st.button("대화 기록 초기화"):
        st.session_state.messages = []
        st.rerun()

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 대화 렌더링
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "mermaid_code" in message and message["mermaid_code"]:
            html_code = f"""
            <div style="background-color: white; padding: 20px; border-radius: 10px;">
                <pre class="mermaid">{message['mermaid_code']}</pre>
                <script>{mermaid_js_content}mermaid.initialize({{ startOnLoad: true, theme: 'default' }});</script>
            </div>
            """
            st.components.v1.html(html_code, height=500, scrolling=True)
        if "plotly_fig" in message and message["plotly_fig"]:
            st.plotly_chart(message["plotly_fig"], use_container_width=True, key=f"plotly_history_{idx}")

# 사용자 입력 처리
if prompt := st.chat_input("메시지를 입력하세요"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 시스템 프롬프트 구성 (다이어그램 및 시각화 지침 강화)
    system_prompt = """
    당신은 시스템 아키텍처 설계와 데이터 시각화 전문가입니다.
    사용자의 요청에 따라 다음 두 가지 중 적절한 방식으로 응답하세요:

    1. **Mermaid 다이어그램**: 구조적 설계가 필요한 경우 반드시 ```mermaid 블록 사용.
       - 중요: 노드 이름이나 텍스트에 한글, 공백, 괄호, 쉼표, 콜론 등 특수 문자가 포함될 경우 반드시 큰따옴표(" ")로 감싸야 합니다.
       - 예: Start(("요리 시작")) --> Prep["재료 준비"]
       - 다이어그램 내에서 한국어 주석과 레이블을 적극적으로 사용하십시오.

    2. **Plotly 시각화**: 수치 데이터 시각화가 필요한 경우 반드시 ```python 블록 사용.
       - Plotly Express(px)를 사용할 때 존재하지 않는 인자(예: line=...)를 사용하지 마십시오.
       - 'fig = px.line(data_frame, x="column1", y="column2", title="제목")' 형식을 사용하세요.
       - 코드 블록 마지막에 'st.plotly_chart(fig)'를 포함하지 않아도 되지만, 변수명은 반드시 'fig'로 지정해야 합니다.

    모든 응답은 한국어로 친절하게 작성하세요.
    """

    # Ollama 메시지 형식 구성
    ollama_messages = [{"role": "system", "content": system_prompt}]
    for m in st.session_state.messages:
        ollama_messages.append({"role": m["role"], "content": m["content"]})
    
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        try:
            # 스트리밍 응답 처리
            stream = ollama.chat(model=selected_model, messages=ollama_messages, stream=True)
            for chunk in stream:
                full_response += chunk['message']['content']
                response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
            
            # Mermaid 추출
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

            # Plotly 추출
            plotly_match = re.search(r'```python\n(.*?)\n```', full_response, re.DOTALL)
            current_fig = None
            if plotly_match:
                python_code = plotly_match.group(1).strip()
                try:
                    local_ns = {"px": px, "go": go, "st": st}
                    exec(python_code, {}, local_ns)
                    if "fig" in local_ns:
                        current_fig = local_ns["fig"]
                        st.plotly_chart(current_fig, use_container_width=True, key=f"plotly_current_{len(st.session_state.messages)}")
                except Exception as e:
                    st.error(f"시각화 코드 오류: {e}")

            st.session_state.messages.append({
                "role": "assistant", 
                "content": full_response,
                "mermaid_code": current_mermaid,
                "plotly_fig": current_fig
            })

        except Exception as e:
            st.error(f"⚠️ 오류 발생: {e}")
