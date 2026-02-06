# Google Sheets URL 설정 가이드

## ✅ 올바른 URL 형식

`st-gsheets-connection`을 사용하려면 **공개 공유 링크**를 사용해야 합니다.

### 올바른 URL (사용해야 할 것):
```
https://docs.google.com/spreadsheets/d/1lEauHDkNImWHV-TpGbqGoBxYpC8dE0MY3SMMBBo1z0k/edit?usp=sharing
```

### 잘못된 URL (사용하면 안 되는 것):
```
https://docs.google.com/spreadsheets/d/1lEauHDkNImWHV-TpGbqGoBxYpC8dE0MY3SMMBBo1z0k/edit?gid=0#gid=0
```

## 🔑 차이점 설명

### `?usp=sharing` (올바른 형식)
- **의미**: "Anyone with the link can view/edit" 공개 공유 링크
- **특징**: 로그인 없이 접근 가능
- **사용**: `st-gsheets-connection`이 CSV export를 위해 사용

### `?gid=0#gid=0` (잘못된 형식)
- **의미**: 일반 편집 링크 (비공개)
- **특징**: 로그인 필요
- **문제**: HTTP 400 오류 발생

## 📝 Streamlit Cloud Secrets 설정

Streamlit Cloud → "Manage app" → "Secrets"에서 다음 형식으로 설정:

```toml
[connections.gsheets]
spreadsheet = "https://docs.google.com/spreadsheets/d/1lEauHDkNImWHV-TpGbqGoBxYpC8dE0MY3SMMBBo1z0k/edit?usp=sharing"
worksheet = "questions"
```

또는 `spreadsheet_id`만 사용:

```toml
[connections.gsheets]
spreadsheet_id = "1lEauHDkNImWHV-TpGbqGoBxYpC8dE0MY3SMMBBo1z0k"
worksheet = "questions"
```

(코드에서 자동으로 `?usp=sharing`을 추가합니다)

## 🔧 공개 공유 링크 얻는 방법

1. Google Sheets를 엽니다
2. 오른쪽 상단의 **"공유"** 버튼 클릭
3. **"링크가 있는 모든 사용자"** 선택
4. 권한을 **"편집자"**로 설정
5. **"완료"** 클릭
6. URL이 `?usp=sharing`으로 끝나는지 확인

## ✅ 확인 방법

시크릿 모드(시크릿 창)에서 URL을 열어보세요:
- 로그인 없이 바로 열리면 ✅ 공개 설정 완료
- 로그인 화면이 나오면 ❌ 공개 설정 필요

## 🚨 주의사항

- `?gid=0#gid=0` 형식은 사용하지 마세요
- 반드시 `?usp=sharing` 형식을 사용하세요
- 공개 설정이 완료되어야 합니다
