"""
Streamlit 메인 엔트리 포인트 (Streamlit Cloud용)
"""

from pathlib import Path
import importlib.util

target = Path(__file__).parent / "00_질문_수집.py"
spec = importlib.util.spec_from_file_location("main_page", target)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
