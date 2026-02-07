# 런치톡 질문 수집 웹 – 진행 과정 & 트러블슈팅 (상세)

본 문서는 **런치톡 질문 수집 웹**을 구축하면서 겪은 전체 과정과 이슈 해결 기록을 회귀용으로 정리한 문서입니다.  
특히 **Streamlit Cloud + Google Sheets 영구 저장** 구성에서 발생한 문제와 해결 방식에 집중했습니다.

---

## 1) 프로젝트 목표 및 제약
### 목표
- 현직자 런치톡을 위해 **질문을 수집/정리**하는 웹앱 구축
- 같은 네트워크(또는 인터넷)에서 누구나 접속 가능
- **관리자 페이지**에서 질문 관리/통계/일괄 삭제 제공
- Streamlit Cloud 배포 + **데이터 영구 저장**

### 제약
- Streamlit Cloud는 **ephemeral filesystem** → SQLite/JSON은 재시작 시 사라질 수 있음
- Google Sheets는 **쓰기 시 인증 필요**

---

## 2) 구현 구조 요약
### 페이지
- **메인**: 질문 작성/목록/좋아요
- **관리자**: 질문 관리, 통계, 데이터 상태 확인

### 데이터 저장 전략 (우선순위)
1. **Google Sheets** (Service Account로 읽기/쓰기)
2. **SQLite** (임시 백업)
3. **JSON** (마이그레이션/호환)

---

## 3) 구현 과정 상세
### 3.1 기본 기능 구축
- 질문 등록/목록, 좋아요, 관리자 페이지 기본 UI 구현
- Streamlit의 `st.form`으로 입력 UX 개선
- KPI/헤더 구성 및 섹션 분리

### 3.2 디자인 개선
- 다크 모던 + 글래스모피즘 테마 적용
- 대비/가독성 개선 및 카드형 UI 구성
- 메인/관리자 페이지 스타일 통일

### 3.3 데이터 저장 안정화
- 로컬 JSON → SQLite로 마이그레이션
- Google Sheets가 동작할 경우 이를 우선 저장
- 실패 시 SQLite로 fallback

---

## 4) 트러블슈팅 상세 타임라인

### 4.1 Google Sheets 연결은 되는데 저장이 안 됨
**증상**
- 관리자 페이지에 “연동됨” 메시지는 보이지만 시트에 데이터 없음

**원인**
- 공개 시트는 읽기만 가능
- `st-gsheets-connection` 내부 URL 변환/읽기 실패 가능

**조치**
- 관리자 페이지에 **연결 테스트 버튼** 추가
- CSV export URL 직접 접근으로 **읽기 성공 확인**
- 쓰기 가능하게 하려면 **Service Account 인증 필요**로 결론

---

### 4.2 `Spreadsheet must be specified`
**증상**
- `spreadsheet`가 없다는 에러

**원인**
- Secrets에 `spreadsheet` 또는 `spreadsheet_id` 누락

**조치**
- Secrets 형식 예시 제공
- `spreadsheet`/`spreadsheet_id` 모두 지원하도록 코드 보강

---

### 4.3 HTTP 400: Bad Request
**증상**
- `conn_gsheet.read()` 호출 시 400 에러

**원인**
- 비공개 시트 접근
- URL 형식 혼동 (`?gid=0#gid=0` vs `?usp=sharing`)

**조치**
- 공개 링크(`?usp=sharing`)만 사용하도록 안내
- **시크릿 모드에서 로그인 없이 열리는지**로 공개 여부 확인
- CSV export URL 직접 테스트 기능 추가

---

### 4.4 SyntaxError: return outside function
**증상**
- Streamlit 페이지 로딩 실패

**원인**
- 관리자 페이지 내 `return`이 함수 밖에 존재

**조치**
- `return` → `st.stop()`로 수정

---

### 4.5 Service Account 적용 후 403 Permission Denied
**증상**
- `Google Sheets API has not been used...` 에러

**원인**
- GCP 프로젝트에서 **Google Sheets API 미활성화**

**조치**
- Google Sheets API 활성화 후 재시도  
- 활성화 반영까지 수 분 대기

---

### 4.6 SQLite 저장 오류: UNIQUE constraint failed
**증상**
- `SQLite 저장 오류: UNIQUE constraint failed: questions.id`
- 동시에 `StreamlitDuplicateElementKey` 발생

**원인**
- 질문 `id`가 중복으로 저장됨
- 삭제 버튼 key가 `delete_{id}` 형태라 **id 중복 시 버튼 키도 중복**

**조치**
- **id 정규화 함수(`normalize_question_ids`)** 추가
  - 중복/0/비정상 id를 순차적으로 재부여
  - 저장 직전/로드 직후에 자동 정리
- 새 질문 id는 `len()`이 아니라 **`max(id)+1`** 방식으로 변경

---

## 5) 최종 안정화 상태
- Service Account 인증으로 **Google Sheets 읽기/쓰기 정상**
- Streamlit 재시작 시에도 **Google Sheets 영구 저장**
- 관리자 페이지에서 **연결 테스트/상태 확인 가능**
- id 충돌 및 Streamlit 키 중복 문제 해결

---

## 6) 운영 팁
- Google Sheets를 **단일 소스**로 유지
- 관리자 삭제/초기화 후 시트 반영 여부 확인
- Service Account JSON 키는 외부 노출 금지
- Streamlit Cloud 배포 시 Secrets 변경 후 **재배포 + 연결 테스트 필수**

---

## 7) 참고 문서
- `GOOGLE_SHEETS_SERVICE_ACCOUNT_SETUP.md`
- `GOOGLE_SHEETS_URL_GUIDE.md`
- `DATA_PERSISTENCE_GUIDE.md`

