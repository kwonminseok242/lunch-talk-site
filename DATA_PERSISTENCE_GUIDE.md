# 데이터 영구 저장 가이드

## ⚠️ 중요: Streamlit Cloud의 데이터 저장

Streamlit Cloud는 **ephemeral filesystem**을 사용합니다. 즉:
- 앱이 재시작되면 SQLite 파일(`questions.db`)이 **사라질 수 있습니다**
- JSON 파일도 마찬가지로 **사라질 수 있습니다**

## ✅ 해결 방법: Google Sheets 영구 저장

데이터를 영구적으로 보존하려면 **Google Sheets에 저장**해야 합니다.

### 현재 상태

1. **읽기**: ✅ CSV export URL로 직접 읽기 (작동 중)
2. **쓰기**: ⚠️ Service Account 인증 필요 (설정 필요)

### Google Sheets 쓰기 설정 방법

공개 시트에 쓰려면 **Service Account 인증**이 필요합니다.

#### 방법 1: Service Account 설정 (권장)

1. **Google Cloud Console에서 프로젝트 생성**
   - https://console.cloud.google.com/ 접속
   - 새 프로젝트 생성

2. **Google Sheets API 활성화**
   - "API 및 서비스" → "라이브러리"
   - "Google Sheets API" 검색 후 활성화

3. **Service Account 생성**
   - "API 및 서비스" → "사용자 인증 정보"
   - "사용자 인증 정보 만들기" → "서비스 계정"
   - 이름 입력 후 생성

4. **JSON 키 다운로드**
   - 생성된 Service Account 클릭
   - "키" 탭 → "키 추가" → "JSON" 선택
   - JSON 파일 다운로드

5. **Google Sheets 공유**
   - Google Sheets 열기
   - "공유" 버튼 클릭
   - Service Account 이메일 주소 추가 (JSON 파일의 `client_email` 필드)
   - 권한: **"편집자"**

6. **Streamlit Cloud Secrets 설정**
   ```toml
   [connections.gsheets]
   spreadsheet = "https://docs.google.com/spreadsheets/d/1lEauHDkNImWHV-TpGbqGoBxYpC8dE0MY3SMMBBo1z0k/edit?usp=sharing"
   worksheet = "questions"
   
   # Service Account 인증 정보
   type = "service_account"
   project_id = "your-project-id"
   private_key_id = "your-private-key-id"
   private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
   client_email = "your-service-account@your-project.iam.gserviceaccount.com"
   client_id = "your-client-id"
   auth_uri = "https://accounts.google.com/o/oauth2/auth"
   token_uri = "https://oauth2.googleapis.com/token"
   auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
   client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
   ```

#### 방법 2: 현재 상태로 사용 (읽기만 가능)

현재 설정으로는:
- ✅ **읽기**: Google Sheets에서 데이터 읽기 가능
- ❌ **쓰기**: SQLite에만 저장 (앱 재시작 시 사라질 수 있음)

**임시 해결책**: 
- 데이터는 SQLite에 저장됩니다
- 앱이 재시작되기 전까지는 데이터가 유지됩니다
- **장기적으로는 Service Account 설정을 권장합니다**

## 📊 데이터 저장 우선순위

현재 코드는 다음 순서로 저장을 시도합니다:

1. **Google Sheets** (쓰기 인증 필요)
2. **SQLite** (`questions.db`) - 앱 재시작 시 사라질 수 있음
3. **JSON** (`questions.json`) - 앱 재시작 시 사라질 수 있음

## 🔍 현재 저장 상태 확인

관리자 페이지 → "⚙️ 설정" 탭 → "📊 데이터 저장 상태"에서 확인할 수 있습니다.

## 💡 권장 사항

**프로덕션 환경에서는 반드시 Google Sheets Service Account를 설정하세요!**
