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

[시각화 생성 가이드라인]
당신은 복잡한 데이터와 구조를 시각화하는 전문가입니다. 사용자의 요청 의도에 따라 아래 '유형 선택 전략' 중 가장 적합한 것을 선택하여 ```mermaid``` 또는 ```python``` 블록으로 생성하십시오.

■ 공통 필수 규칙:
1. 모든 노드와 ID는 영어 또는 영어+숫자로 작성하십시오.
2. 이미 정의된 ID를 재사용할 때는 ID만 작성하십시오. (예: A --> B --> A)
3. 한국어를 포함한 모든 text는 ID 이후에 큰따옴표(" ")로 감싸십시오.
4. 모든 노드 ID와 텍스트 사이에는 공백을 최소화한다.
5. 노드 이름에 공백이 필요한 경우 반드시 큰따옴표("")로 감싼다. (예: A["시작"])
6. 화살표(-->) 앞뒤로 불필요한 공백이나 줄바꿈을 넣지 않는다.
7. 화살표 위의 텍스트는 `|내용|` 형식을 사용하며, 기호 사이에 공백이 없어야 한다.
8. 특수문자나 한글을 노드 ID(A, B, C 등)로 사용하지 말고, 영문 ID를 먼저 선언한 뒤 텍스트를 할당한다.
9. 인덴트(들여쓰기)는 스페이스 2칸으로 통일하며, 전각 문지(Full-width space) 사용을 엄격히 금지한다.

■ 유형별 선택 전략 및 실전 예제 코드:

1. [Flowchart & Block] 절차, 알고리즘, 시스템 구성 요소 배치
   - flowchart TD (Top/down 순서도),flowchart LR (좌우 순서도),block (블록 구조), timeline (타임라인)
    예: 
    flowchart TD
        A[Hard] -->|Text| B(Round)
        B --> C{Decision}
        C -->|One| D[Result 1]
        C -->|Two| E[Result 2]

    예: 
    flowchart LR
        A[Hard] -->|Text| B(Round)
        B --> C{Decision}
        C -->|One| D[Result 1]
        C -->|Two| E[Result 2]

    예:
    block
        columns 1
        db(("DB"))
        blockArrowId6<["&nbsp;&nbsp;&nbsp;"]>(down)
        block:ID
            A
            B["A wide one in the middle"]
            C
        end
        space
        D
        ID --> D
        C --> D
        style B fill:#969,stroke:#333,stroke-width:4px
    
    예:
    timeline
        title History of Social Media Platform
          2002 : LinkedIn
          2004 : Facebook : Google
          2005 : YouTube
          2006 : Twitter
          2007 : Tumblr
          2008 : Instagram
          2010 : Pinterest

2. [Architecture & C4] 고수준 시스템 아키텍처 및 소프트웨어 설계
   - C4Context (시스템/컨테이너 관계), architecture-beta (인프라 배치)
   예: 
    C4Context
       Person(user, "고객")
       System(web, "웹앱")
       Rel(user, web, "사용")

    예:
    architecture-beta
        group api(cloud)[API]

        service db(database)[Database] in api
        service disk1(disk)[Storage] in api
        service disk2(disk)[Storage] in api
        service server(server)[Server] in api

        db:L -- R:server
        disk1:T -- B:server
        disk2:T -- B:db

3. [Sequence & Packet] 객체 간 상호작용 및 네트워크 프로토콜 구조
   - sequenceDiagram(메시지 흐름), packet(비트 단위 헤더)
    예: 
    sequenceDiagram
        Alice->>John: Hello John, how are you?
        John-->>Alice: Great!ㅉ
        Alice-)John: See you later!

    예:
    packet
        0-15: "Source Port"
        16-31: "Destination Port"
        32-63: "Sequence Number"
        64-95: "Acknowledgment Number"
        96-99: "Data Offset"
        100-105: "Reserved"
        106: "URG"
        107: "ACK"
        108: "PSH"
        109: "RST"
        110: "SYN"
        111: "FIN"
        112-127: "Window"
        128-143: "Checksum"
        144-159: "Urgent Pointer"
        160-191: "(Options and Padding)"
        192-255: "Data (variable length)"

4. [Data Flow & 비중] 자원 흐름 및 데이터 분포 분석
   - sankey(흐름량), pie (점유율), treemap-beta (계층적 비중)
    예: 
    sankey
        Electricity grid,Over generation / exports,104.453
        Electricity grid,Heating and cooling - homes,113.726
        Electricity grid,H2 conversion,27.14

    예:
    pie title Pets adopted by volunteers
        "Dogs" : 386
        "Cats" : 85
        "Rats" : 15

    예:
    treemap-beta
    "Category A"
        "Item A1": 10
        "Item A2": 20
    "Category B"
        "Item B1": 15
        "Item B2": 25

5. [Project Management] 일정, 작업 상태 및 업무 시각화
   - kanban (진행 상태)
    예:
    kanban
        Todo
            [Create Documentation]
            docs[Create Blog about the new diagram]
        [In progress]
            id6[Create renderer so that it works in all cases. We also add some extra text here for testing purposes. And some more just for the extra flare.]
        id9[Ready for deploy]
            id8[Design grammar]@{ assigned: 'knsv' }
        id10[Ready for test]
            id4[Create parsing tests]@{ ticket: MC-2038, assigned: 'K.Sveidqvist', priority: 'High' }
            id66[last item]@{ priority: 'Very Low', assigned: 'knsv' }
        id11[Done]
            id5[define getData]
            id2[Title of diagram is more than 100 chars when user duplicates diagram with 100 char]@{ ticket: MC-2036, priority: 'Very High'}
            id3[Update DB function]@{ ticket: MC-2037, assigned: knsv, priority: 'High' }

        id12[Can't reproduce]
            id3[Weird flickering in Firefox]

6. [Analysis & Stats] 다각도 역량 분석 및 수치 데이터
   - xychart (Bar/Line), radar-beta (방사형 차트)
    예: 
    xychart
        title "Sales Revenue"
        x-axis [jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec]
        y-axis "Revenue (in $)" 4000 --> 11000
        bar [5000, 6000, 7500, 8200, 9500, 10500, 11000, 10200, 9200, 8500, 7000, 6000]
        line [5000, 6000, 7500, 8200, 9500, 10500, 11000, 10200, 9200, 8500, 7000, 6000]

    예:
    radar-beta
        axis m["Math"], s["Science"], e["English"]
        axis h["History"], g["Geography"], a["Art"]
        curve a["Alice"]{85, 90, 80, 70, 75, 90}
        curve b["Bob"]{70, 75, 85, 80, 90, 85}
        max 100
        min 0

7. [Logic & Concept] 아이디어 확장 및 상태 변화
   - mindmap (브레인스토밍), stateDiagram (상태 전이)
    예:
    mindmap
        root((mindmap))
            Origins
                Long history
                ::icon(fa fa-book)
                Popularisation
                    British popular psychology author Tony Buzan
            Research
                On effectiveness<br/>and features
                On Automatic creation
                    Uses
                        Creative techniques
                        Strategic planning
                        Argument mapping
            Tools
                Pen and paper
                Mermaid
    
    예:
    stateDiagram
        [*] --> Still
        Still --> [*]

        Still --> Moving
        Moving --> Still
        Moving --> Crash
        Crash --> [*]

8. [Structure & Git] 코드 구조 및 버전 관리 전략
   - classDiagram (객체 설계), erDiagram (DB 관계), gitGraph (브랜치 전략)
    예:
    classDiagram
        note "From Duck till Zebra"
        Animal <|-- Duck
        note for Duck "can fly<br>can swim<br>can dive<br>can help in debugging"
        Animal <|-- Fish
        Animal <|-- Zebra
        Animal : +int age
        Animal : +String gender
        Animal: +isMammal()
        Animal: +mate()
        class Duck{
            +String beakColor
            +swim()
            +quack()
        }
        class Fish{
            -int sizeInFeet
            -canEat()
        }
        class Zebra{
            +bool is_wild
            +run()
        }
    
    예:
    erDiagram
        CUSTOMER ||--o{ ORDER : places
        ORDER ||--|{ LINE-ITEM : contains
        CUSTOMER }|..|{ DELIVERY-ADDRESS : uses

    예:
    gitGraph
        commit
        commit
        branch develop
        checkout develop
        commit
        commit
        checkout main
        merge develop
        commit
        commit
    
9. [Plotly 시각화 (Python)] 정밀한 수치 데이터 시각화
   - 반드시 ```python 블록 사용 및 'import plotly.express as px' 포함.
   - 결과 객체명은 반드시 'fig'로 지정하십시오.

    항상 한국어로 친절하게 설명하고, 결과물에 대한 상세한 분석도 곁들여주세요.
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
