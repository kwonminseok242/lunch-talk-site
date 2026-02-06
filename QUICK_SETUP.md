# 🚀 빠른 설정 가이드

## Google Sheets 연결 설정

### 스프레드시트 ID 추출

제공하신 URL:
```
https://docs.google.com/spreadsheets/d/1lEauHDkNImWHV-TpGbqGoBxYpC8dE0MY3SMMBBo1z0k/edit?gid=0#gid=0
```

**스프레드시트 ID**: `1lEauHDkNImWHV-TpGbqGoBxYpC8dE0MY3SMMBBo1z0k`

---

## 📝 Streamlit Cloud Secrets 작성법

### 1. Streamlit Cloud 접속
- [Streamlit Cloud](https://share.streamlit.io/) 접속
- 앱 선택 → **Settings** → **Secrets** 탭

### 2. Secrets 입력

다음 내용을 **정확히** 입력하세요:

```toml
[connections.gsheets]
spreadsheet_id = "1lEauHDkNImWHV-TpGbqGoBxYpC8dE0MY3SMMBBo1z0k"
worksheet = "questions"
```

**주의사항**:
- `[connections.gsheets]`는 대괄호 포함
- `spreadsheet_id`와 `worksheet`는 소문자
- 등호(`=`) 앞뒤에 공백 가능
- 따옴표(`"`)로 감싸기
- 마지막에 쉼표 없음

### 3. Save 및 재시작
- **Save** 버튼 클릭
- **Reboot app** 클릭

---

## 💻 로컬 테스트 방법

### 1. secrets.toml 파일 생성

프로젝트 폴더에서:

```bash
cd lunch-talk-questions
```

`.streamlit/secrets.toml` 파일 생성:

```bash
# Windows (PowerShell)
New-Item -Path .streamlit\secrets.toml -ItemType File -Force

# Mac/Linux
touch .streamlit/secrets.toml
```

### 2. secrets.toml 파일 편집

텍스트 에디터로 `.streamlit/secrets.toml` 파일을 열고 다음 내용 입력:

```toml
[connections.gsheets]
spreadsheet_id = "1lEauHDkNImWHV-TpGbqGoBxYpC8dE0MY3SMMBBo1z0k"
worksheet = "questions"
```

**파일 위치**: `lunch-talk-questions/.streamlit/secrets.toml`

### 3. 앱 실행

```bash
streamlit run app.py
```

### 4. 연결 확인

1. 브라우저에서 앱 접속
2. 사이드바 → "🔐 관리자" → "관리자 페이지 접속"
3. 비밀번호: `woori2024`
4. "⚙️ 설정" 탭 클릭
5. "📊 데이터 저장 상태" 확인
   - ✅ **"Google Sheets에 저장 중 (영구 저장)"** 메시지가 보이면 성공!

### 5. 테스트

1. 메인 페이지에서 질문 등록
2. Google Sheets를 새로고침하여 질문이 추가되었는지 확인

---

## ⚠️ 중요 확인사항

### Google Sheets 공유 설정 확인

1. Google Sheets 접속
2. 우측 상단 **"공유"** 버튼 클릭
3. **"링크가 있는 모든 사용자"** 선택되어 있는지 확인
4. 권한이 **"편집자"**인지 확인
5. **완료** 클릭

### 헤더 확인

Google Sheets 첫 번째 행에 다음 헤더가 있는지 확인:

| A | B | C | D | E |
|---|---|---|---|---|
| id | name | question | timestamp | likes |

---

## 🔍 문제 해결

### 연결이 안 될 때

1. **공유 설정 확인**
   - "링크가 있는 모든 사용자" + "편집자" 권한

2. **Secrets 확인**
   - `spreadsheet_id` 값이 정확한지 확인
   - 따옴표 포함 여부 확인
   - 오타 없는지 확인

3. **시트 이름 확인**
   - Google Sheets 하단의 시트 이름이 `questions`인지 확인
   - 또는 첫 번째 시트 이름 확인

4. **앱 재시작**
   - Streamlit Cloud: "Reboot app"
   - 로컬: Ctrl+C 후 `streamlit run app.py`

---

## 📋 체크리스트

- [ ] Google Sheets 헤더 추가 완료
- [ ] 공유 설정 완료 ("편집자" 권한)
- [ ] 스프레드시트 ID 확인 완료
- [ ] Streamlit Cloud Secrets 설정 완료
- [ ] 로컬 secrets.toml 파일 생성 완료
- [ ] 앱 재시작 완료
- [ ] 관리자 페이지에서 "Google Sheets에 저장 중" 확인
- [ ] 질문 등록 후 Google Sheets에서 확인

---

**설정이 완료되면 모든 사용자가 같은 질문 목록을 볼 수 있습니다!** 🎉
