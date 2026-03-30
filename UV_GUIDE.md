# 🛠 UV를 이용한 프로젝트 설정 가이드

이 프로젝트는 최신 파이썬 패키지 관리자인 [uv](https://github.com/astral-sh/uv)를 사용합니다. `pip`보다 훨씬 빠르고 안정적인 환경을 제공하며, 단일 명령어로 전체 환경 구성을 완료할 수 있습니다.

## 1. 사전 준비 (uv 설치)
환경에 상관없이 아래 명령어로 `uv`를 먼저 설치하세요.

- **Windows (PowerShell):**
  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
- **macOS/Linux:**
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

## 2. 프로젝트 설정 (Clone 후 최초 1회)
저장소를 클론한 후, 프로젝트 루트 폴더에서 다음 시스템 명령어를 실행합니다.

```powershell
# 의존성 설치 및 가상환경(.venv) 자동 생성
uv sync
```
*이 명령어 하나로 `.python-version`에 적힌 파이썬 설치부터 모든 라이브러리 세팅이 자동 완료됩니다.*

## 3. 프로그램 실행
가상환경을 활성화하지 않고도 `uv run`으로 즉시 실행 가능합니다.

```powershell
# Gemini 버전 실행 (API Key 필요)
uv run streamlit run app_gemini.py

# Ollama(로컬) 버전 실행
uv run streamlit run app_ollama.py
```

## 4. 새로운 패키지 추가 시
```powershell
uv add 패키지명
```
실행 시 `pyproject.toml`과 `uv.lock`이 자동으로 업데이트됩니다. 변경 사항을 Git에 커밋해 주세요.
