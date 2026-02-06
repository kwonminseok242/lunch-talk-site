# lunch-talk-questions

현직자 런치톡을 위한 **질문 수집 웹**입니다.  
같은 네트워크에서 접속해 질문을 남기고, 관리자 페이지에서 질문을 관리할 수 있습니다.

## 주요 기능
- 질문 등록 및 목록 조회
- 좋아요(공감) 기능
- 관리자 페이지: 질문 관리, 통계, 일괄 삭제
- Google Sheets 연동 (영구 저장) + SQLite 백업
- 다크 글래스모피즘 UI

## 페이지 구성
- 메인: 질문 작성/목록
- 관리자: 질문 관리/통계/설정

## 데이터 저장 방식
1. **Google Sheets (권장, 영구 저장)**
2. **SQLite (임시 백업)**
3. **JSON (호환용)**

> Streamlit Cloud 재시작 시 로컬 파일(SQLite/JSON)은 사라질 수 있으므로  
> **Service Account를 통한 Google Sheets 영구 저장을 권장**합니다.

## 로컬 실행
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Cloud 배포
1. GitHub에 푸시
2. Streamlit Cloud에서 앱 생성
3. `Manage app` → `Secrets`에 Google Sheets 설정 입력
4. 재배포 후 관리자 페이지에서 연결 테스트

## Google Sheets 연결
- 공개 읽기 + Service Account 쓰기 설정 권장
- 가이드: `GOOGLE_SHEETS_SERVICE_ACCOUNT_SETUP.md`

