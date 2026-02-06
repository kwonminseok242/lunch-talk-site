"""
현직자 런치톡 질문 수집 웹사이트
우리은행 블루 컬러 테마 적용
"""

import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
from pathlib import Path

# 페이지 설정 (최상단)
st.set_page_config(
    page_title="현직자 런치톡 질문 수집",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 통계 추적 모듈
try:
    from utils_stats import track_visit, get_daily_stats, get_all_time_stats
    STATS_ENABLED = True
except ImportError:
    STATS_ENABLED = False

# Google Sheets 연동 (선택사항)
try:
    from st_gsheets_connection import GSheetsConnection
    USE_GSHEETS = True
except ImportError:
    try:
        from streamlit_gsheets import GSheetsConnection
        USE_GSHEETS = True
    except ImportError:
        USE_GSHEETS = False

# 세션 상태 초기화
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'sort_option' not in st.session_state:
    st.session_state.sort_option = "👍 좋아요 순"
if 'liked_questions' not in st.session_state:
    st.session_state.liked_questions = set()
if 'new_question_id' not in st.session_state:
    st.session_state.new_question_id = None

# 우리은행 블루 컬러
WOORI_BLUE = "#004C97"
WOORI_LIGHT_BLUE = "#0066CC"

# 데이터 파일 경로
DATA_FILE = "questions.json"
WORKSHEET_NAME = "questions"

# Google Sheets 연결 (설정되어 있으면 사용)
conn_gsheet = None
if USE_GSHEETS:
    try:
        conn_gsheet = st.connection("gsheets", type=GSheetsConnection)
        USE_GSHEETS = True
    except Exception:
        USE_GSHEETS = False
        conn_gsheet = None

def load_questions():
    """질문 데이터 로드 - Google Sheets 우선, 없으면 로컬 파일"""
    if USE_GSHEETS and conn_gsheet:
        try:
            df = conn_gsheet.read(worksheet=WORKSHEET_NAME, ttl=0)
            if df is not None and not df.empty:
                questions = df.to_dict('records')
                result = []
                for q in questions:
                    if 'question' in q and pd.notna(q.get('question')):
                        q['id'] = int(q.get('id', 0)) if pd.notna(q.get('id')) else 0
                        q['likes'] = int(q.get('likes', 0)) if pd.notna(q.get('likes')) else 0
                        q['name'] = str(q.get('name', '익명')) if pd.notna(q.get('name')) else '익명'
                        q['question'] = str(q['question'])
                        q['timestamp'] = str(q.get('timestamp', '')) if pd.notna(q.get('timestamp')) else ''
                        result.append(q)
                return result
        except Exception:
            pass
    
    # 로컬 파일 사용
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_questions(questions):
    """질문 데이터 저장 - Google Sheets 우선, 없으면 로컬 파일"""
    if USE_GSHEETS and conn_gsheet and questions:
        try:
            df = pd.DataFrame(questions)
            columns = ['id', 'name', 'question', 'timestamp', 'likes']
            df = df[columns] if all(col in df.columns for col in columns) else df
            conn_gsheet.update(worksheet=WORKSHEET_NAME, data=df)
            st.cache_data.clear()
            return
        except Exception:
            pass
    
    # 로컬 파일 저장
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"파일 저장 오류: {e}")

def add_question(name, question):
    """새 질문 추가"""
    questions = load_questions()
    new_id = len(questions) + 1
    new_question = {
        "id": new_id,
        "name": name,
        "question": question,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "likes": 0
    }
    questions.append(new_question)
    save_questions(questions)
    st.session_state.new_question_id = new_id
    return new_id

def like_question(question_id):
    """질문 좋아요 (중복 방지)"""
    if question_id in st.session_state.liked_questions:
        return
    
    questions = load_questions()
    for q in questions:
        if q["id"] == question_id:
            q["likes"] = q.get("likes", 0) + 1
            st.session_state.liked_questions.add(question_id)
            break
    save_questions(questions)
    st.rerun()

# 커스텀 CSS - 정리된 모던 디자인
st.markdown(f"""
<style>
    /* 전체 배경 */
    .main {{
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0f1419 100%);
        min-height: 100vh;
    }}
    
    /* 컨테이너 여백 줄이기 */
    .block-container {{
        background: transparent;
        padding: 1rem 2rem;
        margin-top: 0.5rem;
    }}
    
    /* 타이틀 스타일 - 크기 축소 */
    h1 {{
        color: #ffffff;
        font-weight: 700;
        font-size: 1.8rem;
        letter-spacing: -0.5px;
        margin-bottom: 0.5rem;
    }}
    
    h2 {{
        color: #ffffff;
        font-weight: 600;
        font-size: 1.3rem;
        margin-bottom: 0.5rem;
    }}
    
    h3 {{
        color: rgba(255, 255, 255, 0.9);
        font-weight: 600;
        font-size: 1.1rem;
    }}
    
    /* 버튼 - 통일된 스타일 */
    .stButton>button {{
        background: {WOORI_BLUE};
        color: white;
        border-radius: 12px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.2s ease;
    }}
    
    .stButton>button:hover {{
        background: {WOORI_LIGHT_BLUE};
        transform: translateY(-1px);
    }}
    
    /* 입력 필드 - 통일된 라운딩 */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea,
    .stSelectbox>div>div>select {{
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 12px;
        color: #ffffff;
        padding: 0.6rem 1rem;
        font-size: 0.95rem;
    }}
    
    .stTextInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus {{
        background: rgba(255, 255, 255, 0.12);
        border: 1px solid {WOORI_LIGHT_BLUE};
        outline: none;
    }}
    
    .stTextInput>div>div>input::placeholder,
    .stTextArea>div>div>textarea::placeholder {{
        color: rgba(255, 255, 255, 0.4);
    }}
    
    /* 질문 카드 - 간소화 */
    .question-card {{
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.12);
        margin-bottom: 1rem;
        transition: all 0.2s ease;
    }}
    
    .question-card:hover {{
        background: rgba(255, 255, 255, 0.1);
        border-color: rgba(255, 255, 255, 0.18);
    }}
    
    .question-card.new-question {{
        border: 2px solid {WOORI_LIGHT_BLUE};
        animation: highlight 2s ease;
    }}
    
    @keyframes highlight {{
        0% {{ border-color: {WOORI_LIGHT_BLUE}; }}
        100% {{ border-color: rgba(255, 255, 255, 0.12); }}
    }}
    
    .question-header {{
        color: #ffffff;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 0.8rem;
    }}
    
    .question-text {{
        color: rgba(255, 255, 255, 0.9);
        font-size: 1rem;
        line-height: 1.7;
        margin-bottom: 0.8rem;
        white-space: pre-wrap;
        word-wrap: break-word;
    }}
    
    .question-meta {{
        color: rgba(255, 255, 255, 0.6);
        font-size: 0.85rem;
        display: flex;
        justify-content: space-between;
        padding-top: 0.8rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }}
    
    /* 사이드바 스타일 */
    .css-1d391kg {{
        background: rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
    }}
    
    /* 메트릭 스타일 - 레이블 명확하게 */
    [data-testid="stMetricContainer"] {{
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }}
    
    [data-testid="stMetricValue"] {{
        color: #ffffff;
        font-weight: 700;
        font-size: 1.5rem;
    }}
    
    [data-testid="stMetricLabel"] {{
        color: rgba(255, 255, 255, 0.8);
        font-size: 0.9rem;
        font-weight: 500;
    }}
    
    /* 빈 상태 카드 - 작게 */
    .empty-state {{
        background: rgba(255, 255, 255, 0.06);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
    }}
    
    /* 체크박스/라디오 스타일 */
    .stCheckbox label,
    .stRadio label {{
        color: rgba(255, 255, 255, 0.9);
    }}
</style>
""", unsafe_allow_html=True)

# 방문 추적
if STATS_ENABLED:
    try:
        track_visit()
    except:
        pass

# 헤더 영역 - 타이틀
st.markdown("""
<div style="padding: 0.5rem 0 1rem 0;">
    <h1 style="margin-bottom: 0.3rem;">💬 현직자 런치톡 질문 수집</h1>
    <p style="color: rgba(255, 255, 255, 0.6); font-size: 0.9rem; margin: 0;">
        함께 수강하는 분들의 질문을 모아서 현직자분께 전달하겠습니다
    </p>
</div>
""", unsafe_allow_html=True)

# KPI를 타이틀 아래로 배치 (명확한 레이블 포함)
all_questions = load_questions()
total_likes = sum(q.get("likes", 0) for q in all_questions)
current_visitors = 0
if STATS_ENABLED:
    try:
        from utils_stats import load_stats, get_current_visitors, get_daily_stats
        stats = load_stats()
        daily_stats = get_daily_stats(stats)
        current_visitors = daily_stats.get('current_visitors', 0)
    except:
        pass

kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
with kpi_col1:
    st.metric("📊 총 질문 수", len(all_questions))
with kpi_col2:
    st.metric("👍 총 좋아요", total_likes)
with kpi_col3:
    st.metric("👥 현재 접속", f"{current_visitors}명")

st.markdown("---")

# 본문을 2열로 분리: 좌측 폼, 우측 목록
col_form, col_list = st.columns([1, 1.5])

# 좌측: 질문 작성 폼
with col_form:
    st.markdown("### 📝 질문 작성")
    
    with st.form("question_form", clear_on_submit=True):
        use_name = st.checkbox("이름을 표시하시겠어요?", value=False)
        
        if use_name:
            name = st.text_input("이름", placeholder="예: 홍길동", max_chars=20)
        else:
            name = ""
            st.caption("ℹ️ 익명으로 질문이 등록됩니다")
        
        question = st.text_area(
            "질문 내용 *",
            placeholder="현직자분께 궁금한 점을 작성해주세요...\n\n예시:\n- 실무에서 가장 중요하게 생각하는 스킬은 무엇인가요?\n- 커리어 전환 시 고려해야 할 점은 무엇인가요?",
            height=200,
            max_chars=1000,
            help="질문 내용은 필수 입력 항목입니다 (최대 1000자)"
        )
        
        # 글자 수 표시
        if question:
            char_count = len(question)
            if char_count > 900:
                st.caption(f"⚠️ {char_count}/1000자 (거의 다 채웠습니다)")
            elif char_count > 0:
                st.caption(f"📝 {char_count}/1000자")
        
        submitted = st.form_submit_button("✅ 질문 등록하기", use_container_width=True, type="primary")
        
        if submitted:
            if question.strip():
                if len(question.strip()) > 1000:
                    st.error("⚠️ 질문은 1000자 이하로 작성해주세요.")
                else:
                    display_name = name.strip() if (use_name and name.strip()) else "익명"
                    new_id = add_question(display_name, question.strip())
                    st.success("✅ 질문이 등록되었습니다!")
                    st.rerun()
            else:
                st.error("⚠️ 질문 내용을 입력해주세요.")

# 우측: 질문 목록
with col_list:
    st.markdown("### 📋 등록된 질문 목록")
    
    # 검색 및 정렬 (통일된 스타일)
    search_col, sort_col = st.columns([2, 1])
    with search_col:
        search_input = st.text_input(
            "🔎 검색",
            placeholder="키워드로 검색...",
            key="search_main",
            value=st.session_state.search_query,
            label_visibility="collapsed"
        )
        if search_input != st.session_state.search_query:
            st.session_state.search_query = search_input
    
    with sort_col:
        sort_index = ["👍 좋아요 순", "🕒 최신순", "📝 작성자순"].index(st.session_state.sort_option)
        sort_select = st.selectbox(
            "정렬",
            ["👍 좋아요 순", "🕒 최신순", "📝 작성자순"],
            key="sort_main",
            label_visibility="collapsed",
            index=sort_index
        )
        if sort_select != st.session_state.sort_option:
            st.session_state.sort_option = sort_select
    
    # 질문 필터링 및 정렬
    questions = load_questions()
    if st.session_state.search_query:
        questions = [q for q in questions if st.session_state.search_query.lower() in q["question"].lower()]
    
    if st.session_state.sort_option == "👍 좋아요 순":
        questions_sorted = sorted(questions, key=lambda x: x.get("likes", 0), reverse=True)
    elif st.session_state.sort_option == "🕒 최신순":
        questions_sorted = sorted(questions, key=lambda x: x.get("timestamp", ""), reverse=True)
    elif st.session_state.sort_option == "📝 작성자순":
        questions_sorted = sorted(questions, key=lambda x: x.get("name", "익명"))
    else:
        questions_sorted = sorted(questions, key=lambda x: x.get("likes", 0), reverse=True)
    
    # 질문 목록 표시
    if not questions:
        if st.session_state.search_query:
            st.warning(f"🔍 '{st.session_state.search_query}'에 대한 검색 결과가 없습니다.")
            if st.button("🔍 검색 초기화", use_container_width=True):
                st.session_state.search_query = ""
                st.rerun()
        else:
            # 빈 상태 UI 개선 (작고 명확하게)
            st.markdown("""
            <div class="empty-state">
                <p style="color: rgba(255, 255, 255, 0.8); font-size: 1rem; margin-bottom: 1rem;">
                    아직 등록된 질문이 없습니다
                </p>
                <p style="color: rgba(255, 255, 255, 0.5); font-size: 0.85rem; margin: 0;">
                    왼쪽 폼에서 첫 번째 질문을 작성해보세요! 💡
                </p>
            </div>
            """, unsafe_allow_html=True)
    else:
        # 검색 결과 표시
        if st.session_state.search_query:
            st.info(f"🔍 '{st.session_state.search_query}' 검색 결과: {len(questions_sorted)}개")
        
        # 질문 개수 표시
        total_questions = len(load_questions())
        if len(questions_sorted) != total_questions:
            st.caption(f"전체 {total_questions}개 중 {len(questions_sorted)}개 표시")
        
        # 질문 카드 표시
        for idx, q in enumerate(questions_sorted, 1):
            name_display = q.get("name", "익명")
            is_anonymous = name_display == "익명"
            is_new = q['id'] == st.session_state.new_question_id
            
            card_class = "question-card new-question" if is_new else "question-card"
            
            st.markdown(f"""
            <div class="{card_class}">
                <div class="question-header">
                    #{idx} {name_display}{'님' if not is_anonymous else ''}의 질문
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
            
            col_like, col_space, col_id = st.columns([3, 7, 2])
            with col_like:
                if q['id'] in st.session_state.liked_questions:
                    st.button("✅ 좋아요 완료", key=f"like_{q['id']}", use_container_width=True, disabled=True)
                else:
                    if st.button("👍 좋아요", key=f"like_{q['id']}", use_container_width=True):
                        like_question(q["id"])
            with col_id:
                st.caption(f"#{q['id']}")
            
            st.markdown("---")
        
        # 새 질문 하이라이트 초기화
        if st.session_state.new_question_id:
            st.session_state.new_question_id = None

# 사이드바 - 필터만
with st.sidebar:
    st.markdown("### 🔍 필터 및 정렬")
    
    search_sidebar = st.text_input(
        "🔎 질문 검색",
        placeholder="키워드로 검색...",
        key="search_sidebar",
        value=st.session_state.search_query
    )
    if search_sidebar != st.session_state.search_query:
        st.session_state.search_query = search_sidebar
    
    st.markdown("---")
    
    sort_index = ["👍 좋아요 순", "🕒 최신순", "📝 작성자순"].index(st.session_state.sort_option)
    sort_sidebar = st.radio(
        "정렬 기준",
        ["👍 좋아요 순", "🕒 최신순", "📝 작성자순"],
        key="sort_sidebar",
        index=sort_index
    )
    if sort_sidebar != st.session_state.sort_option:
        st.session_state.sort_option = sort_sidebar
    
    st.markdown("---")
    
    # 관리자 페이지 링크
    with st.expander("🔐 관리자", expanded=False):
        if st.button("관리자 페이지 접속", use_container_width=True, type="secondary"):
            st.switch_page("pages/admin.py")
