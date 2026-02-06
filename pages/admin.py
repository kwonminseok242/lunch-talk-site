"""
관리자 페이지
질문 관리, 통계, 데이터 내보내기 기능
"""

import streamlit as st
import json
import os
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

# 통계 모듈 임포트
try:
    from utils_stats import load_stats, get_daily_stats, get_all_time_stats, get_current_visitors
    STATS_ENABLED = True
except ImportError:
    STATS_ENABLED = False

# Google Sheets 연동
try:
    from st_gsheets_connection import GSheetsConnection
    USE_GSHEETS = True
except ImportError:
    try:
        from streamlit_gsheets import GSheetsConnection
        USE_GSHEETS = True
    except ImportError:
        USE_GSHEETS = False

# 컬러 상수
WOORI_BLUE = "#004C97"
WOORI_LIGHT_BLUE = "#0066CC"

# 데이터 파일 경로 (절대 경로로 통일)
DATA_FILE = Path(__file__).parent.parent / "questions.json"
DB_FILE = Path(__file__).parent.parent / "questions.db"
WORKSHEET_NAME = "questions"

def init_db():
    """SQLite 데이터베이스 초기화"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            question TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            likes INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def save_to_sqlite(questions):
    """SQLite에 데이터 저장"""
    try:
        init_db()
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM questions')
        for q in questions:
            cursor.execute('''
                INSERT INTO questions (id, name, question, timestamp, likes)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                q.get('id', 0),
                q.get('name', '익명'),
                q.get('question', ''),
                q.get('timestamp', ''),
                q.get('likes', 0)
            ))
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"SQLite 저장 오류: {e}")

# Google Sheets 연결
conn_gsheet = None
SPREADSHEET_URL = None
if USE_GSHEETS:
    try:
        # Secrets에서 spreadsheet 설정 확인
        try:
            gsheets_config = st.secrets.get("connections", {}).get("gsheets", {})
            
            # spreadsheet URL이 직접 있는 경우
            if "spreadsheet" in gsheets_config:
                SPREADSHEET_URL = gsheets_config["spreadsheet"]
            # spreadsheet_id가 있는 경우 URL로 변환
            elif "spreadsheet_id" in gsheets_config:
                spreadsheet_id = gsheets_config["spreadsheet_id"]
                SPREADSHEET_URL = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
            # spreadsheet_url이 있는 경우
            elif "spreadsheet_url" in gsheets_config:
                SPREADSHEET_URL = gsheets_config["spreadsheet_url"]
            
            if SPREADSHEET_URL:
                conn_gsheet = st.connection("gsheets", type=GSheetsConnection)
                USE_GSHEETS = True
            else:
                USE_GSHEETS = False
                conn_gsheet = None
        except Exception as e:
            USE_GSHEETS = False
            conn_gsheet = None
            SPREADSHEET_URL = None
    except Exception:
        USE_GSHEETS = False
        conn_gsheet = None
        SPREADSHEET_URL = None

def load_questions():
    """질문 데이터 로드 - Google Sheets 우선, 없으면 SQLite, 마지막으로 JSON"""
    # 1. Google Sheets 우선
    if USE_GSHEETS and conn_gsheet and SPREADSHEET_URL:
        try:
            df = conn_gsheet.read(spreadsheet=SPREADSHEET_URL, worksheet=WORKSHEET_NAME, ttl=0)
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
                if result:
                    save_to_sqlite(result)
                return result
        except:
            pass
    
    # 2. SQLite 사용 (영구 저장)
    try:
        init_db()
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM questions ORDER BY id')
        rows = cursor.fetchall()
        conn.close()
        
        if rows:
            questions = []
            for row in rows:
                questions.append({
                    'id': row[0],
                    'name': row[1],
                    'question': row[2],
                    'timestamp': row[3],
                    'likes': row[4] if len(row) > 4 else 0
                })
            return questions
    except:
        pass
    
    # 3. JSON 파일 사용 (마이그레이션용)
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                questions = json.load(f)
                if questions:
                    save_to_sqlite(questions)
                return questions
        except:
            pass
    
    return []

def save_questions(questions):
    """질문 데이터 저장 - Google Sheets 우선, SQLite 백업, JSON 마지막"""
    # 1. Google Sheets 저장 (우선)
    if USE_GSHEETS and conn_gsheet and questions:
        try:
            df = pd.DataFrame(questions)
            # 필요한 컬럼만 선택
            required_columns = ['id', 'name', 'question', 'timestamp', 'likes']
            
            # 컬럼이 없는 경우 추가
            for col in required_columns:
                if col not in df.columns:
                    df[col] = ''
            
            # 컬럼 순서 정렬
            df = df[required_columns]
            
            # 빈 값 처리
            df = df.fillna('')
            
            # Google Sheets에 저장
            if SPREADSHEET_URL:
                conn_gsheet.update(spreadsheet=SPREADSHEET_URL, worksheet=WORKSHEET_NAME, data=df)
            else:
                conn_gsheet.update(worksheet=WORKSHEET_NAME, data=df)
            st.cache_data.clear()
            save_to_sqlite(questions)
            return
        except Exception as e:
            # 에러 메시지 표시
            import traceback
            error_msg = f"Google Sheets 저장 오류: {str(e)}"
            st.error(error_msg)
            st.error(f"상세: {traceback.format_exc()}")
            # 실패 시 SQLite로 대체 저장
            pass
    
    # 2. SQLite 저장 (영구 저장)
    try:
        save_to_sqlite(questions)
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(questions, f, ensure_ascii=False, indent=2)
        except:
            pass
        return
    except Exception as e:
        st.error(f"데이터 저장 오류: {e}")
    
    # 3. JSON 파일 저장 (최후의 수단)
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"파일 저장 오류: {e}")

# 페이지 설정
st.set_page_config(
    page_title="관리자 페이지",
    page_icon="🔐",
    layout="wide"
)

# 커스텀 CSS - 어두운 계열 모던 Glass 디자인
st.markdown(f"""
<style>
    /* 전체 배경 - 어두운 그라데이션 */
    .main {{
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0f1419 100%);
        min-height: 100vh;
    }}
    
    /* 스트림릿 컨테이너 - 투명하게 */
    .block-container {{
        background: transparent;
        padding: 2rem;
        margin-top: 1rem;
    }}
    
    /* 버튼 - 모던 글래스 효과 */
    .stButton>button {{
        background: rgba(0, 76, 151, 0.9);
        color: white;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        box-shadow: 0 8px 32px rgba(0, 76, 151, 0.4),
                    inset 0 1px 0 rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
        text-transform: none;
    }}
    
    .stButton>button:hover {{
        background: {WOORI_LIGHT_BLUE};
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(0, 102, 204, 0.5),
                    inset 0 1px 0 rgba(255, 255, 255, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }}
    
    /* 입력 필드 - 글래스 효과 */
    .stTextInput>div>div>input {{
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 10px;
        color: #ffffff;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }}
    
    .stTextInput>div>div>input:focus {{
        background: rgba(255, 255, 255, 0.15);
        border: 1px solid {WOORI_LIGHT_BLUE};
        box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.2);
        outline: none;
    }}
    
    .stTextInput>div>div>input::placeholder {{
        color: rgba(255, 255, 255, 0.4);
    }}
    
    /* 타이틀 스타일 */
    h1 {{
        color: #ffffff;
        font-weight: 700;
        letter-spacing: -1px;
    }}
    
    h2, h3 {{
        color: #ffffff;
        font-weight: 600;
    }}
    
    /* 메트릭 스타일 */
    [data-testid="stMetricValue"] {{
        color: #ffffff;
        font-weight: 700;
    }}
    
    [data-testid="stMetricLabel"] {{
        color: rgba(255, 255, 255, 0.7);
    }}
    
    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] {{
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 12px;
        padding: 0.5rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }}
    
    .stTabs [data-baseweb="tab"] {{
        color: rgba(255, 255, 255, 0.7);
        border-radius: 8px;
        transition: all 0.3s ease;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: rgba(255, 255, 255, 0.15);
        color: #ffffff;
    }}
    
    /* Expander 스타일 */
    .streamlit-expanderHeader {{
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 12px;
        color: rgba(255, 255, 255, 0.9);
        border: 1px solid rgba(255, 255, 255, 0.15);
    }}
    
    /* Dataframe 스타일 */
    .dataframe {{
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 12px;
    }}
    
    /* Alert 박스 스타일 */
    .stAlert {{
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 12px;
    }}
    
    /* 셀렉트박스 스타일 */
    .stSelectbox>div>div>select {{
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 10px;
        color: #ffffff;
    }}
    
    .stSelectbox label {{
        color: rgba(255, 255, 255, 0.9);
    }}
</style>
""", unsafe_allow_html=True)

# 관리자 비밀번호 (실제 사용 시 환경변수나 secrets로 관리)
try:
    ADMIN_PASSWORD = st.secrets.get("admin_password", "woori2024")
except:
    ADMIN_PASSWORD = "woori2024"  # 기본 비밀번호

def check_admin():
    """관리자 인증 확인"""
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False
    
    if not st.session_state.admin_authenticated:
        st.markdown("""
        <div style="text-align: center; padding: 3rem 0 2rem 0;">
            <h1 style="margin-bottom: 0.5rem; font-size: 3rem; font-weight: 700; letter-spacing: -2px; color: #ffffff;">
                🔐 관리자 로그인
            </h1>
        </div>
        """, unsafe_allow_html=True)
        
        password = st.text_input("비밀번호를 입력하세요", type="password")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("로그인", type="primary", use_container_width=True):
                if password == ADMIN_PASSWORD:
                    st.session_state.admin_authenticated = True
                    st.rerun()
                else:
                    st.error("❌ 비밀번호가 올바르지 않습니다")
        
        st.markdown("---")
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.08); backdrop-filter: blur(40px); -webkit-backdrop-filter: blur(40px);
                    padding: 1.5rem; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.15);
                    text-align: center; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);">
            <p style="color: rgba(255, 255, 255, 0.9); font-size: 1.1rem; margin: 0;">
                💡 관리자만 접근할 수 있는 페이지입니다
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()
    
    return True

def delete_question(question_id):
    """질문 삭제"""
    questions = load_questions()
    questions = [q for q in questions if q['id'] != question_id]
    # ID 재정렬
    for idx, q in enumerate(questions, 1):
        q['id'] = idx
    save_questions(questions)
    st.success(f"✅ 질문 #{question_id}이(가) 삭제되었습니다")
    st.rerun()

def export_to_csv():
    """CSV로 내보내기"""
    questions = load_questions()
    if not questions:
        return None
    
    df = pd.DataFrame(questions)
    return df.to_csv(index=False, encoding='utf-8-sig')

def export_to_excel():
    """Excel로 내보내기"""
    questions = load_questions()
    if not questions:
        st.warning("내보낼 질문이 없습니다")
        return None
    
    df = pd.DataFrame(questions)
    from io import BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='질문목록')
    return output.getvalue()

# 관리자 인증 확인
if check_admin():
    # 헤더 - 글래스 스타일
    st.markdown(f"""
    <div style="background: rgba(255, 255, 255, 0.08); backdrop-filter: blur(40px); -webkit-backdrop-filter: blur(40px);
                padding: 2rem; border-radius: 16px; margin-bottom: 2rem;
                border: 1px solid rgba(255, 255, 255, 0.15);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1);">
        <h1 style="color: #ffffff; margin: 0; text-align: center; font-weight: 700; font-size: 2.5rem;">
            🔐 관리자 페이지
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    # 로그아웃 버튼
    col1, col2 = st.columns([10, 1])
    with col2:
        if st.button("🚪 로그아웃"):
            st.session_state.admin_authenticated = False
            st.rerun()
    
    st.markdown("---")
    
    # 탭 구성
    tab1, tab2, tab3, tab4 = st.tabs(["📋 질문 관리", "📊 통계", "📥 데이터 내보내기", "⚙️ 설정"])
    
    questions = load_questions()
    
    # 탭 1: 질문 관리
    with tab1:
        st.header("📋 질문 관리")
        
        if not questions:
            st.markdown("""
            <div style="background: rgba(255, 255, 255, 0.08); backdrop-filter: blur(40px); -webkit-backdrop-filter: blur(40px);
                        padding: 2rem; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.15);
                        text-align: center; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);">
                <p style="color: rgba(255, 255, 255, 0.9); font-size: 1.2rem; margin: 0;">
                    등록된 질문이 없습니다
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # 검색 및 필터
            col1, col2 = st.columns([3, 1])
            with col1:
                search_admin = st.text_input("🔍 질문 검색", placeholder="키워드로 검색...")
            with col2:
                filter_likes = st.selectbox("좋아요 필터", ["전체", "5개 이상", "10개 이상"])
            
            # 질문 필터링
            filtered_questions = questions
            if search_admin:
                filtered_questions = [q for q in filtered_questions if search_admin.lower() in q["question"].lower()]
            if filter_likes == "5개 이상":
                filtered_questions = [q for q in filtered_questions if q.get("likes", 0) >= 5]
            elif filter_likes == "10개 이상":
                filtered_questions = [q for q in filtered_questions if q.get("likes", 0) >= 10]
            
            col_metric1, col_metric2, col_metric3 = st.columns(3)
            with col_metric1:
                st.metric("총 질문 수", len(questions))
            with col_metric2:
                st.metric("필터링된 질문 수", len(filtered_questions))
            with col_metric3:
                total_likes_admin = sum(q.get("likes", 0) for q in questions)
                st.metric("총 좋아요", total_likes_admin)
            
            st.markdown("---")
            
            # 일괄 삭제 옵션
            with st.expander("🗑️ 일괄 삭제 옵션", expanded=False):
                col_batch1, col_batch2 = st.columns(2)
                
                with col_batch1:
                    st.markdown("**좋아요 기준 일괄 삭제**")
                    batch_delete_likes = st.number_input(
                        "좋아요가 이 값 이하인 질문 삭제",
                        min_value=0,
                        value=0,
                        key="batch_delete_likes",
                        help="예: 0을 입력하면 좋아요가 0개인 질문만 삭제"
                    )
                    if st.button("일괄 삭제 실행", key="batch_delete_by_likes", type="secondary"):
                        if st.session_state.get("confirm_batch_delete_likes", False):
                            deleted_count = 0
                            remaining_questions = []
                            for q in questions:
                                if q.get("likes", 0) <= batch_delete_likes:
                                    deleted_count += 1
                                else:
                                    remaining_questions.append(q)
                            
                            # ID 재정렬
                            for idx, q in enumerate(remaining_questions, 1):
                                q['id'] = idx
                            
                            save_questions(remaining_questions)
                            st.success(f"✅ 좋아요 {batch_delete_likes}개 이하인 질문 {deleted_count}개가 삭제되었습니다")
                            st.session_state.confirm_batch_delete_likes = False
                            st.rerun()
                        else:
                            count = sum(1 for q in questions if q.get("likes", 0) <= batch_delete_likes)
                            if count > 0:
                                st.session_state.confirm_batch_delete_likes = True
                                st.warning(f"⚠️ 좋아요 {batch_delete_likes}개 이하인 질문 {count}개가 삭제됩니다. 다시 클릭하면 삭제됩니다.")
                            else:
                                st.info("해당 조건에 맞는 질문이 없습니다.")
                    
                    if st.session_state.get("confirm_batch_delete_likes", False):
                        if st.button("취소", key="cancel_batch_delete_likes"):
                            st.session_state.confirm_batch_delete_likes = False
                            st.rerun()
                
                with col_batch2:
                    st.markdown("**날짜 기준 일괄 삭제**")
                    batch_delete_days = st.number_input(
                        "몇 일 이전 질문 삭제",
                        min_value=1,
                        value=7,
                        key="batch_delete_days",
                        help="예: 7을 입력하면 7일 이전 질문이 삭제"
                    )
                    if st.button("일괄 삭제 실행", key="batch_delete_by_date", type="secondary"):
                        if st.session_state.get("confirm_batch_delete_date", False):
                            cutoff_date = datetime.now() - timedelta(days=batch_delete_days)
                            deleted_count = 0
                            remaining_questions = []
                            for q in questions:
                                try:
                                    q_date = datetime.strptime(q.get("timestamp", ""), "%Y-%m-%d %H:%M:%S")
                                    if q_date < cutoff_date:
                                        deleted_count += 1
                                    else:
                                        remaining_questions.append(q)
                                except:
                                    remaining_questions.append(q)
                            
                            # ID 재정렬
                            for idx, q in enumerate(remaining_questions, 1):
                                q['id'] = idx
                            
                            save_questions(remaining_questions)
                            st.success(f"✅ {batch_delete_days}일 이전 질문 {deleted_count}개가 삭제되었습니다")
                            st.session_state.confirm_batch_delete_date = False
                            st.rerun()
                        else:
                            cutoff_date = datetime.now() - timedelta(days=batch_delete_days)
                            count = 0
                            for q in questions:
                                try:
                                    q_date = datetime.strptime(q.get("timestamp", ""), "%Y-%m-%d %H:%M:%S")
                                    if q_date < cutoff_date:
                                        count += 1
                                except:
                                    pass
                            if count > 0:
                                st.session_state.confirm_batch_delete_date = True
                                st.warning(f"⚠️ {batch_delete_days}일 이전 질문 {count}개가 삭제됩니다. 다시 클릭하면 삭제됩니다.")
                            else:
                                st.info("해당 조건에 맞는 질문이 없습니다.")
                    
                    if st.session_state.get("confirm_batch_delete_date", False):
                        if st.button("취소", key="cancel_batch_delete_date"):
                            st.session_state.confirm_batch_delete_date = False
                            st.rerun()
            
            st.markdown("---")
            
            # 질문 목록 표시
            for q in filtered_questions:
                with st.expander(f"질문 #{q['id']} - {q.get('name', '익명')}님 ({q.get('likes', 0)}👍)", expanded=False):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"**작성자:** {q.get('name', '익명')}")
                        st.markdown(f"**작성 시간:** {q['timestamp']}")
                        st.markdown(f"**좋아요:** {q.get('likes', 0)}개")
                        st.markdown("---")
                        st.markdown(f"**질문 내용:**")
                        st.write(q['question'])
                    
                    with col2:
                        # 삭제 확인
                        delete_key = f"delete_{q['id']}"
                        confirm_key = f"confirm_delete_{q['id']}"
                        
                        if st.session_state.get(confirm_key, False):
                            col_yes, col_no = st.columns(2)
                            with col_yes:
                                if st.button("✅ 확인", key=f"yes_{q['id']}", use_container_width=True):
                                    delete_question(q['id'])
                                    st.session_state[confirm_key] = False
                            with col_no:
                                if st.button("❌ 취소", key=f"no_{q['id']}", use_container_width=True):
                                    st.session_state[confirm_key] = False
                                    st.rerun()
                        else:
                            if st.button("🗑️ 삭제", key=delete_key, type="secondary", use_container_width=True):
                                st.session_state[confirm_key] = True
                                st.rerun()
                
                st.markdown("---")
    
    # 탭 2: 통계
    with tab2:
        st.header("📊 통계 정보")
        
        # 방문자 통계
        if STATS_ENABLED:
            try:
                stats = load_stats()
                
                if stats:
                    st.subheader("👥 방문자 통계")
                    daily_stats = get_daily_stats(stats)
                    all_time_stats = get_all_time_stats(stats)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("현재 접속 중", f"{daily_stats.get('current_visitors', 0)}명")
                    
                    with col2:
                        st.metric("오늘 방문자", f"{daily_stats.get('unique_visitors', 0)}명")
                    
                    with col3:
                        st.metric("오늘 총 방문", f"{daily_stats.get('total_visits', 0)}회")
                    
                    with col4:
                        st.metric("전체 방문자", f"{all_time_stats.get('total_unique_visitors', 0)}명")
                    
                    st.markdown("---")
                    
                    # 시간대별 접속 통계
                    st.subheader("🕒 시간대별 접속 현황")
                    time_stats = {}
                    for stat in stats:
                        try:
                            last_visit_str = stat.get('last_visit', '')
                            if last_visit_str:
                                last_visit = datetime.strptime(last_visit_str, "%Y-%m-%d %H:%M:%S")
                                hour = last_visit.hour
                                time_range = f"{hour:02d}:00"
                                time_stats[time_range] = time_stats.get(time_range, 0) + 1
                        except:
                            pass
                    
                    if time_stats:
                        time_df = pd.DataFrame([
                            {"시간대": k, "접속 수": v}
                            for k, v in sorted(time_stats.items())
                        ])
                        st.bar_chart(time_df.set_index("시간대"))
                    
                    st.markdown("---")
            except Exception as e:
                st.warning(f"방문자 통계 로드 오류: {e}")
        else:
            st.markdown("""
            <div style="background: rgba(255, 255, 255, 0.08); backdrop-filter: blur(40px); -webkit-backdrop-filter: blur(40px);
                        padding: 1.5rem; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.15);
                        text-align: center; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);">
                <p style="color: rgba(255, 255, 255, 0.9); font-size: 1.1rem; margin: 0;">
                    ℹ️ 방문자 통계 기능을 사용할 수 없습니다
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # 질문 통계
        st.subheader("📝 질문 통계")
        if not questions:
            st.markdown("""
            <div style="background: rgba(255, 255, 255, 0.08); backdrop-filter: blur(40px); -webkit-backdrop-filter: blur(40px);
                        padding: 2rem; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.15);
                        text-align: center; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);">
                <p style="color: rgba(255, 255, 255, 0.9); font-size: 1.2rem; margin: 0;">
                    질문 데이터가 없습니다
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("총 질문 수", len(questions))
            
            with col2:
                total_likes = sum(q.get("likes", 0) for q in questions)
                st.metric("총 좋아요 수", total_likes)
            
            with col3:
                avg_likes = total_likes / len(questions) if questions else 0
                st.metric("평균 좋아요", f"{avg_likes:.1f}")
            
            with col4:
                anonymous_count = sum(1 for q in questions if q.get("name") == "익명")
                st.metric("익명 질문", anonymous_count)
            
            st.markdown("---")
            
            # 작성자별 통계
            st.subheader("📊 작성자별 통계")
            author_stats = {}
            for q in questions:
                author = q.get("name", "익명")
                if author not in author_stats:
                    author_stats[author] = {"count": 0, "likes": 0}
                author_stats[author]["count"] += 1
                author_stats[author]["likes"] += q.get("likes", 0)
            
            author_df = pd.DataFrame([
                {
                    "작성자": author,
                    "질문 수": stats["count"],
                    "총 좋아요": stats["likes"],
                    "평균 좋아요": round(stats["likes"] / stats["count"], 1)
                }
                for author, stats in author_stats.items()
            ]).sort_values("질문 수", ascending=False)
            
            st.dataframe(author_df, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            
            # 시간대별 통계
            st.subheader("🕒 시간대별 질문 수")
            time_stats = {}
            for q in questions:
                timestamp = q.get("timestamp", "")
                if timestamp:
                    try:
                        hour = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").hour
                        time_range = f"{hour:02d}:00-{hour+1:02d}:00"
                        time_stats[time_range] = time_stats.get(time_range, 0) + 1
                    except:
                        pass
            
            if time_stats:
                time_df = pd.DataFrame([
                    {"시간대": k, "질문 수": v}
                    for k, v in sorted(time_stats.items())
                ])
                st.bar_chart(time_df.set_index("시간대"))
    
    # 탭 3: 데이터 내보내기
    with tab3:
        st.header("📥 데이터 내보내기")
        
        if not questions:
            st.markdown("""
            <div style="background: rgba(255, 193, 7, 0.1); backdrop-filter: blur(40px); -webkit-backdrop-filter: blur(40px);
                        padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(255, 193, 7, 0.2);
                        text-align: center;">
                <p style="color: #ffffff; font-size: 1.1rem; margin: 0;">
                    내보낼 데이터가 없습니다
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background: rgba(0, 102, 204, 0.15); backdrop-filter: blur(40px); -webkit-backdrop-filter: blur(40px);
                        padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(0, 102, 204, 0.2);
                        text-align: center; margin-bottom: 1.5rem;">
                <p style="color: #ffffff; font-size: 1.1rem; margin: 0;">
                    총 {len(questions)}개의 질문을 내보낼 수 있습니다
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📄 CSV 파일로 내보내기")
                csv_data = export_to_csv()
                if csv_data:
                    st.download_button(
                        label="📥 CSV 다운로드",
                        data=csv_data,
                        file_name=f"questions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            
            with col2:
                st.subheader("📊 Excel 파일로 내보내기")
                try:
                    excel_data = export_to_excel()
                    if excel_data:
                        st.download_button(
                            label="📥 Excel 다운로드",
                            data=excel_data,
                            file_name=f"questions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                except ImportError:
                    st.error("Excel 내보내기를 사용하려면 openpyxl 패키지가 필요합니다")
                    st.code("pip install openpyxl")
            
            st.markdown("---")
            
            # 미리보기
            st.subheader("📋 데이터 미리보기")
            df = pd.DataFrame(questions)
            st.dataframe(df, use_container_width=True, hide_index=True)
    
    # 탭 4: 설정
    with tab4:
        st.header("⚙️ 관리자 설정")
        
        st.subheader("📊 데이터 저장 상태")
        
        # 저장 상태 확인
        storage_status = None
        if USE_GSHEETS and conn_gsheet:
            storage_status = "google_sheets"
        elif DB_FILE.exists():
            storage_status = "sqlite"
        else:
            storage_status = "json"
        
        # 저장 상태 표시
        if storage_status == "google_sheets":
            st.markdown("""
            <div style="background: rgba(40, 167, 69, 0.15); backdrop-filter: blur(40px); -webkit-backdrop-filter: blur(40px);
                        padding: 1rem; border-radius: 12px; border: 1px solid rgba(40, 167, 69, 0.2);
                        margin-bottom: 1rem;">
                <p style="color: #ffffff; font-size: 1rem; margin: 0; font-weight: 600;">
                    ✅ Google Sheets에 저장 중 (영구 저장)
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.info(f"📋 워크시트: `{WORKSHEET_NAME}`")
            st.caption("💡 Google Sheets는 재시작 후에도 데이터가 유지됩니다.")
        elif storage_status == "sqlite":
            st.markdown("""
            <div style="background: rgba(40, 167, 69, 0.15); backdrop-filter: blur(40px); -webkit-backdrop-filter: blur(40px);
                        padding: 1rem; border-radius: 12px; border: 1px solid rgba(40, 167, 69, 0.2);
                        margin-bottom: 1rem;">
                <p style="color: #ffffff; font-size: 1rem; margin: 0; font-weight: 600;">
                    ✅ SQLite 데이터베이스에 저장 중 (영구 저장)
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.info(f"💾 데이터베이스: `{DB_FILE.name}`")
            st.info(f"📁 파일 경로: `{DB_FILE}`")
            st.caption("💡 SQLite는 재시작 후에도 데이터가 유지됩니다.")
            st.warning("⚠️ **권장**: Streamlit Cloud에서는 Google Sheets 연동을 권장합니다.")
        else:
            st.markdown("""
            <div style="background: rgba(255, 193, 7, 0.15); backdrop-filter: blur(40px); -webkit-backdrop-filter: blur(40px);
                        padding: 1rem; border-radius: 12px; border: 1px solid rgba(255, 193, 7, 0.2);
                        margin-bottom: 1rem;">
                <p style="color: #ffffff; font-size: 1rem; margin: 0; font-weight: 600;">
                    ⚠️ JSON 파일에 저장 중 (임시 저장)
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.info(f"📁 파일 경로: `{DATA_FILE}`")
            st.error("🚨 **주의**: Streamlit Cloud에서 재시작 시 데이터가 사라질 수 있습니다!")
            st.info("💡 **해결 방법**: Google Sheets를 연동하거나 SQLite를 사용하세요.")
        
        # 현재 저장된 질문 수 표시
        questions_count = len(load_questions())
        st.markdown("---")
        st.metric("현재 저장된 질문 수", f"{questions_count}개")
        
        # Google Sheets 연결 테스트 및 디버깅
        st.markdown("---")
        st.subheader("🔧 Google Sheets 연결 테스트")
        
        # Secrets 확인
        try:
            gsheets_config = st.secrets.get("connections", {}).get("gsheets", {})
            st.info(f"📋 Secrets 확인:")
            st.json(gsheets_config)
            
            # 여러 형식 지원
            spreadsheet_id = gsheets_config.get("spreadsheet_id", "")
            spreadsheet_url = gsheets_config.get("spreadsheet", gsheets_config.get("spreadsheet_url", ""))
            worksheet_name = gsheets_config.get("worksheet", WORKSHEET_NAME)
            
            if SPREADSHEET_URL:
                st.success(f"✅ 스프레드시트 URL: `{SPREADSHEET_URL}`")
            elif spreadsheet_id:
                st.success(f"✅ 스프레드시트 ID: `{spreadsheet_id}`")
            else:
                st.error("❌ `spreadsheet` 또는 `spreadsheet_id`가 Secrets에 없습니다!")
                st.info("💡 Secrets에 다음 중 하나를 추가하세요:")
                st.code("""
[connections.gsheets]
spreadsheet = "https://docs.google.com/spreadsheets/d/1lEauHDkNImWHV-TpGbqGoBxYpC8dE0MY3SMMBBo1z0k/edit"
# 또는
spreadsheet_id = "1lEauHDkNImWHV-TpGbqGoBxYpC8dE0MY3SMMBBo1z0k"
worksheet = "questions"
                """)
            
            if worksheet_name:
                st.info(f"📄 워크시트 이름: `{worksheet_name}`")
        except Exception as e:
            st.error(f"Secrets 확인 오류: {e}")
        
        if USE_GSHEETS and conn_gsheet:
            if st.button("연결 테스트", key="test_gsheets"):
                try:
                    # 읽기 테스트
                    if SPREADSHEET_URL:
                        df_read = conn_gsheet.read(spreadsheet=SPREADSHEET_URL, worksheet=WORKSHEET_NAME, ttl=0)
                    else:
                        df_read = conn_gsheet.read(worksheet=WORKSHEET_NAME, ttl=0)
                    st.success(f"✅ 읽기 성공: {len(df_read) if df_read is not None and not df_read.empty else 0}개 행")
                    
                    # 쓰기 테스트 (테스트 데이터)
                    test_data = pd.DataFrame([{
                        'id': 999,
                        'name': '테스트',
                        'question': '연결 테스트',
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'likes': 0
                    }])
                    
                    # 기존 데이터와 합치기
                    if df_read is not None and not df_read.empty:
                        # 테스트 데이터 제거 (이미 있으면)
                        df_read = df_read[df_read['id'] != 999]
                        combined_df = pd.concat([df_read, test_data], ignore_index=True)
                    else:
                        combined_df = test_data
                    
                    if SPREADSHEET_URL:
                        conn_gsheet.update(spreadsheet=SPREADSHEET_URL, worksheet=WORKSHEET_NAME, data=combined_df)
                    else:
                        conn_gsheet.update(worksheet=WORKSHEET_NAME, data=combined_df)
                    st.success("✅ 쓰기 성공: 테스트 데이터가 저장되었습니다")
                    st.info("💡 Google Sheets를 새로고침하여 확인하세요. 테스트 데이터는 나중에 삭제하세요.")
                except Exception as e:
                    import traceback
                    st.error(f"❌ 연결 실패: {str(e)}")
                    with st.expander("상세 에러 정보"):
                        st.code(traceback.format_exc())
        else:
            st.warning("⚠️ Google Sheets 연결이 설정되지 않았습니다")
        
        st.markdown("---")
        
        st.subheader("🗑️ 질문 관리 기능")
        
        # 질문 일괄 삭제 옵션
        col_del1, col_del2 = st.columns(2)
        
        with col_del1:
            st.markdown("**좋아요가 적은 질문 삭제**")
            delete_likes_threshold = st.number_input(
                "좋아요가 이 값 이하인 질문 삭제",
                min_value=0,
                value=0,
                key="delete_likes_threshold",
                help="예: 0을 입력하면 좋아요가 0개인 질문만 삭제됩니다"
            )
            if st.button("좋아요 기준으로 삭제", key="delete_by_likes", type="secondary"):
                if st.session_state.get("confirm_delete_by_likes", False):
                    questions = load_questions()
                    deleted_count = 0
                    remaining_questions = []
                    for q in questions:
                        if q.get("likes", 0) <= delete_likes_threshold:
                            deleted_count += 1
                        else:
                            remaining_questions.append(q)
                    
                    # ID 재정렬
                    for idx, q in enumerate(remaining_questions, 1):
                        q['id'] = idx
                    
                    save_questions(remaining_questions)
                    st.success(f"✅ 좋아요 {delete_likes_threshold}개 이하인 질문 {deleted_count}개가 삭제되었습니다")
                    st.session_state.confirm_delete_by_likes = False
                    st.rerun()
                else:
                    questions = load_questions()
                    count = sum(1 for q in questions if q.get("likes", 0) <= delete_likes_threshold)
                    if count > 0:
                        st.session_state.confirm_delete_by_likes = True
                        st.warning(f"⚠️ 좋아요 {delete_likes_threshold}개 이하인 질문 {count}개가 삭제됩니다. 다시 클릭하면 삭제됩니다.")
                    else:
                        st.info("해당 조건에 맞는 질문이 없습니다.")
            
            if st.session_state.get("confirm_delete_by_likes", False):
                if st.button("취소", key="cancel_delete_by_likes"):
                    st.session_state.confirm_delete_by_likes = False
                    st.rerun()
        
        with col_del2:
            st.markdown("**오래된 질문 삭제**")
            delete_days = st.number_input(
                "몇 일 이전 질문 삭제",
                min_value=1,
                value=7,
                key="delete_days",
                help="예: 7을 입력하면 7일 이전 질문이 삭제됩니다"
            )
            if st.button("날짜 기준으로 삭제", key="delete_by_date", type="secondary"):
                if st.session_state.get("confirm_delete_by_date", False):
                    questions = load_questions()
                    from datetime import timedelta
                    cutoff_date = datetime.now() - timedelta(days=delete_days)
                    deleted_count = 0
                    remaining_questions = []
                    for q in questions:
                        try:
                            q_date = datetime.strptime(q.get("timestamp", ""), "%Y-%m-%d %H:%M:%S")
                            if q_date < cutoff_date:
                                deleted_count += 1
                            else:
                                remaining_questions.append(q)
                        except:
                            remaining_questions.append(q)
                    
                    # ID 재정렬
                    for idx, q in enumerate(remaining_questions, 1):
                        q['id'] = idx
                    
                    save_questions(remaining_questions)
                    st.success(f"✅ {delete_days}일 이전 질문 {deleted_count}개가 삭제되었습니다")
                    st.session_state.confirm_delete_by_date = False
                    st.rerun()
                else:
                    questions = load_questions()
                    from datetime import timedelta
                    cutoff_date = datetime.now() - timedelta(days=delete_days)
                    count = 0
                    for q in questions:
                        try:
                            q_date = datetime.strptime(q.get("timestamp", ""), "%Y-%m-%d %H:%M:%S")
                            if q_date < cutoff_date:
                                count += 1
                        except:
                            pass
                    if count > 0:
                        st.session_state.confirm_delete_by_date = True
                        st.warning(f"⚠️ {delete_days}일 이전 질문 {count}개가 삭제됩니다. 다시 클릭하면 삭제됩니다.")
                    else:
                        st.info("해당 조건에 맞는 질문이 없습니다.")
            
            if st.session_state.get("confirm_delete_by_date", False):
                if st.button("취소", key="cancel_delete_by_date"):
                    st.session_state.confirm_delete_by_date = False
                    st.rerun()
        
        st.markdown("---")
        
        st.subheader("📊 통계 초기화")
        
        col_stats1, col_stats2 = st.columns(2)
        
        with col_stats1:
            st.markdown("**조회수 초기화**")
            st.caption("방문자 통계 데이터를 모두 삭제합니다")
            if st.button("조회수 초기화", key="reset_stats", type="secondary"):
                if st.session_state.get("confirm_reset_stats", False):
                    try:
                        from utils_stats import load_stats, save_stats
                        stats = []
                        save_stats(stats)
                        st.success("✅ 조회수 통계가 초기화되었습니다")
                        st.session_state.confirm_reset_stats = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"오류: {e}")
                else:
                    st.session_state.confirm_reset_stats = True
                    st.warning("⚠️ 조회수 통계가 모두 삭제됩니다. 다시 클릭하면 초기화됩니다.")
            
            if st.session_state.get("confirm_reset_stats", False):
                if st.button("취소", key="cancel_reset_stats"):
                    st.session_state.confirm_reset_stats = False
                    st.rerun()
        
        with col_stats2:
            st.markdown("**좋아요 초기화**")
            st.caption("모든 질문의 좋아요 수를 0으로 초기화합니다")
            if st.button("좋아요 초기화", key="reset_likes", type="secondary"):
                if st.session_state.get("confirm_reset_likes", False):
                    questions = load_questions()
                    for q in questions:
                        q['likes'] = 0
                    save_questions(questions)
                    st.success("✅ 모든 질문의 좋아요가 초기화되었습니다")
                    st.session_state.confirm_reset_likes = False
                    st.rerun()
                else:
                    questions = load_questions()
                    total_likes = sum(q.get("likes", 0) for q in questions)
                    if total_likes > 0:
                        st.session_state.confirm_reset_likes = True
                        st.warning(f"⚠️ 총 {total_likes}개의 좋아요가 모두 0으로 초기화됩니다. 다시 클릭하면 초기화됩니다.")
                    else:
                        st.info("초기화할 좋아요가 없습니다.")
            
            if st.session_state.get("confirm_reset_likes", False):
                if st.button("취소", key="cancel_reset_likes"):
                    st.session_state.confirm_reset_likes = False
                    st.rerun()
        
        st.markdown("---")
        
        st.subheader("🔐 비밀번호 변경")
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.08); backdrop-filter: blur(40px); -webkit-backdrop-filter: blur(40px);
                    padding: 1rem; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.15);
                    margin-bottom: 1rem;">
            <p style="color: rgba(255, 255, 255, 0.9); font-size: 1rem; margin: 0;">
                현재 비밀번호: <code style="background: rgba(0, 0, 0, 0.3); padding: 0.2rem 0.5rem; border-radius: 4px; color: #ffffff;">woori2024</code>
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style="background: rgba(255, 193, 7, 0.1); backdrop-filter: blur(40px); -webkit-backdrop-filter: blur(40px);
                    padding: 1rem; border-radius: 12px; border: 1px solid rgba(255, 193, 7, 0.2);">
            <p style="color: #ffffff; font-size: 1rem; margin: 0;">
                ⚠️ 비밀번호를 변경하려면 코드를 수정하거나 Streamlit Cloud Secrets를 사용하세요
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.subheader("🗑️ 전체 데이터 삭제")
        st.markdown("""
        <div style="background: rgba(220, 53, 69, 0.15); backdrop-filter: blur(40px); -webkit-backdrop-filter: blur(40px);
                    padding: 1rem; border-radius: 12px; border: 1px solid rgba(220, 53, 69, 0.2);
                    margin-bottom: 1rem;">
            <p style="color: #ffffff; font-size: 1rem; margin: 0; font-weight: 600;">
                ⚠️ 주의: 이 작업은 되돌릴 수 없습니다!
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("전체 질문 삭제", type="secondary"):
            if st.session_state.get("confirm_delete", False):
                save_questions([])
                st.session_state.confirm_delete = False
                st.markdown("""
                <div style="background: rgba(40, 167, 69, 0.15); backdrop-filter: blur(40px); -webkit-backdrop-filter: blur(40px);
                            padding: 1rem; border-radius: 12px; border: 1px solid rgba(40, 167, 69, 0.2);
                            text-align: center; margin-top: 1rem;">
                    <p style="color: #ffffff; font-size: 1rem; margin: 0;">
                        ✅ 모든 질문이 삭제되었습니다
                    </p>
                </div>
                """, unsafe_allow_html=True)
                st.rerun()
            else:
                st.session_state.confirm_delete = True
                st.markdown("""
                <div style="background: rgba(255, 193, 7, 0.1); backdrop-filter: blur(40px); -webkit-backdrop-filter: blur(40px);
                            padding: 1rem; border-radius: 12px; border: 1px solid rgba(255, 193, 7, 0.2);
                            text-align: center; margin-top: 1rem;">
                    <p style="color: #ffffff; font-size: 1rem; margin: 0;">
                        ⚠️ 다시 클릭하면 삭제됩니다
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        if st.session_state.get("confirm_delete", False):
            if st.button("취소"):
                st.session_state.confirm_delete = False
                st.rerun()
