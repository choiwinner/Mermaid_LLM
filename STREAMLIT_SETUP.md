# 🧞‍♂️ Gemini Mermaid Diagram Generator 설정 가이드

이 문서는 현재 개발된 Streamlit 기반의 **Gemini Mermaid 다이어그램 생성기**를 Git 저장소에 업로드하고, 다른 환경에서 다운로드하여 설치 및 실행하는 전체 과정을 안내합니다.

---

## 설치 방법 : https://mermaid.ai/open-source/intro/index.html

## 1. 현재 폴더를 Git 저장소에 업로드 (최초 1회)

### 1.1 저장소 생성 및 환경 보호 파일 확인
먼저 GitHub 또는 GitLab 등에서 새로운 빈 저장소(Repository)를 만듭니다.
그다음, 불필요하거나 보안상 민감한 파일이 올라가지 않도록 최상위 경로에 있는 `.gitignore` 파일에 아래 내용이 **반드시** 포함되어 있는지 확인하세요.
```text
# .gitignore 
.venv/
.env
```

### 1.2 Git 커밋 및 Push
터미널을 열고 현재 프로젝트 폴더(`c:\python\Mermaid_LLM`)에서 아래 명령어들을 순차적으로 실행합니다.

```bash
# 1. (필요 시) Git 초기화 (이미 git 저장소라면 생략 가능)
git init

# 2. 변경된 사항들 모두 스테이징 (app.py 등 추가)
git add .

# 3. 커밋 메시지 작성 
git commit -m "Add Streamlit Gemini Mermaid App"

# 4. 원격 저장소 주소 연결 
git remote add origin <본인의_저장소_URL>

# 5. 메인 브랜치 설정 및 원격 저장소에 업로드 (푸시)
git branch -M main
git push -u origin main
```

---

## 2. 다른 환경에서 다운로드 및 설치하기 (클론)

새로운 PC나 서버 환경에서 프로젝트 코드를 다운로드받고 실행 환경을 구성하는 단계입니다.

### 2.1 소스 코드 다운로드
```bash
# 저장소 복제 (폴더명: Mermaid_LLM)
git clone <본인의_저장소_URL>

# 복제한 폴더로 이동
cd Mermaid_LLM
```

### 2.2 패키지 및 가상환경 설치 (Node.js & Python)
이 프로젝트는 원본 Mermaid 코어 저장소를 기반으로 하므로, Node.js 패키지 환경과 사이드 기능인 Python 환경을 모두 구축해야 합니다. 대상 컴퓨터에 `Node.js`와 `uv`가 먼저 설치되어 있어야 합니다.

#### A. Node.js 의존성 설치 (Mermaid 코어용)
```bash
# 1. 원본 프로젝트가 pnpm을 사용하므로, 전역으로 pnpm 설치 (npm 권장)
npm install -g pnpm

# 2. 해당 폴더의 모든 의존성 설치
pnpm install
```

#### B. Python 가상환경 및 패키지 설치 (Streamlit 앱용)
해당 파일들은 빠르고 가벼운 패키지 관리자인 `uv`를 사용합니다.

```bash
# 1. uv를 사용하여 .venv라는 이름의 가상환경 생성
uv venv .venv

# 2. 필요한 파이썬 라이브러리 설치 (Streamlit 및 Gemini API 모듈)
uv pip install streamlit google-generativeai
```

> **참고:** `pnpm dev` 명령어를 실행하면 Mermaid 개발 서버가 실행되어 `http://localhost:9000` 등에서 로컬 예제 파일들을 직접 구동하고 확인할 수 있습니다. Streamlit 앱 자체는 이와 독립적으로 실행됩니다.

---

## 3. 프로그램 실행하기

의존성 패키지가 모두 설치되었으면 앱을 바로 실행할 수 있습니다. 

```bash
# Streamlit 앱 실행
uv run streamlit run app.py
```

* 정상적으로 실행되면 터미널에 `Local URL: http://localhost:8501`과 같은 주소가 출력됩니다.
* 브라우저가 자동으로 열리면서 프로그램에 접속됩니다. (자동으로 열리지 않을 경우 출력된 URL을 브라우저 주소창에 직접 입력하세요.)
* 화면 좌측 **사이드바(설정)** 영역에서 발급받으신 **Gemini API Key**를 입력하신 후 바로 이용하실 수 있습니다. (서버 환경 변수로 `GEMINI_API_KEY`를 등록해 둘 경우, 입력 없이 자동으로 실행됩니다.)
