# 런치톡 질문 수집 웹 – 진행 과정 & 트러블슈팅

## 1) 프로젝트 목표
- 현직자 런치톡을 위해 질문을 수집/정리하는 웹앱 구축
- 같은 네트워크에서 누구나 접속 가능
- 관리자 페이지로 질문 관리/통계/삭제 기능 제공
- Streamlit Cloud 배포 및 **데이터 영구 저장** 확보

## 2) 주요 구현 흐름
1. **Streamlit 앱 기본 구성**
   - 메인: 질문 작성/목록
   - 관리자: 질문 관리/통계/설정
2. **UX 개선**
   - 입력 UX 개선(`st.form`, clear_on_submit)
   - KPI/섹션 레이아웃 재배치
3. **디자인 고도화**
   - 다크 모던/글래스모피즘 테마
   - 섹션 분리, 카드형 UI, 대비 강화
4. **데이터 저장 전략**
   - Google Sheets(우선) → SQLite → JSON
   - Streamlit Cloud 재시작 대비
5. **Google Sheets 연동**
   - 공개 시트 읽기(CSV export URL) 시도
   - 서비스 계정(Service Account) 인증 도입

## 3) 트러블슈팅 타임라인

### 3.1 Google Sheets 연결은 되는데 저장이 안 됨
**증상**
- 관리자 페이지에서 “연동됨” 메시지는 뜨지만 시트에 데이터가 안 보임

**원인**
- `st-gsheets-connection`이 내부적으로 URL 변환/읽기에서 실패
- 공개 시트는 **읽기만 가능**, 쓰기는 인증 필요

**해결**
- 관리자 페이지에 **연결 테스트** 추가
- CSV export URL 직접 접근으로 **읽기 성공 확인**
- 서비스 계정 인증 도입으로 **쓰기 가능** 전환

---

### 3.2 `Spreadsheet must be specified`
**증상**
- `spreadsheet`가 없다는 에러

**원인**
- Secrets에 `spreadsheet_id` 또는 `spreadsheet` 키 누락

**해결**
- Secrets 형식 통일
- `spreadsheet`/`spreadsheet_id` 둘 다 지원하도록 보강

---

### 3.3 HTTP 400: Bad Request
**증상**
- `read()` 호출 시 400 에러

**원인**
- 비공개 시트 접근
- 공개 URL 형식 혼동 (`?gid=0#gid=0` vs `?usp=sharing`)

**해결**
- 공개 링크(`?usp=sharing`) 사용 안내
- 시크릿 모드로 공개 여부 확인
- CSV export URL 직접 테스트 기능 추가

---

### 3.4 SyntaxError: return outside function
**증상**
- Streamlit 앱 로딩 실패

**원인**
- 관리자 페이지 내 `return`이 함수 밖에 존재

**해결**
- `return` → `st.stop()`로 수정

---

### 3.5 Service Account 적용 후 403 Permission Denied
**증상**
- `Google Sheets API has not been used...` 에러

**원인**
- GCP 프로젝트에서 **Google Sheets API 미활성화**

**해결**
- Google Sheets API 활성화 후 재시도

---

## 4) 최종 안정화 상태
- **읽기/쓰기 모두 Service Account 인증으로 동작**
- Streamlit 재시작에도 **Google Sheets 영구 저장**
- 관리자 페이지에서 연결 테스트/상태 확인 가능

## 5) 운영 팁
- 질문 데이터는 Google Sheets가 **단일 소스**가 되도록 유지
- 관리자 페이지에서 삭제/초기화 후 반드시 재확인
- Service Account JSON 키는 외부에 노출하지 않기

