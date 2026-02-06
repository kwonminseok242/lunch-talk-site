# 📊 Google Sheets 연동 설정 가이드

모든 사용자가 같은 질문 목록을 볼 수 있도록 Google Sheets를 연동하는 방법입니다.

## 🚀 설정 단계

### 1단계: Google Sheets 생성

1. [Google Sheets](https://sheets.google.com) 접속
2. 새 스프레드시트 생성
3. 첫 번째 시트 이름을 `questions`로 변경 (또는 그대로 두기)
4. 첫 번째 행에 헤더 추가:
   ```
   id | name | question | timestamp | likes
   ```

### 2단계: Google Sheets 공유 설정

1. 스프레드시트 우측 상단 **"공유"** 버튼 클릭
2. **"링크가 있는 모든 사용자"** 선택
3. 권한: **"뷰어"** → **"편집자"**로 변경
4. **"완료"** 클릭

### 3단계: 스프레드시트 ID 확인

URL에서 스프레드시트 ID 확인:
```
https://docs.google.com/spreadsheets/d/[여기가_ID]/edit
```

예: `https://docs.google.com/spreadsheets/d/1ABC123xyz/edit`
→ ID는 `1ABC123xyz`

### 4단계: Streamlit Cloud Secrets 설정

1. Streamlit Cloud 대시보드 접속
2. 앱 선택 → **"Settings"** 클릭
3. **"Secrets"** 탭 클릭
4. 다음 내용 입력:

```toml
[connections.gsheets]
spreadsheet_id = "YOUR_SPREADSHEET_ID_HERE"
worksheet = "questions"
```

또는 URL 사용:

```toml
[connections.gsheets]
spreadsheet_url = "https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit"
worksheet = "questions"
```

5. **"Save"** 클릭

### 5단계: 앱 재배포

1. Streamlit Cloud에서 **"Reboot app"** 클릭
2. 또는 자동으로 재시작됨

## ✅ 확인 방법

1. 앱에 접속하여 질문 작성
2. Google Sheets에서 질문이 추가되는지 확인
3. 다른 브라우저/기기에서 접속하여 같은 질문이 보이는지 확인

## 🔧 문제 해결

### Google Sheets에 연결되지 않음

- **확인사항:**
  1. Secrets 설정이 올바른지 확인
  2. 스프레드시트 ID가 정확한지 확인
  3. 스프레드시트가 공유 설정되어 있는지 확인
  4. 앱을 재시작했는지 확인

### 권한 오류

- **해결:**
  1. 스프레드시트 공유 설정 확인
  2. "편집자" 권한으로 설정되어 있는지 확인
  3. "링크가 있는 모든 사용자"로 공유되어 있는지 확인

### 데이터가 표시되지 않음

- **해결:**
  1. Google Sheets에 헤더가 있는지 확인
  2. 시트 이름이 `questions`인지 확인 (또는 secrets에서 올바른 시트 이름 지정)
  3. 첫 번째 행에 데이터가 있는지 확인

## 📝 Google Sheets 구조

권장 컬럼 구조:

| id | name | question | timestamp | likes |
|----|------|----------|-----------|-------|
| 1 | 홍길동 | 질문 내용... | 2026-02-06 12:00:00 | 0 |
| 2 | 익명 | 질문 내용... | 2026-02-06 12:05:00 | 3 |

## 💡 팁

- Google Sheets에서 직접 데이터를 확인하고 수정할 수 있습니다
- 데이터 백업이 자동으로 됩니다
- 여러 사용자가 동시에 질문을 작성해도 충돌 없이 저장됩니다

---

설정이 완료되면 모든 사용자가 같은 질문 목록을 볼 수 있습니다! 🎉
