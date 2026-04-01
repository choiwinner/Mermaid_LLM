#uv run streamlit run app_high_performance.py
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
    page_title="High-Performance Mermaid & Data LLM",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 고성능 모델 전용 커스텀 CSS (더욱 프리미엄한 디자인)
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at 0% 0%, #0f172a, #1e293b);
        color: #f1f5f9;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    [data-testid="stSidebar"] {
        background-color: rgba(2, 6, 23, 0.9);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    .stChatMessage {
        background-color: rgba(30, 41, 59, 0.4) !important;
        backdrop-filter: blur(12px);
        border-radius: 24px !important;
        padding: 24px !important;
        margin-bottom: 24px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }
    .stChatMessage p, .stChatMessage li, .stChatMessage div {
        color: #e2e8f0 !important;
        font-size: 1.05rem;
        line-height: 1.7;
    }
    .main-title {
        background: linear-gradient(135deg, #60a5fa, #c084fc, #fb7185);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        font-size: 4rem;
        letter-spacing: -0.02em;
    }
    .status-badge {
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid rgba(59, 130, 246, 0.2);
        color: #60a5fa;
        padding: 4px 12px;
        border-radius: 100px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    /* 코드 블록 스타일링 강화 */
    code {
        color: #93c5fd !important;
        background-color: rgba(30, 41, 59, 0.6) !important;
        padding: 2px 8px !important;
        border-radius: 6px;
    }
    pre {
        background-color: #020617 !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 16px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 타이틀 출력
title_col1, title_col2 = st.columns([0.1, 0.9])
with title_col1:
    st.image("Mermaid_icon.svg", width=80)
with title_col2:
    st.markdown('<h1 class="main-title">High-Performance LLM Diagram</h1>', unsafe_allow_html=True)
st.markdown('<span class="status-badge">Nemotron & GPT-OSS Optimized</span> &nbsp; <span class="status-badge">Next-Gen Visualization</span>', unsafe_allow_html=True)

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
    st.header("⚙️ 고성능 모델 엔진")
    
    try:
        model_names = []
        models = ollama.list()
        for model in models['models']:
            model_names.append(model['model'])

        if not model_names:
            st.error("설치된 Ollama 모델이 없습니다.")
            st.stop()
            
        # 기본값으로 사용자가 언급한 모델 우선 순위 부여
        default_index = 0
        preferred_models = ["nemotron-cascade-2", "gpt-oss:120b"]
        for i, m in enumerate(model_names):
            if any(p in m.lower() for p in preferred_models):
                default_index = i
                break
                
        selected_model = st.selectbox("엔진 선택", model_names, index=default_index)
        st.success(f"🔥 '{selected_model}' 가동 중")
    except Exception as e:
        st.error(f"❌ Ollama 서비스 연결 오류: {e}")
        st.stop()
    
    st.divider()
    st.markdown("""
    ### 🚀 주요 특징 (100B+ 전용)
    - **CoT(Chain-of-Thought)**: 논리적 분석 선행
    - **Nested Architecture**: 복잡한 계층 구조 지원
    - **Advanced Mermaid**: Journey, XY, State-V2 적용
    - **Precise Plotly**: 정규 분포 및 회귀 분석 시각화
    """)
    if st.button("대화 초기화"):
        st.session_state.messages = []
        st.rerun()

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 대화 렌더링
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "mermaid_code" in message and message["mermaid_code"]:
            html_code = f"""
            <div style="background-color: white; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0;">
                <pre class="mermaid" style="background-color: transparent !important; color: #1e293b !important; font-family: 'Courier New', monospace;">{message['mermaid_code']}</pre>
                <script>{mermaid_js_content}mermaid.initialize({{ startOnLoad: true, theme: 'neutral' }});</script>
            </div>
            """
            st.components.v1.html(html_code, height=600, scrolling=True)
        if "plotly_fig" in message and message["plotly_fig"]:
            st.plotly_chart(message["plotly_fig"], use_container_width=True, key=f"plotly_history_{idx}")

# 사용자 입력 처리
if prompt := st.chat_input("설계할 시스템이나 분석할 데이터를 입력하세요 (예: MSA 결제 시스템 설계해줘)"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 고성능 모델 전용 시스템 프롬프트 (분석 + CoT + 고수준 설계)
    system_prompt = """
당신은 최고 수준의 시스템 아키텍트이자 데이터 과학자입니다. 사용하시는 모델의 뛰어난 추론 능력을 활용하여 정교한 결과물을 제공해야 합니다.

[작동 매커니즘: Think Before Code]
1. 분석(Analysis): 사용자의 요청을 수신하면 즉시 다이어그램을 그리지 말고, 시스템의 핵심 구성 요소, 데이터 흐름, 잠재적 병목 지점을 텍스트로 먼저 분석하십시오.
2. 설계(Design): 분석을 바탕으로 최적의 시각화 도구(Mermaid의 특정 유형 또는 Plotly)를 결정하십시오.
3. 구현(Code): 결정된 도구를 사용하여 완성도 높은 시각화 블록을 생성하십시오.

[Mermaid 고난도 설계 지침]
- 가독성: 복잡한 구조의 경우 subgraph를 사용하여 논리적 영역을 반드시 분리하십시오.
- 스타일: classDef와 style을 사용하여 중요 노드나 데이터를 강조하십시오.
- 최신 문법: 다음 고성능 다이어그램 유형을 적극 활용하십시오.
    1. architecture-beta (인프라/클라우드 설계)
    2. journey (사용자 여정 및 경험 분석)
    3. stateDiagram-v2 (정밀한 상태 전이 제어)
    4. sequenceDiagram (비동기 메시징 및 루프 표현)
    5. packet (통신 프로토콜 상세 구조)
    6. sankey / treemap-beta (복잡한 자원 배분 분석)

■ Flowchart 문법 필수 수칙 (절대 오류 방지):
1. 'graph' 대신 'flowchart' 지시어를 사용하십시오. (예: flowchart TD)
2. 화살표 라벨 규칙: 라벨과 바(|) 사이에는 공백이 없어야 합니다.
   - 옳은 예: A -->|"라벨"| B (O)
   - 틀린 예: A -->| "라벨" | B (X) , A --> B|라벨| (X), A --> B : "라벨" (X)
3. 주석(%%) 관련 규칙: 주석은 반드시 별도의 줄에 작성하십시오. 코드와 같은 줄에 작성하는 것을 엄격히 금지합니다.
   - 옳은 예:
     %% 주석 내용
     A --> B
   - 틀린 예: A --> B %% 주석 내용 (X)
4. 모든 텍스트 레이블은 반드시 큰따옴표(" ")로 감쌉니다.
5. 노드 ID는 영문자로 시작하며 특수문자를 포함하지 마십시오. (예: ID1, Process_A 등)
6. 노드 디자인: A["텍스트"], B("텍스트"), C{"결정"} 등 다양한 박스 형태를 활용하십시오.
7. 서브그래프는 반드시 명시적 ID와 따옴표를 사용하십시오. (예: subgraph SG1 ["라벨"])

■ 실전 예제 (Flowchart):
```mermaid
flowchart TD
    A["시작"] -->| "데이터 입력" | B["처리"]
    B --> C{"검증 결과"}
    C -->| "성공" | D["완료"]
    C -->| "실패" | E["재시도"]
    style A fill:#f9f,stroke:#333,stroke-width:4px
```

■ Plotly 시각화 (Power analysis):
- 단순한 차트를 넘어, 추세선(Trendline), 히트맵, 또는 다차원 산점도를 통해 데이터의 깊은 통찰을 제공하십시오.

항상 한국어로 전문가다운 톤으로 설명하며, 생성된 시각화 결과물에 대한 기술적 분석과 개선 제안을 함께 곁들여주세요.
"""

    ollama_messages = [{"role": "system", "content": system_prompt}]
    for m in st.session_state.messages:
        ollama_messages.append({"role": m["role"], "content": m["content"]})
    
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        try:
            stream = ollama.chat(model=selected_model, messages=ollama_messages, stream=True)
            for chunk in stream:
                full_response += chunk['message']['content']
                response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
            
            # Mermaid 및 Plotly 추출 처리 (기존 로직 고도화)
            mermaid_match = re.search(r'```mermaid\n(.*?)\n```', full_response, re.DOTALL)
            current_mermaid = None
            if mermaid_match:
                current_mermaid = mermaid_match.group(1).strip()
                html_code = f"""
                <div style="background-color: white; padding: 20px; border-radius: 12px; margin-top: 15px; border: 1px solid #e2e8f0;">
                    <pre class="mermaid" style="background-color: transparent !important; color: #1e293b !important; font-family: 'Courier New', monospace;">{current_mermaid}</pre>
                    <script>{mermaid_js_content}mermaid.initialize({{ startOnLoad: true, theme: 'neutral' }});</script>
                </div>
                """
                st.components.v1.html(html_code, height=600, scrolling=True)

            plotly_match = re.search(r'```python\n(.*?)\n```', full_response, re.DOTALL)
            current_fig = None
            if plotly_match:
                python_code = plotly_match.group(1).strip()
                try:
                    local_ns = {"px": px, "go": go, "st": st, "plt": plt}
                    exec(python_code, {}, local_ns)
                    if "fig" in local_ns:
                        current_fig = local_ns["fig"]
                        st.plotly_chart(current_fig, use_container_width=True, key=f"plotly_current_{len(st.session_state.messages)}")
                except Exception as e:
                    st.error(f"시각화 엔진 오류: {e}")

            st.session_state.messages.append({
                "role": "assistant", 
                "content": full_response,
                "mermaid_code": current_mermaid,
                "plotly_fig": current_fig
            })

        except Exception as e:
            st.error(f"⚠️ 시스템 오류: {e}")
