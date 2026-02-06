"""
관리자 페이지
질문 관리, 통계, 데이터 내보내기 기능
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
from pathlib import Path

# Google Sheets 연동
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
if USE_GSHEETS:
    try:
        conn_gsheet = st.connection("gsheets", type=GSheetsConnection)
        USE_GSHEETS = True
    except:
        USE_GSHEETS = False

def load_questions():
    """질문 데이터 로드"""
    if USE_GSHEETS:
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
    if USE_GSHEETS and questions:
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
        st.title("🔐 관리자 로그인")
        
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
        st.info("💡 관리자만 접근할 수 있는 페이지입니다")
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
        st.warning("내보낼 질문이 없습니다")
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
    # 헤더
    st.markdown(f"""
    <div style="background-color: {WOORI_BLUE}; padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;">
        <h1 style="color: white; margin: 0; text-align: center;">🔐 관리자 페이지</h1>
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
            st.info("등록된 질문이 없습니다")
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
                        if st.button("🗑️ 삭제", key=f"delete_{q['id']}", type="secondary", use_container_width=True):
                            delete_question(q['id'])
                
                st.markdown("---")
    
    # 탭 2: 통계
    with tab2:
        st.header("📊 통계 정보")
        
        if not questions:
            st.info("통계 데이터가 없습니다")
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
            st.subheader("📝 작성자별 통계")
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
            st.warning("내보낼 데이터가 없습니다")
        else:
            st.info(f"총 {len(questions)}개의 질문을 내보낼 수 있습니다")
            
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
        if USE_GSHEETS:
            st.success("✅ Google Sheets 연동 중")
            st.info("모든 사용자가 같은 질문 목록을 볼 수 있습니다")
        else:
            st.info("ℹ️ 로컬 파일 모드")
            st.warning("Google Sheets 연동을 권장합니다")
        
        st.markdown("---")
        
        st.subheader("🔐 비밀번호 변경")
        st.info("현재 비밀번호: `woori2024`")
        st.warning("⚠️ 비밀번호를 변경하려면 코드를 수정하거나 Streamlit Cloud Secrets를 사용하세요")
        
        st.markdown("---")
        
        st.subheader("🗑️ 전체 데이터 삭제")
        st.error("⚠️ 주의: 이 작업은 되돌릴 수 없습니다!")
        
        if st.button("전체 질문 삭제", type="secondary"):
            if st.session_state.get("confirm_delete", False):
                save_questions([])
                st.session_state.confirm_delete = False
                st.success("✅ 모든 질문이 삭제되었습니다")
                st.rerun()
            else:
                st.session_state.confirm_delete = True
                st.warning("⚠️ 다시 클릭하면 삭제됩니다")
        
        if st.session_state.get("confirm_delete", False):
            if st.button("취소"):
                st.session_state.confirm_delete = False
                st.rerun()
