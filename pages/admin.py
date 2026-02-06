"""
관리자 페이지
질문 관리, 통계, 데이터 내보내기 기능
"""

import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
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

# 데이터 파일 경로
DATA_FILE = "../questions.json"
WORKSHEET_NAME = "questions"

# Google Sheets 연결
conn_gsheet = None
if USE_GSHEETS:
    try:
        conn_gsheet = st.connection("gsheets", type=GSheetsConnection)
        USE_GSHEETS = True
    except:
        USE_GSHEETS = False
        conn_gsheet = None

def load_questions():
    """질문 데이터 로드"""
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
        except:
            pass
    
    # 로컬 파일 사용
    file_path = Path(__file__).parent.parent / DATA_FILE
    if file_path.exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_questions(questions):
    """질문 데이터 저장"""
    if USE_GSHEETS and conn_gsheet and questions:
        try:
            df = pd.DataFrame(questions)
            columns = ['id', 'name', 'question', 'timestamp', 'likes']
            df = df[columns] if all(col in df.columns for col in columns) else df
            conn_gsheet.update(worksheet=WORKSHEET_NAME, data=df)
            st.cache_data.clear()
            return
        except:
            pass
    
    # 로컬 파일 저장
    file_path = Path(__file__).parent.parent / DATA_FILE
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"파일 저장 오류: {e}")

# 페이지 설정
st.set_page_config(
    page_title="관리자 페이지",
    page_icon="🔐",
    layout="wide"
)

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
    
    /* 타이틀 스타일 */
    h1 {{
        color: rgba(255, 255, 255, 0.95);
        font-weight: 700;
        text-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        letter-spacing: -1px;
    }}
    
    h2, h3 {{
        color: rgba(255, 255, 255, 0.95);
        font-weight: 600;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    }}
    
    /* 메트릭 스타일 */
    [data-testid="stMetricValue"] {{
        color: rgba(255, 255, 255, 0.95);
        font-weight: 700;
    }}
    
    [data-testid="stMetricLabel"] {{
        color: rgba(255, 255, 255, 0.7);
    }}
    
    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] {{
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 0.5rem;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        color: rgba(255, 255, 255, 0.7);
        border-radius: 8px;
        transition: all 0.3s ease;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: rgba(255, 255, 255, 0.15);
        color: rgba(255, 255, 255, 0.95);
    }}
    
    /* Expander 스타일 */
    .streamlit-expanderHeader {{
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 12px;
        color: rgba(255, 255, 255, 0.9);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }}
    
    /* Dataframe 스타일 */
    .dataframe {{
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 12px;
    }}
    
    /* Alert 박스 스타일 */
    .stAlert {{
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px;
    }}
    
    /* 셀렉트박스 스타일 */
    .stSelectbox>div>div>select {{
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        color: rgba(255, 255, 255, 0.95);
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
            <h1 style="margin-bottom: 0.5rem; font-size: 3rem; font-weight: 700; letter-spacing: -2px; color: rgba(255, 255, 255, 0.95);">
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
        <div style="background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
                    padding: 1.5rem; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.2);
                    text-align: center;">
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
    # 헤더 - Liquid Glass 스타일
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(0, 76, 151, 0.3), rgba(0, 102, 204, 0.3)); 
                backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
                padding: 2rem; border-radius: 20px; margin-bottom: 2rem;
                border: 1px solid rgba(255, 255, 255, 0.2);
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);">
        <h1 style="color: rgba(255, 255, 255, 0.95); margin: 0; text-align: center; font-weight: 700; font-size: 2.5rem; letter-spacing: -1px;">
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
            <div style="background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
                        padding: 2rem; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.2);
                        text-align: center;">
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
            
            st.metric("총 질문 수", len(questions))
            st.metric("필터링된 질문 수", len(filtered_questions))
            
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
            <div style="background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
                        padding: 1.5rem; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.2);
                        text-align: center;">
                <p style="color: rgba(255, 255, 255, 0.9); font-size: 1.1rem; margin: 0;">
                    ℹ️ 방문자 통계 기능을 사용할 수 없습니다
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # 질문 통계
        st.subheader("📝 질문 통계")
        if not questions:
            st.markdown("""
            <div style="background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
                        padding: 2rem; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.2);
                        text-align: center;">
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
            <div style="background: rgba(255, 193, 7, 0.15); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
                        padding: 1.5rem; border-radius: 16px; border: 1px solid rgba(255, 193, 7, 0.3);
                        text-align: center;">
                <p style="color: rgba(255, 255, 255, 0.95); font-size: 1.1rem; margin: 0;">
                    내보낼 데이터가 없습니다
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background: rgba(0, 102, 204, 0.2); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
                        padding: 1.5rem; border-radius: 16px; border: 1px solid rgba(0, 102, 204, 0.3);
                        text-align: center; margin-bottom: 1.5rem;">
                <p style="color: rgba(255, 255, 255, 0.95); font-size: 1.1rem; margin: 0;">
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
        if USE_GSHEETS and conn_gsheet:
            st.markdown("""
            <div style="background: rgba(40, 167, 69, 0.2); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
                        padding: 1rem; border-radius: 12px; border: 1px solid rgba(40, 167, 69, 0.3);
                        text-align: center;">
                <p style="color: rgba(255, 255, 255, 0.95); font-size: 1rem; margin: 0;">
                    ✅ 데이터 저장소 연결됨
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
                        padding: 1rem; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.2);
                        text-align: center;">
                <p style="color: rgba(255, 255, 255, 0.9); font-size: 1rem; margin: 0;">
                    ℹ️ 로컬 파일 모드
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.subheader("🔐 비밀번호 변경")
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
                    padding: 1rem; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.2);
                    margin-bottom: 1rem;">
            <p style="color: rgba(255, 255, 255, 0.9); font-size: 1rem; margin: 0;">
                현재 비밀번호: <code style="background: rgba(0, 0, 0, 0.2); padding: 0.2rem 0.5rem; border-radius: 4px;">woori2024</code>
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style="background: rgba(255, 193, 7, 0.15); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
                    padding: 1rem; border-radius: 12px; border: 1px solid rgba(255, 193, 7, 0.3);">
            <p style="color: rgba(255, 255, 255, 0.95); font-size: 1rem; margin: 0;">
                ⚠️ 비밀번호를 변경하려면 코드를 수정하거나 Streamlit Cloud Secrets를 사용하세요
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.subheader("🗑️ 전체 데이터 삭제")
        st.markdown("""
        <div style="background: rgba(220, 53, 69, 0.2); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
                    padding: 1rem; border-radius: 12px; border: 1px solid rgba(220, 53, 69, 0.3);
                    margin-bottom: 1rem;">
            <p style="color: rgba(255, 255, 255, 0.95); font-size: 1rem; margin: 0; font-weight: 600;">
                ⚠️ 주의: 이 작업은 되돌릴 수 없습니다!
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("전체 질문 삭제", type="secondary"):
            if st.session_state.get("confirm_delete", False):
                save_questions([])
                st.session_state.confirm_delete = False
                st.markdown("""
                <div style="background: rgba(40, 167, 69, 0.2); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
                            padding: 1rem; border-radius: 12px; border: 1px solid rgba(40, 167, 69, 0.3);
                            text-align: center; margin-top: 1rem;">
                    <p style="color: rgba(255, 255, 255, 0.95); font-size: 1rem; margin: 0;">
                        ✅ 모든 질문이 삭제되었습니다
                    </p>
                </div>
                """, unsafe_allow_html=True)
                st.rerun()
            else:
                st.session_state.confirm_delete = True
                st.markdown("""
                <div style="background: rgba(255, 193, 7, 0.15); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
                            padding: 1rem; border-radius: 12px; border: 1px solid rgba(255, 193, 7, 0.3);
                            text-align: center; margin-top: 1rem;">
                    <p style="color: rgba(255, 255, 255, 0.95); font-size: 1rem; margin: 0;">
                        ⚠️ 다시 클릭하면 삭제됩니다
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        if st.session_state.get("confirm_delete", False):
            if st.button("취소"):
                st.session_state.confirm_delete = False
                st.rerun()
