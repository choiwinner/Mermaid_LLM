# Node.js 및 의존성 완벽 재설치 가이드 (Windows)

이 가이드는 기존의 Node.js 환경을 완전히 비우고, **Node.js v24.14.1 (LTS)** 환경에서 프로젝트 의존성을 새롭게 설정하는 과정을 설명합니다.

---

## 1단계: 기존 Node.js 삭제
1.  **제어판** > **프로그램 및 기능** (또는 설정 > 앱)으로 이동합니다.
2.  목록에서 **Node.js**를 찾아 **제거**합니다.

---

## 2단계: 잔류 폴더 및 캐시 수동 삭제
Node.js를 삭제해도 환경 설정과 패키지 매니저(`npm`, `pnpm`)의 캐시 데이터는 남아있을 수 있습니다. 아래 경로들을 복사하여 탐색기 주소창에 입력한 뒤, 해당 폴더들을 **모두 삭제**해 주세요.

### 🗑️ 삭제 대상 목록 (복사해서 탐색기 주소창에 입력)
*   ** `%AppData%\npm`** (전역 실행 파일 폴더)
*   ** `%AppData%\npm-cache`** (npm 캐시 폴더)
*   ** `%AppData%\pnpm`** (pnpm 설정 및 바이너리 폴더)
*   ** `%LocalAppData%\pnpm`** (pnpm 저장소 및 캐시 폴더)

> [!IMPORTANT]
> 폴더가 존재하지 않는다면 이미 삭제된 것이므로 다음 단계로 넘어가셔도 됩니다.

---

## 3단계: Node.js v24.14.1 (LTS) 설치
1.  [Node.js 공식 사이트](https://nodejs.org/en)에서 **v24.14.1 (LTS)** 버전을 다운로드하거나 [Prebuilt Binaries](https://nodejs.org/en/download/prebuilt-binaries)를 이용합니다.
2.  다운로드된 설치 파일을 실행하여 설치를 완료합니다.
3.  설치 완료 후 **재부팅**을 권장합니다 (환경 변수 적용을 위해).

---

## 4단계: 설치 확인 및 pnpm 재설치
터미널(PowerShell 또는 CMD)을 열고 다음 명령어를 실행하여 설치 상태를 확인합니다.

```powershell
# 1. 버전 확인
node -v  # v24.14.1 출력 확인
npm -v

# 2. pnpm 재설치 (방법 A 또는 B 중 선택)

# 방법 A: npm으로 전역 설치 (추천)
npm install -g pnpm

# 방법 B: Corepack 활성화 (Node.js 내장 관리 기능 사용 시)
corepack enable
```

---

## 5단계: 프로젝트 의존성 재설치 (`Mermaid_LLM`)
프로젝트 폴더(`c:\python\Mermaid_LLM`)로 이동하여 기존 설치 내역을 지우고 깨끗하게 다시 설치합니다.

```powershell
# 1. 기존 node_modules 삭제 (이전 버전의 산물 제거)
rm -r node_modules

# 2. 의존성 새로 설치 (pnpm-lock.yaml 기준)
pnpm install

# 3. 프로젝트 빌드 확인 (Mermaid 라이브러리 재생성)
pnpm run build
```

---

## 6단계: Python 환경 확인 (참고)
이 프로젝트의 Streamlit 앱(`app.py`)은 Node.js가 아닌 **Python 환경**에서 작동합니다. Node.js 재설치는 Python 가상환경(`uv`)에 영향을 주지 않으므로, 앱 실행은 기존처럼 진행하시면 됩니다.

```powershell
# 예시: 가상환경으로 앱 실행
uv run streamlit run app.py
```

---
**가이드 작성 완료.** 모든 과정을 안전하게 진행하시기 바랍니다!
