## Google Sheets Service Account 설정 가이드

이 설정을 완료하면 **읽기 + 쓰기 모두 가능**하고, Streamlit이 꺼져도 데이터가 **Google Sheets에 영구 저장**됩니다.

### 1) Google Cloud 프로젝트 생성
- https://console.cloud.google.com 접속
- 새 프로젝트 생성

### 2) Google Sheets API 활성화
- “API 및 서비스” → “라이브러리”
- “Google Sheets API” 검색 → 활성화

### 3) 서비스 계정 생성
- “API 및 서비스” → “사용자 인증 정보”
- “사용자 인증 정보 만들기” → “서비스 계정”
- 이름 입력 후 생성

### 4) JSON 키 생성/다운로드
- 생성한 서비스 계정 클릭
- “키” 탭 → “키 추가” → “JSON”
- 다운로드된 JSON 파일 보관

### 5) Google Sheets 공유
- Google Sheets 열기 → “공유” 버튼
- **서비스 계정 이메일(client_email)** 추가
- 권한 **편집자**로 설정

### 6) Streamlit Cloud Secrets 설정
Streamlit Cloud → “Manage app” → “Secrets”에 아래 형식으로 입력

```toml
[connections.gsheets]
spreadsheet = "https://docs.google.com/spreadsheets/d/1lEauHDkNImWHV-TpGbqGoBxYpC8dE0MY3SMMBBo1z0k/edit?usp=sharing"
worksheet = "questions"
type = "service_account"
project_id = "YOUR_PROJECT_ID"
private_key_id = "YOUR_PRIVATE_KEY_ID"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n"
client_email = "YOUR_SERVICE_ACCOUNT_EMAIL"
client_id = "YOUR_CLIENT_ID"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/YOUR_SERVICE_ACCOUNT_EMAIL"
```

### 7) 확인
- 앱 재배포
- 관리자 페이지 → “연결 테스트”
- **읽기/쓰기 성공** 메시지 확인

---
문제가 있으면 JSON 키에서 필드 값을 정확히 복사했는지 확인해 주세요.
