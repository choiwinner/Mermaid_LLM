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

# 프롬프트 정의
PLANNER_SYSTEM_PROMPT = """
당신은 시스템 아키텍처 설계 및 데이터 분석 전문가 'Planner'입니다.
사용자의 요청을 분석하고 가장 적절한 시각화 전략과 다이어그램 도구를 제안하는 것이 당신의 역할입니다.

[수행 지침]
1. 분석(Analysis): 사용자의 요청 의도를 파악하고 핵심 엔티티, 흐름, 구조적 관계 등을 텍스트로 분석하세요.
2. 도구 선택(Tools): 분석을 바탕으로 가장 적합한 **단 하나(Only One)**의 시각화 도구를 결정하세요. 여러 다이어그램을 동시에 제안하지 마십시오.
   - flowchart: 일반적인 비즈니스 프로세스, 알고리즘, 시스템 구성도
   - sequenceDiagram: 객체/시스템 간의 상호작용 및 시간 순서상 흐름 (메시징, API 호출 등)
   - erDiagram: 데이터베이스 스키마 및 엔티티 간의 관계 정의
   - stateDiagram-v2: 시스템의 상태 전이 및 동작 제어 흐름
   - classDiagram: 객체 지향 클래스 구조, 상속 관계, 프로퍼티 정의
   - gantt: 프로젝트 일정, 로드맵, 타임라인 관리
   - journey: 사용자의 서비스 경험 여정 및 감정 변화 분석
   - pie / quadrantChart / mindmap: 특수 목적의 데이터 분포 및 브레인스토밍
   - Plotly (Python): 복잡한 수치 데이터 분석, 통계 그래프, 대화형 차트
3. 설계 전략(Strategy): 선택한 **하나의 도구**에서 어떤 요소(subgraph, style, note, loop 등)를 강조하고, **한국어 레이블**을 통해 가독성을 어떻게 높일지 구체적인 계획을 세우세요.
4. 사용자 승인 요청: 분석한 내용을 요약하고 "이 설계 방향(도구: [OOO], 한국어 레이블 적용)이 맞으신가요? 확인해 주시면 바로 시각화를 시작하겠습니다."와 같은 질문으로 끝맺음하세요.

[주의사항]
- 실제 실행 코드 블록(```mermaid, ```python)을 생성하지 마세요. 오직 계획과 구조만 제안하세요.
- 결과물에 대한 기대 효과를 포함하세요.
- 설명은 한국어로 전문가답고 친절하게 작성하세요.
"""

EXECUTOR_SYSTEM_PROMPT = """
당신은 'Planner'의 설계를 바탕으로 완벽한 시각화 결과물을 만드는 'Executor'입니다.

[수행 지침]
1. 구현(Code): Planner의 설계안과 사용자의 최종 요청을 바탕으로 지정된 다이어그램 유형의 ```mermaid``` 또는 ```python``` 블록으로 생성하십시오. **반드시 응답 당 단 하나의 코드 블록만 포함해야 합니다.**
2. 엄격한 문법 준수 (절대 준수):
   - **공통 규칙**:
     - ID(대괄호/괄호 앞) 한국어 사용 절대 금지: 영문 또는 영문+숫자만 사용하십시오.
     - **노드 정의**: `ID["한국어 레이블"]` 처럼 모든 노드의 텍스트는 반드시 **한국어**로 작성하고 **큰따옴표(" ")**로 감싸십시오.
     - **화살표 라벨**: 아래 기술된 **'유형별 라벨 문법'**을 반드시 따르십시오. (공통 규칙보다 우선함)
     - 주석(%%)은 반드시 별도의 줄에 작성하십시오.
   - **유형별 라벨 문법 (필수 준수)**:
     - **flowchart**: 화살표 라벨은 반드시 `| 라벨 |` 형식을 사용하십시오. **내부에 절대 따옴표(")를 포함하지 마십시오.** (예: `A -->| 승인 | B`)
     - **classDiagram / sequenceDiagram / erDiagram / stateDiagram-v2**: 라벨은 반드시 콜론(`:`) 뒤에 작성하고 **큰따옴표(" ")**로 감싸십시오. (예: `A -> B : "메시지"`, `ClassA <|-- ClassB : "상속"`)
     - **stateDiagram-v2 주의**: 단순 상태 설명은 `ID : "한국어 설명"` 형식을 사용하고, 불필요하게 `state ID { ID : "설명" }` 처럼 자기 자신을 블록으로 감싸지 마십시오. (순환 참조 오류 방지)
   - 구조적 복잡성이 있는 경우 subgraph나 note 등을 사용하여 가독성을 높이십시오.
3. 스타일 및 완성도:
   - `flowchart`: `style ID fill:#f9f` 명령어로 중요 노드를 강조하십시오.
   - `classDiagram / sequenceDiagram`: 무리한 스타일링보다 정확한 관계 정의와 `note`를 활용하여 정보를 전달하십시오.
4. 분석 결과 (간결함 유지): 생성된 시각화물에 대한 핵심 인사이트를 3~5문장 내외의 한국어로 요약하여 제공하십시오.
5. 종료: 모든 작업이 끝나면 더 이상 말을 덧붙이지 말고 응답을 종료하십시오.

[주의사항]
- **ID 부분에 절대 한국어를 포함하지 마십시오.** (문법 오류의 90% 원인)
- **서로 다른 다이어그램의 문법(특히 라벨 기법)을 절대 혼용하지 마십시오.**
- 응답 내에 여러 개의 ```mermaid``` 블록을 생성하지 마십시오. 가장 핵심적인 하나만 작성하십시오.
- Planner가 제안한 유형을 우선으로 하되, 문법적 오류가 예상되는 경우 가장 안정적인 표준 문법을 선택하세요.

[최종 경고: 렌더링 오류 방지 지침]
1. **키워드 고정**: 그룹화 시에는 반드시 `subgraph` 키워드만 사용하십시오. (`sublect` 등 존재하지 않는 단어 금지)
2. **flowchart 화살표 라벨 (유일한 예외)**: `| |` 내부의 한국어는 **절대 따옴표(")를 붙이지 마십시오.** 이 앱에서 유일하게 따옴표가 허용되지 않는 구역입니다.
   - ✅ 올바른 예: `A -->| 이동 | B`
   - ❌ 절대 금지: `A -->| "이동" | B`
3. **노드 정의와의 차이**: 박스 안의 텍스트(`ID["내용"]`)는 반드시 따옴표를 써야 하지만, 화살표 위의 텍스트(`|내용|`)는 쓰지 말아야 합니다. 이 차이를 엄격히 구분하십시오.
"""

# 페이지 설정
st.set_page_config(
    page_title="Mermaid & Data LLM (Agentic)",
    page_icon="🧞‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS (기본 스타일 유지)
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
        color: #f1f5f9 !important;
    }
    .stChatMessage p, .stChatMessage li, .stChatMessage div {
        color: #f1f5f9 !important;
    }
    .main-title {
        background: linear-gradient(to right, #60a5fa, #a78bfa, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3.5rem;
    }
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
    .status-box {
        background-color: rgba(96, 165, 250, 0.1);
        border-left: 5px solid #60a5fa;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# 타이틀 출력
title_col1, title_col2 = st.columns([0.1, 0.9])
with title_col1:
    st.image("Mermaid_icon.svg", width=80)
with title_col2:
    st.markdown('<h1 class="main-title">Mermaid Agentic LLM</h1>', unsafe_allow_html=True)
st.caption("Planner-Executor 기반의 인터랙티브 다이어그램 설계 및 생성 도구 (Ollama)")

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
    
    try:
        models = ollama.list()
        model_names = [m['model'] for m in models['models']]
        if not model_names:
            st.error("설치된 Ollama 모델이 없습니다.")
            st.stop()
        selected_model = st.selectbox("사용할 모델을 선택하세요", model_names, index=0)
        st.success(f"✅ '{selected_model}' 모델 준비됨")
    except Exception as e:
        st.error(f"❌ Ollama 서비스 연결 실패: {e}")
        st.stop()
    
    st.divider()
    if st.button("대화 기록 초기화"):
        st.session_state.messages = []
        st.session_state.pending_plan = None
        st.rerun()

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_plan" not in st.session_state:
    st.session_state.pending_plan = None
if "trigger_executor" not in st.session_state:
    st.session_state.trigger_executor = False

# 대화 기록 렌더링
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("type") == "plan":
            st.info("💡 위 설계가 마음에 드시면 실행 버튼을 눌러주세요.")
        if message.get("mermaid_code"):
            html_code = f"""<div style="background-color: white; padding: 20px; border-radius: 10px;">
                <pre class="mermaid">{message['mermaid_code']}</pre>
                <script>{mermaid_js_content}mermaid.initialize({{ startOnLoad: true, theme: 'default' }});</script>
            </div>"""
            st.components.v1.html(html_code, height=500, scrolling=True)
        if message.get("plotly_fig"):
            st.plotly_chart(message["plotly_fig"], use_container_width=True, key=f"plotly_history_{idx}")

# 플래너 실행 함수
def run_planner(user_prompt):
    messages = [{"role": "system", "content": PLANNER_SYSTEM_PROMPT}]
    # 과거 대화 맥락 포함
    for m in st.session_state.messages:
        if m["role"] != "system":
            messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": user_prompt})
    
    with st.status("🏗️ 아키텍처 및 시각화 계획 수립 중...", expanded=True) as status:
        try:
            response = ollama.chat(model=selected_model, messages=messages, options={'num_ctx': 8192})
            plan_content = response['message']['content']
            status.update(label="✅ 계획 수립 완료!", state="complete")
            return plan_content
        except Exception as e:
            status.update(label="❌ 계획 수립 실패", state="error")
            st.error(f"Planner 실행 중 오류가 발생했습니다: {e}")
            return None

# 실행자 실행 함수
def run_executor(plan_content, user_feedback=""):
    messages = [
        {"role": "system", "content": EXECUTOR_SYSTEM_PROMPT},
        {"role": "user", "content": f"다음 'Planner'의 설계안을 바탕으로 시각화 코드를 생성하고 분석해 주세요.\n\n[Planner의 설계안]\n{plan_content}"}
    ]
    if user_feedback:
        messages.append({"role": "user", "content": f"사용자 추가 피드백: {user_feedback}"})
    
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        try:
            stream = ollama.chat(model=selected_model, messages=messages, stream=True, 
                                 options={'num_ctx': 8192})
            
            for chunk in stream:
                full_response += chunk['message']['content']
                response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"Executor 실행 중 오류가 발생했습니다: {e}")
            return
        
        # Mermaid 추출
        mermaid_match = re.search(r'```mermaid\n(.*?)\n```', full_response, re.DOTALL)
        current_mermaid = mermaid_match.group(1).strip() if mermaid_match else None
        if current_mermaid:
            html_code = f"""<div style="background-color: white; padding: 20px; border-radius: 10px; margin-top: 10px;">
                <pre class="mermaid">{current_mermaid}</pre>
                <script>{mermaid_js_content}mermaid.initialize({{ startOnLoad: true, theme: 'default' }});</script>
            </div>"""
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
                    st.plotly_chart(current_fig, use_container_width=True)
            except Exception as e:
                st.error(f"시각화 코드 오류: {e}")

        # 메시지 추가
        st.session_state.messages.append({
            "role": "assistant",
            "content": full_response,
            "mermaid_code": current_mermaid,
            "plotly_fig": current_fig
        })
        st.session_state.pending_plan = None # 완료 후 삭제

# 사용자 입력 처리
if prompt := st.chat_input("메시지를 입력하세요 (예: MSA 구조 그려줘)"):
    # 이전 계획이 있더라도 새로운 입력이 오면 다시 계획 수립
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 플래너 실행
    plan = run_planner(prompt)
    st.session_state.pending_plan = plan
    st.session_state.messages.append({"role": "assistant", "content": plan, "type": "plan"})
    st.rerun()

# 리뷰 단계 UI (마지막 메시지가 계획일 때만 표시)
if st.session_state.pending_plan and st.session_state.messages and st.session_state.messages[-1].get("type") == "plan":
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        if st.button("🚀 실행(Proceed)", use_container_width=True):
            st.session_state.trigger_executor = True
            st.rerun()
    with col2:
        st.write("계획이 마음에 안 드시면 채팅창에 다시 입력해 주세요.")

# 실행 트리거 (컬럼 외부에서 실행하여 전체 너비 사용)
if st.session_state.trigger_executor and st.session_state.pending_plan:
    run_executor(st.session_state.pending_plan)
    st.session_state.trigger_executor = False
    st.rerun()
