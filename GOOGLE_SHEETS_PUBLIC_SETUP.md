# Google Sheets 공개 설정 가이드

`st-gsheets-connection` 패키지는 **공개(Public)로 설정된 Google Sheets**만 지원합니다.

## 🚀 빠른 설정 방법 (권장)

### 1단계: Google Sheets 공개 설정

1. Google Sheets를 엽니다: `https://docs.google.com/spreadsheets/d/1lEauHDkNImWHV-TpGbqGoBxYpC8dE0MY3SMMBBo1z0k/edit`

2. 오른쪽 상단의 **"공유"** 버튼을 클릭합니다.

3. 공유 설정 창에서:
   - **"링크가 있는 모든 사용자"** 선택
   - 권한을 **"편집자"** 또는 **"뷰어"**로 설정
   - **"완료"** 클릭

4. URL이 다음과 같은 형식인지 확인:
   ```
   https://docs.google.com/spreadsheets/d/1lEauHDkNImWHV-TpGbqGoBxYpC8dE0MY3SMMBBo1z0k/edit?usp=sharing
   ```

### 2단계: Streamlit Cloud Secrets 설정

Streamlit Cloud → "Manage app" → "Secrets"에서:

```toml
[connections.gsheets]
spreadsheet = "https://docs.google.com/spreadsheets/d/1lEauHDkNImWHV-TpGbqGoBxYpC8dE0MY3SMMBBo1z0k/edit?usp=sharing"
worksheet = "questions"
```

또는:

```toml
[connections.gsheets]
spreadsheet_id = "1lEauHDkNImWHV-TpGbqGoBxYpC8dE0MY3SMMBBo1z0k"
worksheet = "questions"
```

### 3단계: 워크시트 헤더 확인

Google Sheets의 첫 번째 행에 다음 헤더가 있는지 확인:

| id | name | question | timestamp | likes |
|----|------|----------|-----------|-------|

### 4단계: 테스트

앱을 재배포한 후 관리자 페이지의 **"🔧 Google Sheets 연결 테스트"** 버튼을 클릭하여 확인하세요.

---

## ❓ 문제 해결

### HTTP Error 400: Bad Request
- **원인**: Google Sheets가 비공개로 설정되어 있음
- **해결**: 위의 1단계를 따라 공개 설정

### "Spreadsheet must be specified" 오류
- **원인**: Secrets에 `spreadsheet` 또는 `spreadsheet_id`가 없음
- **해결**: Streamlit Cloud Secrets에 올바른 설정 추가

### 데이터가 저장되지 않음
- **원인**: 공개 설정이 되어 있지만 권한이 "뷰어"로만 설정됨
- **해결**: 권한을 "편집자"로 변경

---

## 🔒 비공개 시트를 사용하려면?

비공개 시트를 사용하려면 Google Cloud Service Account 인증이 필요합니다. 이는 더 복잡하므로, 가능하면 공개 설정을 권장합니다.

비공개 시트 설정이 필요하다면 `GOOGLE_SHEETS_SERVICE_ACCOUNT_SETUP.md` 파일을 참고하세요.
