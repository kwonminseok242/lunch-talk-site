# 🔧 배포 오류 해결 가이드

## 문제: requirements 설치 오류

Streamlit Cloud에서 requirements 설치 오류가 발생하는 경우 해결 방법입니다.

## 해결 방법

### 방법 1: Google Sheets 없이 배포 (가장 간단)

`requirements.txt`를 최소 버전으로 변경:

```txt
streamlit>=1.28.0
pandas>=2.0.0
openpyxl>=3.1.0
```

이 경우 Google Sheets 연동 없이 로컬 파일 모드로 작동합니다.

### 방법 2: 패키지 버전 명시

현재 `requirements.txt`:
```txt
streamlit>=1.28.0
pandas>=2.0.0
openpyxl>=3.1.0
st-gsheets-connection
```

### 방법 3: 특정 버전 사용

```txt
streamlit==1.28.0
pandas==2.0.0
openpyxl==3.1.0
st-gsheets-connection==0.1.0
```

## 확인 사항

1. **패키지 이름 확인**
   - `st-gsheets-connection` (하이픈 포함)
   - 설치 후 import는 `from streamlit_gsheets import GSheetsConnection` 또는 `from st_gsheets_connection import GSheetsConnection`

2. **Streamlit Cloud 로그 확인**
   - Streamlit Cloud 대시보드 → 앱 선택 → "Manage app" → "Terminal" 탭
   - 오류 메시지 확인

3. **Python 버전 확인**
   - Streamlit Cloud는 기본적으로 Python 3.11 사용
   - `runtime.txt` 파일로 버전 지정 가능

## 빠른 해결책

Google Sheets가 필요 없다면 `requirements.txt`에서 `st-gsheets-connection` 라인을 제거하세요:

```txt
streamlit>=1.28.0
pandas>=2.0.0
openpyxl>=3.1.0
```

앱은 정상 작동하며, 로컬 파일 모드로 질문을 저장합니다.

## 추가 디버깅

터미널 로그에서 확인할 사항:
- 어떤 패키지에서 오류가 발생하는지
- Python 버전 호환성 문제인지
- 네트워크 문제인지

---

**참고**: Google Sheets 연동은 선택사항입니다. 없어도 앱은 정상 작동합니다!
