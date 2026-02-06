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

# 페이지 설정
st.set_page_config(
    page_title="현직자 런치톡 질문 수집",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 세션 상태 초기화
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'sort_option' not in st.session_state:
    st.session_state.sort_option = "👍 좋아요 순"
if 'liked_questions' not in st.session_state:
    st.session_state.liked_questions = set()

# 우리은행 블루 컬러
WOORI_BLUE = "#004C97"
WOORI_LIGHT_BLUE = "#0066CC"
WOORI_WHITE = "#FFFFFF"

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
    """질문 좋아요 (중복 방지)"""
    # 이미 좋아요를 누른 질문인지 확인
    if question_id in st.session_state.liked_questions:
        st.warning("이미 좋아요를 누른 질문입니다")
        return
    
    questions = load_questions()
    for q in questions:
        if q["id"] == question_id:
            q["likes"] = q.get("likes", 0) + 1
            st.session_state.liked_questions.add(question_id)
            break
    save_questions(questions)
    st.success("👍 좋아요가 반영되었습니다!")
    st.rerun()

# 커스텀 CSS - 애플 스타일 Liquid Glass 디자인
st.markdown(f"""
<style>
    /* 전체 배경 그라데이션 */
    .main {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #004C97 50%, #0066CC 75%, #004C97 100%);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        min-height: 100vh;
    }}
    
    @keyframes gradientShift {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}
    
    /* 스트림릿 컨테이너 유리 효과 */
    .block-container {{
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.18);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        padding: 2rem;
        margin-top: 1rem;
    }}
    
    /* 버튼 - Liquid Glass 효과 */
    .stButton>button {{
        background: linear-gradient(135deg, rgba(0, 76, 151, 0.8), rgba(0, 102, 204, 0.9));
        color: white;
        border-radius: 16px;
        padding: 0.75rem 2.5rem;
        font-weight: 600;
        font-size: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.3);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px 0 rgba(0, 76, 151, 0.37), 
                    inset 0 1px 0 rgba(255, 255, 255, 0.2);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        text-transform: none;
        letter-spacing: 0.5px;
    }}
    
    .stButton>button:hover {{
        background: linear-gradient(135deg, rgba(0, 102, 204, 0.9), rgba(0, 76, 151, 0.95));
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 12px 40px 0 rgba(0, 76, 151, 0.5),
                    inset 0 1px 0 rgba(255, 255, 255, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.4);
    }}
    
    .stButton>button:active {{
        transform: translateY(-1px) scale(0.98);
    }}
    
    /* 질문 카드 - Glassmorphism */
    .question-card {{
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        padding: 2rem;
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2),
                    inset 0 1px 0 rgba(255, 255, 255, 0.1);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }}
    
    .question-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, {WOORI_BLUE}, {WOORI_LIGHT_BLUE}, {WOORI_BLUE});
        background-size: 200% 100%;
        animation: shimmer 3s ease infinite;
    }}
    
    @keyframes shimmer {{
        0% {{ background-position: -200% 0; }}
        100% {{ background-position: 200% 0; }}
    }}
    
    .question-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 12px 48px 0 rgba(0, 0, 0, 0.3),
                    inset 0 1px 0 rgba(255, 255, 255, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }}
    
    .question-header {{
        color: rgba(255, 255, 255, 0.95);
        font-weight: 700;
        font-size: 1.2rem;
        margin-bottom: 1rem;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
        letter-spacing: -0.5px;
    }}
    
    .question-text {{
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.05rem;
        line-height: 1.8;
        margin-bottom: 1rem;
        white-space: pre-wrap;
        word-wrap: break-word;
        text-shadow: 0 1px 5px rgba(0, 0, 0, 0.1);
    }}
    
    .question-meta {{
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.9rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-top: 1rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }}
    
    /* 타이틀 스타일 */
    h1 {{
        color: rgba(255, 255, 255, 0.95);
        text-align: center;
        padding-bottom: 1.5rem;
        font-weight: 700;
        font-size: 2.5rem;
        text-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        letter-spacing: -1px;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.7));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    
    h2 {{
        color: rgba(255, 255, 255, 0.95);
        font-weight: 600;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    }}
    
    /* 입력 필드 - Glassmorphism */
    .stTextInput>div>div>input {{
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        color: rgba(255, 255, 255, 0.95);
        padding: 0.75rem 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }}
    
    .stTextInput>div>div>input:focus {{
        background: rgba(255, 255, 255, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.4);
        box-shadow: 0 4px 20px rgba(0, 76, 151, 0.3);
        outline: none;
    }}
    
    .stTextInput>div>div>input::placeholder {{
        color: rgba(255, 255, 255, 0.5);
    }}
    
    .stTextArea>div>div>textarea {{
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        color: rgba(255, 255, 255, 0.95);
        padding: 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }}
    
    .stTextArea>div>div>textarea:focus {{
        background: rgba(255, 255, 255, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.4);
        box-shadow: 0 4px 20px rgba(0, 76, 151, 0.3);
        outline: none;
    }}
    
    .stTextArea>div>div>textarea::placeholder {{
        color: rgba(255, 255, 255, 0.5);
    }}
    
    /* 사이드바 스타일 */
    .css-1d391kg {{
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }}
    
    /* 체크박스 스타일 */
    .stCheckbox label {{
        color: rgba(255, 255, 255, 0.9);
        font-weight: 500;
    }}
    
    /* 라디오 버튼 스타일 */
    .stRadio label {{
        color: rgba(255, 255, 255, 0.9);
    }}
    
    /* 셀렉트박스 스타일 */
    .stSelectbox label {{
        color: rgba(255, 255, 255, 0.9);
    }}
    
    .stSelectbox>div>div>select {{
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        color: rgba(255, 255, 255, 0.95);
    }}
    
    /* 메트릭 스타일 */
    [data-testid="stMetricValue"] {{
        color: rgba(255, 255, 255, 0.95);
        font-weight: 700;
    }}
    
    [data-testid="stMetricLabel"] {{
        color: rgba(255, 255, 255, 0.7);
    }}
    
    /* 캡션 스타일 */
    .stCaption {{
        color: rgba(255, 255, 255, 0.7);
    }}
    
    /* Info/Warning/Success 박스 스타일 */
    .stAlert {{
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px;
    }}
    
    /* Expander 스타일 */
    .streamlit-expanderHeader {{
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 12px;
        color: rgba(255, 255, 255, 0.9);
    }}
    
    /* 스크롤바 스타일 */
    ::-webkit-scrollbar {{
        width: 10px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: rgba(255, 255, 255, 0.2);
        border-radius: 10px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: rgba(255, 255, 255, 0.3);
    }}
</style>
""", unsafe_allow_html=True)

# 방문 추적
if STATS_ENABLED:
    try:
        track_visit()
    except:
        pass

# 메인 타이틀 - Liquid Glass 스타일
st.markdown(f"""
<div style="text-align: center; padding: 3rem 0 2rem 0;">
    <h1 style="margin-bottom: 0.5rem; font-size: 3rem; font-weight: 700; letter-spacing: -2px;">
        💬 현직자 런치톡 질문 수집
    </h1>
    <p style="color: rgba(255, 255, 255, 0.8); font-size: 1.2rem; font-weight: 300; letter-spacing: 0.5px; margin-top: 1rem;">
        함께 수강하는 분들의 질문을 모아서 현직자분께 전달하겠습니다
    </p>
</div>
""", unsafe_allow_html=True)

# 실시간 통계 표시
if STATS_ENABLED:
    try:
        from utils_stats import load_stats, get_current_visitors, get_daily_stats
        stats = load_stats()
        daily_stats = get_daily_stats(stats)
        current_visitors = daily_stats.get('current_visitors', 0)
        
        if current_visitors > 0:
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); 
                        padding: 1rem; border-radius: 16px; margin-bottom: 1.5rem; text-align: center; 
                        border: 1px solid rgba(255, 255, 255, 0.2); 
                        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);">
                <strong style="color: rgba(255, 255, 255, 0.95); font-size: 1.1rem; font-weight: 600; letter-spacing: 0.5px;">
                    👥 현재 접속 중: {current_visitors}명
                </strong>
            </div>
            """, unsafe_allow_html=True)
    except:
        pass

# 사이드바 - 질문 작성 및 필터
with st.sidebar:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(0, 76, 151, 0.3), rgba(0, 102, 204, 0.3)); 
                backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
                padding: 2rem; border-radius: 20px; margin-bottom: 2rem;
                border: 1px solid rgba(255, 255, 255, 0.2);
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);">
        <h2 style="color: rgba(255, 255, 255, 0.95); margin: 0; text-align: center; font-weight: 700; font-size: 1.5rem; letter-spacing: -0.5px;">
            📝 질문 작성
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # 익명 옵션 (기본값: 익명)
    use_name = st.checkbox("이름을 표시하시겠어요?", value=False, help="체크 해제 시 '익명'으로 표시됩니다")
    
    if use_name:
        name = st.text_input("이름", placeholder="예: 홍길동", help="이름을 입력하지 않으면 익명으로 표시됩니다", max_chars=20, key="input_name")
    else:
        name = ""
        st.markdown('<p style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem; margin-top: -0.5rem;">ℹ️ 익명으로 질문이 등록됩니다</p>', unsafe_allow_html=True)
    
    question = st.text_area(
        "질문 내용 *",
        placeholder="현직자분께 궁금한 점을 작성해주세요...",
        height=150,
        help="질문 내용은 필수 입력 항목입니다 (최대 1000자)",
        max_chars=1000,
        key="input_question"
    )
    
    # 글자 수 표시
    if question:
        char_count = len(question)
        if char_count > 900:
            st.markdown(f'<p style="color: rgba(255, 193, 7, 0.9); font-size: 0.85rem; margin-top: -0.5rem;">⚠️ {char_count}/1000자 (거의 다 채웠습니다)</p>', unsafe_allow_html=True)
        elif char_count > 0:
            st.markdown(f'<p style="color: rgba(255, 255, 255, 0.6); font-size: 0.85rem; margin-top: -0.5rem;">📝 {char_count}/1000자</p>', unsafe_allow_html=True)
    
    # 질문 등록 버튼
    if st.button("✅ 질문 등록하기", use_container_width=True, type="primary"):
        if question.strip():
            # 질문 길이 제한
            if len(question.strip()) > 1000:
                st.error("⚠️ 질문은 1000자 이하로 작성해주세요.")
            else:
                display_name = name.strip() if (use_name and name.strip()) else "익명"
                add_question(display_name, question.strip())
                st.success("✅ 질문이 등록되었습니다!")
                st.balloons()
                st.rerun()
        else:
            st.error("⚠️ 질문 내용을 입력해주세요.")
    
    st.markdown("---")
    
    # 관리자 페이지 링크 (작게 표시)
    with st.expander("🔐 관리자", expanded=False):
        if st.button("관리자 페이지 접속", use_container_width=True, type="secondary"):
            st.switch_page("pages/admin.py")
    
    st.markdown("---")
    
    # 필터 및 정렬 옵션
    st.markdown("### 🔍 필터 및 정렬")
    search_input_sidebar = st.text_input("🔎 질문 검색", placeholder="키워드로 검색...", help="질문 내용에서 검색합니다", key="search_sidebar", value=st.session_state.search_query)
    if search_input_sidebar != st.session_state.search_query:
        st.session_state.search_query = search_input_sidebar
    
    sort_index = ["👍 좋아요 순", "🕒 최신순", "📝 작성자순"].index(st.session_state.sort_option)
    sort_input_sidebar = st.radio(
        "정렬 기준",
        ["👍 좋아요 순", "🕒 최신순", "📝 작성자순"],
        help="질문 목록을 정렬하는 기준을 선택하세요",
        key="sort_sidebar",
        index=sort_index
    )
    if sort_input_sidebar != st.session_state.sort_option:
        st.session_state.sort_option = sort_input_sidebar

# 메인 영역 - 질문 목록
questions = load_questions()

# 검색 및 정렬을 메인 영역에도 추가
col_title, col_search, col_sort = st.columns([2, 2, 2])
with col_title:
    st.markdown('<h2 style="color: rgba(255, 255, 255, 0.95); font-weight: 700; margin-bottom: 0;">📋 등록된 질문 목록</h2>', unsafe_allow_html=True)
with col_search:
    # 메인 검색창 (사이드바와 동기화)
    search_input_main = st.text_input("🔎 검색", placeholder="키워드로 검색...", key="search_main", label_visibility="collapsed", value=st.session_state.search_query)
    if search_input_main != st.session_state.search_query:
        st.session_state.search_query = search_input_main
with col_sort:
    # 메인 정렬 (사이드바와 동기화)
    current_sort = st.session_state.sort_option
    sort_index = ["👍 좋아요 순", "🕒 최신순", "📝 작성자순"].index(current_sort)
    sort_select_main = st.selectbox(
        "정렬",
        ["👍 좋아요 순", "🕒 최신순", "📝 작성자순"],
        key="sort_main",
        label_visibility="collapsed",
        index=sort_index
    )
    if sort_select_main != current_sort:
        st.session_state.sort_option = sort_select_main

# 검색 필터 적용
if st.session_state.search_query:
    questions = [q for q in questions if st.session_state.search_query.lower() in q["question"].lower()]

# 정렬 옵션에 따라 정렬
if st.session_state.sort_option == "👍 좋아요 순":
    questions_sorted = sorted(questions, key=lambda x: x.get("likes", 0), reverse=True)
elif st.session_state.sort_option == "🕒 최신순":
    questions_sorted = sorted(questions, key=lambda x: x.get("timestamp", ""), reverse=True)
elif st.session_state.sort_option == "📝 작성자순":
    questions_sorted = sorted(questions, key=lambda x: x.get("name", "익명"))
else:
    questions_sorted = sorted(questions, key=lambda x: x.get("likes", 0), reverse=True)

if not questions:
    if st.session_state.search_query:
        st.markdown(f"""
        <div style="background: rgba(255, 193, 7, 0.15); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
                    padding: 1.5rem; border-radius: 16px; border: 1px solid rgba(255, 193, 7, 0.3);
                    margin-bottom: 1rem; text-align: center;">
            <p style="color: rgba(255, 255, 255, 0.95); font-size: 1.1rem; margin: 0;">
                🔍 '{st.session_state.search_query}'에 대한 검색 결과가 없습니다.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔍 검색 초기화", use_container_width=True):
            st.session_state.search_query = ""
            st.rerun()
    else:
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
                    padding: 2rem; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.2);
                    text-align: center;">
            <p style="color: rgba(255, 255, 255, 0.9); font-size: 1.2rem; margin: 0;">
                아직 등록된 질문이 없습니다. 첫 번째 질문을 작성해보세요! 💡
            </p>
        </div>
        """, unsafe_allow_html=True)
else:
    # 검색 결과 표시
    if st.session_state.search_query:
        st.markdown(f"""
        <div style="background: rgba(0, 102, 204, 0.2); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
                    padding: 1rem; border-radius: 12px; border: 1px solid rgba(0, 102, 204, 0.3);
                    margin-bottom: 1rem; text-align: center;">
            <p style="color: rgba(255, 255, 255, 0.95); font-size: 1rem; margin: 0;">
                🔍 '{st.session_state.search_query}' 검색 결과: {len(questions_sorted)}개
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # 질문 개수 표시
    total_questions = len(load_questions())
    if len(questions_sorted) != total_questions:
        st.markdown(f'<p style="color: rgba(255, 255, 255, 0.6); font-size: 0.85rem; margin-top: -0.5rem;">전체 {total_questions}개 중 {len(questions_sorted)}개 표시</p>', unsafe_allow_html=True)
    
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
                # 좋아요 버튼 (이미 좋아요를 누른 경우 비활성화)
                if q['id'] in st.session_state.liked_questions:
                    st.button("✅ 좋아요 완료", key=f"like_{q['id']}", use_container_width=True, disabled=True, help="이미 좋아요를 누른 질문입니다")
                else:
                    if st.button("👍 좋아요", key=f"like_{q['id']}", use_container_width=True):
                        like_question(q["id"])
            with col3:
                st.markdown(f'<p style="color: rgba(255, 255, 255, 0.5); font-size: 0.85rem; text-align: right;">#{q["id"]}</p>', unsafe_allow_html=True)
            
            st.markdown("---")

# 통계 정보 - Liquid Glass 스타일
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
    <div style="background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
                padding: 1.5rem; border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.2);
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2); text-align: center;">
        <p style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem; margin-bottom: 0.5rem;">총 질문 수</p>
        <p style="color: rgba(255, 255, 255, 0.95); font-size: 2rem; font-weight: 700; margin: 0;">{len(load_questions())}</p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    all_questions = load_questions()
    total_likes = sum(q.get("likes", 0) for q in all_questions)
    st.markdown(f"""
    <div style="background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
                padding: 1.5rem; border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.2);
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2); text-align: center;">
        <p style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem; margin-bottom: 0.5rem;">총 좋아요</p>
        <p style="color: rgba(255, 255, 255, 0.95); font-size: 2rem; font-weight: 700; margin: 0;">{total_likes}</p>
    </div>
    """, unsafe_allow_html=True)
with col3:
    if all_questions:
        avg_likes = total_likes / len(all_questions) if all_questions else 0
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
                    padding: 1.5rem; border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.2);
                    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2); text-align: center;">
            <p style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem; margin-bottom: 0.5rem;">평균 좋아요</p>
            <p style="color: rgba(255, 255, 255, 0.95); font-size: 2rem; font-weight: 700; margin: 0;">{avg_likes:.1f}</p>
        </div>
        """, unsafe_allow_html=True)

# 푸터 - Liquid Glass 스타일
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown(f"""
    <div style="background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
                text-align: center; color: rgba(255, 255, 255, 0.8); padding: 2rem; border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2); margin-top: 2rem;">
        <p style="font-size: 1rem; margin-bottom: 0.5rem;">💡 질문은 실시간으로 업데이트됩니다</p>
        <p style="font-size: 1rem; margin-bottom: 1rem;">🔄 페이지를 새로고침하면 최신 질문을 확인할 수 있습니다</p>
        <p style="color: rgba(255, 255, 255, 0.95); font-weight: 700; font-size: 1.2rem; margin-top: 1rem; letter-spacing: 0.5px;">
            우리은행 FISA 부트캠프 💙
        </p>
    </div>
    """, unsafe_allow_html=True)
