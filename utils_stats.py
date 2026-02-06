"""
통계 및 방문자 추적 유틸리티
"""

import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
from pathlib import Path

# 통계 데이터 파일 경로
STATS_FILE = "stats.json"
STATS_WORKSHEET = "stats"

def get_session_id():
    """세션 ID 생성 (간단한 방법)"""
    if 'session_id' not in st.session_state:
        import random
        import string
        st.session_state.session_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    return st.session_state.session_id

def load_stats():
    """통계 데이터 로드"""
    # Google Sheets 사용 시도
    try:
        from st_gsheets_connection import GSheetsConnection
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet=STATS_WORKSHEET, ttl=0)
        if df is not None and not df.empty:
            return df.to_dict('records')
    except:
        pass
    
    # 로컬 파일 사용
    file_path = Path(STATS_FILE)
    if file_path.exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_stats(stats):
    """통계 데이터 저장"""
    # Google Sheets 사용 시도
    try:
        from st_gsheets_connection import GSheetsConnection
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = pd.DataFrame(stats)
        conn.update(worksheet=STATS_WORKSHEET, data=df)
        return
    except:
        pass
    
    # 로컬 파일 저장
    try:
        with open(STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
    except:
        pass

def track_visit():
    """방문 추적"""
    session_id = get_session_id()
    stats = load_stats()
    
    # 오늘 날짜
    today = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 기존 방문 기록 확인
    existing_visit = None
    for stat in stats:
        if stat.get('session_id') == session_id and stat.get('date') == today:
            existing_visit = stat
            break
    
    if existing_visit:
        # 기존 방문 기록 업데이트 (마지막 접속 시간)
        existing_visit['last_visit'] = current_time
        existing_visit['visit_count'] = existing_visit.get('visit_count', 0) + 1
    else:
        # 새 방문 기록 추가
        stats.append({
            'session_id': session_id,
            'date': today,
            'first_visit': current_time,
            'last_visit': current_time,
            'visit_count': 1
        })
    
    save_stats(stats)
    return stats

def get_current_visitors(stats):
    """현재 접속 중인 사용자 수 계산 (최근 5분 이내)"""
    if not stats:
        return 0
    
    current_time = datetime.now()
    active_count = 0
    
    for stat in stats:
        try:
            last_visit_str = stat.get('last_visit', '')
            if last_visit_str:
                last_visit = datetime.strptime(last_visit_str, "%Y-%m-%d %H:%M:%S")
                # 최근 5분 이내 접속
                if (current_time - last_visit).total_seconds() < 300:
                    active_count += 1
        except:
            pass
    
    return active_count

def get_daily_stats(stats):
    """일일 통계"""
    today = datetime.now().strftime("%Y-%m-%d")
    today_stats = [s for s in stats if s.get('date') == today]
    
    unique_visitors = len(set(s.get('session_id') for s in today_stats))
    total_visits = sum(s.get('visit_count', 0) for s in today_stats)
    
    return {
        'unique_visitors': unique_visitors,
        'total_visits': total_visits,
        'current_visitors': get_current_visitors(today_stats)
    }

def get_all_time_stats(stats):
    """전체 기간 통계"""
    if not stats:
        return {
            'total_unique_visitors': 0,
            'total_visits': 0,
            'average_visits_per_day': 0
        }
    
    unique_visitors = len(set(s.get('session_id') for s in stats))
    total_visits = sum(s.get('visit_count', 0) for s in stats)
    
    # 날짜별 방문자 수
    dates = set(s.get('date') for s in stats if s.get('date'))
    days_count = len(dates) if dates else 1
    
    return {
        'total_unique_visitors': unique_visitors,
        'total_visits': total_visits,
        'average_visits_per_day': round(total_visits / days_count, 1) if days_count > 0 else 0
    }
