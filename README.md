# 💬 현직자 런치톡 질문 수집 웹사이트

현직자 런치톡을 위한 질문 수집 웹사이트입니다. Streamlit Cloud로 배포하여 누구나 접근할 수 있습니다.

## 🚀 Streamlit Cloud 배포 방법

### 1단계: GitHub에 저장소 업로드

```bash
# Git 초기화
git init
git add .
git commit -m "Initial commit: Lunch talk questions app"

# GitHub에 새 저장소 생성 후
git remote add origin https://github.com/YOUR_USERNAME/lunch-talk-questions.git
git push -u origin main
```

### 2단계: Streamlit Cloud에 배포

1. [Streamlit Cloud](https://share.streamlit.io/) 접속
2. "New app" 클릭
3. GitHub 저장소 선택
4. Main file path: `app.py`
5. "Deploy" 클릭

### 3단계: 배포 완료!

배포가 완료되면 자동으로 URL이 생성됩니다:
- 예: `https://your-app-name.streamlit.app`

## ✨ 주요 기능

- ✅ **익명 질문**: 이름 표시 여부를 선택할 수 있습니다 (기본값: 익명)
- ✅ **질문 작성**: 간단하게 질문 작성 및 등록
- ✅ **질문 검색**: 키워드로 질문 검색
- ✅ **정렬 옵션**: 좋아요 순, 최신순, 작성자순 정렬
- ✅ **좋아요 기능**: 유용한 질문에 좋아요 표시
- ✅ **실시간 통계**: 총 질문 수, 좋아요 수 등 통계 확인
- ✅ **우리은행 블루 디자인**: 우리은행 핵심 컬러 적용

## 📋 사용 방법

### 질문 작성하기

1. 왼쪽 사이드바에서 질문 작성
2. **이름 표시 여부 선택**:
   - 체크 해제 (기본값): 익명으로 질문 등록
   - 체크: 이름을 입력하여 질문 등록
3. 질문 내용 입력
4. "✅ 질문 등록하기" 버튼 클릭

### 질문 확인하기

1. 메인 화면에서 등록된 모든 질문 확인
2. **검색 기능**: 사이드바에서 키워드로 검색
3. **정렬 옵션**: 좋아요 순, 최신순, 작성자순 선택
4. **좋아요 표시**: 각 질문의 "👍 좋아요" 버튼 클릭

## 🎨 디자인

- **메인 컬러**: 우리은행 블루 (#004C97)
- **보조 컬러**: 라이트 블루 (#0066CC)
- **배경**: 화이트 (#FFFFFF)
- **카드 디자인**: 깔끔한 카드 레이아웃

## 📁 파일 구조

```
lunch-talk-questions/
├── app.py                 # Streamlit 메인 애플리케이션
├── requirements.txt       # Python 의존성
├── .streamlit/
│   └── config.toml       # Streamlit 설정
├── questions.json         # 질문 데이터 (자동 생성)
└── README.md             # 이 파일
```

## 🔧 로컬에서 실행하기

```bash
# 의존성 설치
pip install -r requirements.txt

# 실행
streamlit run app.py
```

## 📝 데이터 저장

질문 데이터는 `questions.json` 파일에 저장됩니다. Streamlit Cloud에서는 세션별로 저장되므로, 영구 저장이 필요하면 데이터베이스 연동을 고려하세요.

## 💡 사용 팁

1. **익명 질문**: 이름을 표시하지 않고 싶다면 체크박스를 해제하세요
2. **검색 기능**: 많은 질문이 있을 때 키워드로 빠르게 찾을 수 있습니다
3. **정렬 기능**: 좋아요가 많은 질문을 먼저 보고 싶다면 "좋아요 순" 선택
4. **새로고침**: 새 질문을 확인하려면 "🔄 새로고침" 버튼 클릭

---

**우리은행 FISA 부트캠프** 💙
# lunch-talk-site
