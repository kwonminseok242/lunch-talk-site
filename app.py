"""
현직자 런치톡 질문 수집 웹사이트
우리은행 블루 컬러 테마 적용
"""

import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path

# 페이지 설정
st.set_page_config(
    page_title="현직자 런치톡 질문 수집",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 우리은행 블루 컬러
WOORI_BLUE = "#004C97"
WOORI_LIGHT_BLUE = "#0066CC"
WOORI_WHITE = "#FFFFFF"

# 데이터 파일 경로
DATA_FILE = "questions.json"

def load_questions():
    """질문 데이터 로드"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_questions(questions):
    """질문 데이터 저장"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

def add_question(name, question):
    """새 질문 추가"""
    questions = load_questions()
    new_question = {
        "id": len(questions) + 1,
        "name": name,
        "question": question,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "likes": 0
    }
    questions.append(new_question)
    save_questions(questions)
    return questions

def like_question(question_id):
    """질문 좋아요"""
    questions = load_questions()
    for q in questions:
        if q["id"] == question_id:
            q["likes"] = q.get("likes", 0) + 1
            break
    save_questions(questions)
    st.rerun()

# 커스텀 CSS
st.markdown(f"""
<style>
    .main {{
        background-color: {WOORI_WHITE};
    }}
    .stButton>button {{
        background-color: {WOORI_BLUE};
        color: white;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        border: none;
        transition: all 0.3s;
    }}
    .stButton>button:hover {{
        background-color: {WOORI_LIGHT_BLUE};
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 76, 151, 0.3);
    }}
    .question-card {{
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid {WOORI_BLUE};
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }}
    .question-header {{
        color: {WOORI_BLUE};
        font-weight: bold;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }}
    .question-text {{
        color: #333;
        font-size: 1rem;
        line-height: 1.6;
        margin-bottom: 0.5rem;
    }}
    .question-meta {{
        color: #666;
        font-size: 0.85rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .like-button {{
        background-color: {WOORI_LIGHT_BLUE};
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.3rem 0.8rem;
        cursor: pointer;
        font-size: 0.85rem;
    }}
    h1 {{
        color: {WOORI_BLUE};
        text-align: center;
        padding-bottom: 1rem;
        border-bottom: 3px solid {WOORI_BLUE};
    }}
    .stTextInput>div>div>input {{
        border: 2px solid {WOORI_BLUE};
        border-radius: 5px;
    }}
    .stTextArea>div>div>textarea {{
        border: 2px solid {WOORI_BLUE};
        border-radius: 5px;
    }}
</style>
""", unsafe_allow_html=True)

# 메인 타이틀
st.markdown(f"""
<div style="text-align: center; padding: 2rem 0;">
    <h1 style="color: {WOORI_BLUE}; margin-bottom: 0.5rem;">💬 현직자 런치톡 질문 수집</h1>
    <p style="color: #666; font-size: 1.1rem;">함께 수강하는 분들의 질문을 모아서 현직자분께 전달하겠습니다</p>
</div>
""", unsafe_allow_html=True)

# 사이드바 - 질문 작성 및 필터
with st.sidebar:
    st.markdown(f"""
    <div style="background-color: {WOORI_BLUE}; padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;">
        <h2 style="color: white; margin: 0; text-align: center;">📝 질문 작성</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # 익명 옵션 (기본값: 익명)
    use_name = st.checkbox("이름을 표시하시겠어요?", value=False, help="체크 해제 시 '익명'으로 표시됩니다")
    
    if use_name:
        name = st.text_input("이름", placeholder="예: 홍길동", help="이름을 입력하지 않으면 익명으로 표시됩니다")
    else:
        name = ""
        st.info("ℹ️ 익명으로 질문이 등록됩니다")
    
    question = st.text_area(
        "질문 내용 *",
        placeholder="현직자분께 궁금한 점을 작성해주세요...",
        height=150,
        help="질문 내용은 필수 입력 항목입니다"
    )
    
    if st.button("✅ 질문 등록하기", use_container_width=True, type="primary"):
        if question.strip():
            display_name = name.strip() if (use_name and name.strip()) else "익명"
            add_question(display_name, question.strip())
            st.success("✅ 질문이 등록되었습니다!")
            st.balloons()
            st.rerun()
        else:
            st.error("⚠️ 질문 내용을 입력해주세요.")
    
    st.markdown("---")
    
    # 필터 및 정렬 옵션
    st.markdown("### 🔍 필터 및 정렬")
    search_query = st.text_input("🔎 질문 검색", placeholder="키워드로 검색...", help="질문 내용에서 검색합니다")
    
    sort_option = st.radio(
        "정렬 기준",
        ["👍 좋아요 순", "🕒 최신순", "📝 작성자순"],
        help="질문 목록을 정렬하는 기준을 선택하세요"
    )

# 메인 영역 - 질문 목록
col_title, col_info = st.columns([3, 1])
with col_title:
    st.markdown("## 📋 등록된 질문 목록")
with col_info:
    questions = load_questions()
    if questions:
        st.caption(f"총 {len(questions)}개")

questions = load_questions()

# 검색 필터 적용
if 'search_query' in locals() and search_query:
    questions = [q for q in questions if search_query.lower() in q["question"].lower()]

if not questions:
    if 'search_query' in locals() and search_query:
        st.warning(f"🔍 '{search_query}'에 대한 검색 결과가 없습니다.")
    else:
        st.info("아직 등록된 질문이 없습니다. 첫 번째 질문을 작성해보세요! 💡")
else:
    # 정렬 옵션에 따라 정렬
    if 'sort_option' in locals():
        if sort_option == "👍 좋아요 순":
            questions_sorted = sorted(questions, key=lambda x: x.get("likes", 0), reverse=True)
        elif sort_option == "🕒 최신순":
            questions_sorted = sorted(questions, key=lambda x: x.get("timestamp", ""), reverse=True)
        elif sort_option == "📝 작성자순":
            questions_sorted = sorted(questions, key=lambda x: x.get("name", "익명"))
        else:
            questions_sorted = sorted(questions, key=lambda x: x.get("likes", 0), reverse=True)
    else:
        questions_sorted = sorted(questions, key=lambda x: x.get("likes", 0), reverse=True)
    
    # 검색 결과 표시
    if 'search_query' in locals() and search_query:
        st.success(f"🔍 '{search_query}' 검색 결과: {len(questions_sorted)}개")
    
    for idx, q in enumerate(questions_sorted, 1):
        with st.container():
            # 질문 번호와 작성자 정보
            name_display = q.get("name", "익명")
            is_anonymous = name_display == "익명"
            
            st.markdown(f"""
            <div class="question-card">
                <div class="question-header">
                    #{idx} {name_display}{'님' if not is_anonymous else ''}의 질문
                    {'<span style="color: #999; font-size: 0.9rem;">(익명)</span>' if is_anonymous else ''}
                </div>
                <div class="question-text">
                    {q["question"]}
                </div>
                <div class="question-meta">
                    <span>🕒 {q["timestamp"]}</span>
                    <span>👍 좋아요 {q.get("likes", 0)}개</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([2, 8, 2])
            with col1:
                if st.button("👍 좋아요", key=f"like_{q['id']}", use_container_width=True):
                    like_question(q["id"])
            with col3:
                st.caption(f"질문 #{q['id']}")
            
            st.markdown("---")

# 통계 정보
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("총 질문 수", len(questions))
with col2:
    total_likes = sum(q.get("likes", 0) for q in questions)
    st.metric("총 좋아요", total_likes)
with col3:
    if questions:
        avg_likes = total_likes / len(questions) if questions else 0
        st.metric("평균 좋아요", f"{avg_likes:.1f}")

# 푸터
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown(f"""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>💡 질문은 실시간으로 업데이트됩니다</p>
        <p>🔄 새로고침하면 최신 질문을 확인할 수 있습니다</p>
        <p style="color: {WOORI_BLUE}; font-weight: bold; margin-top: 1rem;">우리은행 FISA 부트캠프 💙</p>
    </div>
    """, unsafe_allow_html=True)

# 새로고침 버튼 (선택사항)
if st.button("🔄 새로고침", use_container_width=False):
    st.rerun()
