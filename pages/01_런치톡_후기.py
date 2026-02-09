"""
런치톡 후기 & 기록 페이지
비밀번호로 보호되는 요약 / 블로그 / 오디오 / PDF 뷰어
"""

from pathlib import Path
import base64
import re

import streamlit as st
import streamlit.components.v1 as components

# 페이지 기본 설정
st.set_page_config(
    page_title="런치톡 후기",
    page_icon="🎧",
    layout="wide",
)

# 상수 및 경로 설정
PASSWORD = "20f0isa626"

BASE_DIR = Path(__file__).parent.parent
RECORD_DIR = BASE_DIR / "lunch_talk_record"

SUMMARY_FILE = RECORD_DIR / "lunch_talk_summary.txt"
BLOG_FILE = RECORD_DIR / "google_nootbook_blog.txt"
AUDIO_FILE = RECORD_DIR / "금융_IT_자소서엔_기술_스택_말고_고민을_담아라.m4a"
PDF_FILE = RECORD_DIR / "현직_선배의_금융_IT_공략집.pdf"

# 멘토 프로필 PDF (사진이 포함된 프로필 PDF라 가정)
MENTOR_PDF_SONG = RECORD_DIR / "(우리FISA 6기) 런치톡 멘토 프로필_송지현 계장님.pdf"
MENTOR_PDF_KIM = RECORD_DIR / "(우리FISA 6기) 런치톡 멘토 프로필_김혁준 계장님.pdf"


def load_text(path: Path) -> str:
    """텍스트 파일을 안전하게 읽기"""
    try:
        if path.exists():
            return path.read_text(encoding="utf-8")
    except Exception:
        pass
    return ""


def format_summary_text(raw: str) -> str:
    """
    원본 summary 텍스트에서:
    - '### 인터뷰 정보' 제목 제거
    - 시간 표기([09:44] 등) 제거
    - Q/A 블록을 조금 더 눈에 띄게 정리
    """
    if not raw.strip():
        return ""

    lines = raw.splitlines()
    filtered = []
    for line in lines:
        stripped = line.strip()
        # '인터뷰 정보' 제목은 제거
        if stripped.startswith("### 인터뷰 정보"):
            continue
        # 시간 태그 제거
        no_time = re.sub(r"\[\d{2}:\d{2}\]", "", line).rstrip()
        filtered.append(no_time)

    processed: list[str] = []
    for line in filtered:
        stripped = line.lstrip()

        # 섹션 헤더는 그대로 (조금 띄워 주기)
        if stripped.startswith("**["):
            processed.append("")
            processed.append(stripped)
        # 질문: 굵게 한 줄로 강조
        elif stripped.startswith("- **Q:"):
            q_text = stripped[len("- ") :].strip()  # "- " 제거
            processed.append("")
            processed.append(q_text)  # 이미 **Q: ...** 형태
            processed.append("")  # 질문과 답변 사이 공백 한 줄
        # 답변: 말풍선 이모지 + bullet 로 줄마다 분리
        elif stripped.startswith("- A:"):
            a_text = stripped[len("- A:") :].strip()
            processed.append(f"- 💬 {a_text}")
        else:
            processed.append(line)

    return "\n".join(processed)


def render_qa_body(body: str) -> None:
    """
    Summary 섹션 본문에서 Q/A 쌍을 찾아
    - Q/A 한 묶음씩 카드 형태로 렌더링
    """
    lines = body.splitlines()
    qa_blocks: list[tuple[str, str]] = []

    def normalize_line(line: str) -> str:
        return line.strip().strip("*").strip()

    def is_q_line(line: str) -> bool:
        return normalize_line(line).startswith("Q.")

    def is_a_line(line: str) -> bool:
        return normalize_line(line).startswith("A.")

    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if is_q_line(line):
            q_text = normalize_line(line)[2:].strip()
            i += 1

            # 공백 라인은 스킵
            while i < n and not lines[i].strip():
                i += 1

            answer_parts: list[str] = []
            if i < n and is_a_line(lines[i]):
                first = normalize_line(lines[i])[2:].strip()
                if first:
                    answer_parts.append(first)
                i += 1

            while i < n and not is_q_line(lines[i]):
                answer_parts.append(lines[i])
                i += 1

            answer = "\n".join(answer_parts).strip()
            qa_blocks.append((q_text, answer))
        else:
            i += 1

    if not qa_blocks:
        st.markdown(body)
        return

    for q_text, answer in qa_blocks:
        answer_lines = [ln.strip() for ln in answer.splitlines() if ln.strip()]
        answer_html = "<br/>".join(answer_lines)
        qa_html = f"""
<div class="qa-card">
  <div class="qa-q">❓ Q. {q_text}</div>
  <div class="qa-a"><span class="summary-a-label">💬 A.</span> {answer_html}</div>
</div>
"""
        st.markdown(qa_html, unsafe_allow_html=True)


def format_blog_text(raw: str) -> str:
    """
    일반 텍스트 형태의 블로그 글을 마크다운 형태로 보기 좋게 변환.
    - 첫 번째 줄: 큰 제목
    - 구분선(----, ----)은 마크다운 수평선으로
    - '1. [Takeaway ...]' 같은 라인은 섹션 제목으로 처리
    """
    if not raw.strip():
        return ""

    lines = raw.splitlines()
    # 첫 번째 비어있지 않은 줄을 제목으로 사용
    title_idx = None
    for i, line in enumerate(lines):
        if line.strip():
            title_idx = i
            break

    markdown_parts = []

    if title_idx is not None:
        title = lines[title_idx].strip()
        markdown_parts.append(f"## {title}")
        markdown_parts.append("")  # 공백 줄

    for i, line in enumerate(lines):
        if title_idx is not None and i == title_idx:
            continue  # 이미 제목으로 사용

        stripped = line.strip()

        # 긴 구분선 -> 수평선
        if set(stripped) == {"-"} and len(stripped) >= 4:
            markdown_parts.append("---")
            continue

        # 번호 매겨진 Takeaway 제목
        if stripped and stripped[0].isdigit() and stripped[1:3] in [". ", ".)"]:
            markdown_parts.append(f"### {stripped}")
            continue

        markdown_parts.append(line)

    return "\n".join(markdown_parts)


def pdf_to_html_embed(path: Path, height: int = 700) -> None:
    """
    PDF를 내장 iframe 뷰어로 임베드.
    - streamlit[pdf] 컴포넌트 없이도 동작하도록 st.pdf는 사용하지 않음
    - 별도의 다운로드 버튼은 제공하지 않고, 페이지 내에서만 열람 가능하도록 구성
    (브라우저/환경 특성상 완전한 다운로드 차단은 기술적으로 불가능합니다.)
    """
    if not path.exists():
        st.error(f"PDF 파일을 찾을 수 없습니다: {path.name}")
        return

    try:
        with path.open("rb") as f:
            pdf_bytes = f.read()
        b64 = base64.b64encode(pdf_bytes).decode("utf-8")

        # pdf.js 기반 간단 뷰어
        html = f"""
        <div id="pdf-viewer" style="width:100%; background:#111827; border-radius:12px; padding:12px; border:1px solid rgba(255,255,255,0.15);">
            <div style="display:flex; gap:8px; align-items:center; margin-bottom:8px;">
                <button id="prev" style="padding:6px 12px; border-radius:8px; border:1px solid #3b82f6; background:#1f2937; color:#fff;">이전</button>
                <button id="next" style="padding:6px 12px; border-radius:8px; border:1px solid #3b82f6; background:#1f2937; color:#fff;">다음</button>
                <span id="page-info" style="color:#e5e7eb; font-size:0.9rem;">1 / ?</span>
            </div>
            <canvas id="pdf-canvas" style="width:100%; border-radius:8px; background:#fff;"></canvas>
        </div>

        <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
        <script>
            const pdfData = atob("{b64}");
            const pdfjsLib = window['pdfjs-dist/build/pdf'];
            pdfjsLib.GlobalWorkerOptions.workerSrc = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";

            let pdfDoc = null;
            let pageNum = 1;
            let pageRendering = false;
            let pageNumPending = null;
            const scale = 1.2;
            const canvas = document.getElementById('pdf-canvas');
            const ctx = canvas.getContext('2d');

            function renderPage(num) {{
                pageRendering = true;
                pdfDoc.getPage(num).then(function(page) {{
                    const viewport = page.getViewport({{scale: scale}});
                    canvas.height = viewport.height;
                    canvas.width = viewport.width;
                    const renderContext = {{
                        canvasContext: ctx,
                        viewport: viewport
                    }};
                    const renderTask = page.render(renderContext);
                    renderTask.promise.then(function() {{
                        pageRendering = false;
                        if (pageNumPending !== null) {{
                            renderPage(pageNumPending);
                            pageNumPending = null;
                        }}
                    }});
                    document.getElementById('page-info').textContent = num + " / " + pdfDoc.numPages;
                }});
            }}

            function queueRenderPage(num) {{
                if (pageRendering) {{
                    pageNumPending = num;
                }} else {{
                    renderPage(num);
                }}
            }}

            function onPrevPage() {{
                if (pageNum <= 1) {{
                    return;
                }}
                pageNum--;
                queueRenderPage(pageNum);
            }}

            function onNextPage() {{
                if (pageNum >= pdfDoc.numPages) {{
                    return;
                }}
                pageNum++;
                queueRenderPage(pageNum);
            }}

            document.getElementById('prev').addEventListener('click', onPrevPage);
            document.getElementById('next').addEventListener('click', onNextPage);

            const loadingTask = pdfjsLib.getDocument({{data: pdfData}});
            loadingTask.promise.then(function(pdf) {{
                pdfDoc = pdf;
                renderPage(pageNum);
            }});
        </script>
        """
        components.html(html, height=height + 80)
    except Exception as e:
        st.error(f"PDF를 표시하는 중 오류가 발생했습니다: {e}")


# 기존 요약에 보완 내용을 덧붙인 summary (원본 파일은 수정하지 않음)
EXTRA_SUMMARY = """
### 🔎 대화 맥락 & 추가 정리

- 런치톡 분위기와 시작  
  - 클라우드/AI 반의 반장 이야기, 반의 성향(다소 소심하지만 점점 친해지는 분위기), 아이스브레이킹 게임 등으로 친해지는 과정이 먼저 언급되었습니다.  
  - 태국 음식점에서 세트 메뉴와 음료를 고르며 자연스럽게 대화를 시작했고, 편안한 점심 자리라는 분위기가 강조되었습니다.

- 교육생들의 배경과 관계  
  - AI·클라우드 등 과정별로 이미 취업한 친구, 인턴 경험이 있는 동기 등 다양한 배경의 교육생들이 함께했고, 서로의 진로와 고민을 공유하는 자리가 되었습니다.  
  - 특히 이미 취업한 동기(석·박사, 인턴 경험 보유) 사례를 통해 “스펙만이 아니라 방향 설정과 지원 전략”이 중요하다는 메시지가 나왔습니다.

- 인턴십의 실제 모습  
  - 금융권 인턴은 보안/권한 문제로 인해 “실제 개발 업무를 깊게 맡기기보다는 환경 이해와 공부 중심의 체험”에 가깝다는 현실적인 설명이 있었습니다.  
  - 그럼에도 불구하고 현업 환경을 가까이에서 보고, 실무자와 직접 대화하는 경험 자체가 큰 자산이라는 점을 여러 번 강조했습니다.

- 자소서·포트폴리오를 위한 기록 습관  
  - 프로젝트를 하면서 노션, 엑셀, 업무일지 등으로 매일 기록해 두면 나중에 자소서나 면접 준비가 훨씬 수월하다는 팁이 나왔습니다.  
  - “처음부터 완벽하게 구조를 잡으려 하지 말고, 일단 다 써놓고 나중에 분류/정리하라”는 현실적인 방법이 소개되었습니다.

- 프로젝트 개수보다 ‘어필하고 싶은 프로젝트’가 더 중요  
  - 포트폴리오에는 여러 프로젝트를 써도 되지만, 자소서와 면접에서 깊게 가져갈 프로젝트는 1~3개 정도로 집중하는 것이 좋다는 의견이 나왔습니다.  
  - 실서비스 경험이 있다면 큰 강점이지만, 없더라도 “예외 상황 설계, 장애 시나리오, 안정성/비용을 고민한 흔적”을 녹여내면 충분히 경쟁력이 있다는 메시지가 나왔습니다.

- 실무에서 요구되는 태도(적극성·멀티태스킹)  
  - 단순히 지시받은 일만 처리하는 것이 아니라, 그 뒤에 생길 수 있는 영향과 후속 이슈까지 미리 질문하고 고민하는 적극성이 중요하다고 했습니다.  
  - 특히 인프라/보안 조직은 동시에 여러 건을 처리해야 할 때가 많아, 우선순위 판단과 멀티태스킹 능력이 실제로 큰 평가 요소가 된다고 언급했습니다.

- 조직 문화와 ‘모나지 않음’의 중요성  
  - 금융 IT는 보수적인 분위기가 강한 편이라, 너무 강한 자기 주장보다는 겸손하고 배우려는 태도가 신입에게 더 중요한 덕목으로 언급되었습니다.  
  - “회사와 팀의 색깔에 맞춰 적응하려는 마음가짐”을 보여주면, 기술 역량이 조금 부족해도 함께 일하고 싶은 사람으로 보일 수 있다는 조언이 나왔습니다.
"""


# 공통 스타일 (메인 페이지와 비슷한 다크/블루 테마)
WOORI_BLUE = "#004C97"
WOORI_LIGHT_BLUE = "#0066CC"

st.markdown(
    f"""
<style>
    .main {{
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0f1419 100%);
        min-height: 100vh;
    }}
    .block-container {{
        background: transparent;
        padding: 1.5rem 2rem;
        margin-top: 0.5rem;
    }}
    h1 {{
        color: #ffffff;
        font-weight: 700;
        font-size: 1.9rem;
        letter-spacing: -0.5px;
        margin-bottom: 0.5rem;
    }}
    h2, h3 {{
        color: #ffffff;
        font-weight: 600;
    }}
    .section-card {{
        background: rgba(255, 255, 255, 0.10);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        padding: 1.75rem;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.18);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
        margin-bottom: 1.5rem;
    }}
    .stButton>button {{
        background: {WOORI_BLUE};
        color: white;
        border-radius: 999px;
        padding: 0.55rem 1.6rem;
        font-weight: 600;
        font-size: 0.95rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.2s ease;
    }}
    .stButton>button:hover {{
        background: {WOORI_LIGHT_BLUE};
        transform: translateY(-1px);
    }}
    .password-box {{
        max-width: 420px;
        margin: 3rem auto 0 auto;
        text-align: center;
    }}
    .password-box-inner {{
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        padding: 2rem 1.8rem;
        border-radius: 18px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.6);
    }}
    .password-box h1 {{
        font-size: 1.8rem;
        margin-bottom: 0.5rem;
    }}
    .password-desc {{
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.95rem;
        margin-bottom: 1.2rem;
    }}
    .hero-sub {{
        color: rgba(255, 255, 255, 0.75);
        font-size: 0.95rem;
        margin-top: 0;
    }}
    /* 기본 본문 텍스트 색상 조금 더 선명하게 */
    p, li, span {{
        color: rgba(255, 255, 255, 0.96);
    }}
    .meta-badge {{
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.2rem 0.7rem;
        border-radius: 999px;
        border: 1px solid rgba(255, 255, 255, 0.25);
        color: rgba(255, 255, 255, 0.85);
        font-size: 0.8rem;
        background: rgba(0, 0, 0, 0.25);
    }}
    /* Summary용 콜아웃(섹션 헤더 박스) 스타일 */
    .summary-callout {{
        background: linear-gradient(135deg, rgba(0, 76, 151, 0.35), rgba(0, 102, 204, 0.18));
        border: 1px solid rgba(0, 102, 204, 0.45);
        border-left: 6px solid {WOORI_LIGHT_BLUE};
        padding: 1rem 1.2rem;
        border-radius: 14px;
        color: rgba(255, 255, 255, 0.98);
        margin: 0.6rem 0 0.9rem 0;
        box-shadow: 0 8px 22px rgba(0, 0, 0, 0.5);
        font-weight: 700;
    }}
    .summary-q {{
        color: rgba(255, 255, 255, 1.0);
        font-weight: 700;
    }}
    .summary-a-label {{
        color: rgba(255, 255, 255, 0.9);
        font-weight: 700;
    }}
    /* Q/A 카드 스타일 */
    .qa-card {{
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-left: 4px solid rgba(255, 255, 255, 0.25);
        padding: 0.95rem 1.05rem;
        border-radius: 12px;
        margin: 0.35rem 0 0.95rem 0;
        box-shadow: 0 5px 14px rgba(0, 0, 0, 0.4);
    }}
    .qa-q {{
        font-weight: 700;
        color: rgba(255, 255, 255, 0.98);
        margin-bottom: 0.5rem;
    }}
    .qa-a {{
        color: rgba(255, 255, 255, 0.95);
        line-height: 1.7;
    }}
    /* 기본 사이드바 네비게이션 숨김 */
    [data-testid="stSidebarNav"] {{
        display: none;
    }}
</style>
""",
    unsafe_allow_html=True,
)

# 사이드바 메뉴
with st.sidebar:
    st.markdown("### 📌 메뉴")
    st.page_link("app.py", label="질문 수집", icon="💬")
    st.page_link("pages/01_런치톡_후기.py", label="런치톡 후기", icon="📝")
    st.page_link("pages/02_관리자.py", label="관리자", icon="🔐")


# 비밀번호 인증 상태
if "lunch_talk_unlocked" not in st.session_state:
    st.session_state.lunch_talk_unlocked = False


def password_gate():
    """비밀번호 입력 UI"""
    st.markdown(
        """
        <div class="password-box">
            <div class="password-box-inner">
                <h1>🎧 런치톡 후기 아카이브</h1>
                <p class="password-desc">
                    우리 FISA 교육생만을 위한 비공개 런치톡 기록입니다.<br/>
                    아래에 비밀번호를 입력하면 내용을 확인할 수 있어요.<br/><br/>
                    ⚠️ 이 페이지의 내용은 실제 런치톡 전체를 그대로 옮긴 것이 아니라,<br/>
                    기억에 남는 핵심 내용과 인사이트만 정리한 요약본입니다.<br/>
                    모든 정보를 절대적인 사실로 받아들이기보다는,<br/>
                    취업 전략을 세울 때 참고용 인사이트로 활용해 주세요.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    pwd = st.text_input("비밀번호를 입력하세요", type="password")
    col_empty_left, col_login, col_reset, col_empty_right = st.columns([2, 1, 1, 2])
    with col_login:
        if st.button("입장하기", type="primary", width="stretch"):
            if pwd == PASSWORD:
                st.session_state.lunch_talk_unlocked = True
                st.success("✅ 인증이 완료되었습니다.")
                st.rerun()
            else:
                st.error("❌ 비밀번호가 올바르지 않습니다.")
    with col_reset:
        if st.button("초기화", width="stretch"):
            st.session_state.lunch_talk_unlocked = False
            st.rerun()


if not st.session_state.lunch_talk_unlocked:
    password_gate()
    st.stop()


# 본문 헤더
st.markdown(
    """
<div class="section-card" style="margin-top: 0.5rem;">
    <div style="display:flex; align-items:flex-start; justify-content:space-between; gap:1rem; flex-wrap:wrap;">
        <div>
            <div class="meta-badge">우리 FISA 런치톡 · 비공개 아카이브</div>
            <h1>현직 선배의 금융 IT 공략집 · 런치톡 후기</h1>
            <p class="hero-sub">
                점심시간 동안 나눴던 금융 IT 커리어 이야기, 자소서/면접 실전 팁, 인프라·보안 직무 인사이트를 한 페이지에 정리했습니다.
            </p>
        </div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)


# 탭 구성
tab_intro, tab_summary, tab_blog, tab_audio, tab_pdf = st.tabs(
    ["👥 멘토 소개", "📝 Summary 정리", "📰 블로그형 글", "🎧 런치톡 팟캐스트", "📑 자료집 슬라이드"]
)


with tab_intro:
    st.markdown("### 👥 멘토 프로필")
    st.markdown(
        """
우리 FISA 1기 수료 후 입사한 정보보안부 송지영 계장, 클라우드 엔지니어링부 김혁준 계장님의 런치톡입니다.  
두 분 모두 교육생 시절의 고민부터 실제 입사까지의 여정을 솔직하게 나눠주셨어요.
"""
    )

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("🔐 정보보안부 송지영 계장")
        st.caption("보안·안정성을 최우선으로 보는 금융 IT 보안 전문가")
        st.markdown(
            """
- FISA 1기 수료 후 우리FIS 입사  
- 정보보안부 근무, 보안 정책·시스템 운영  
- 탄탄한 준비와 면접 연습(질문 200개 준비)의 대표 사례
"""
        )

    with col_b:
        st.subheader("☁️ 클라우드 엔지니어링부 김혁준 계장")
        st.caption("비전공자로 시작해 개발·인프라를 모두 경험한 클라우드 엔지니어")
        st.markdown(
            """
- 비전공자 출신으로 백엔드 개발을 거쳐 인프라로 전향  
- 우리FIS 1기 수료 후 클라우드 엔지니어링부 입사  
- 개발·인프라를 모두 아우르는 취업 전략과 기술 선택 인사이트 공유
"""
        )

    st.markdown("---")
    st.markdown("#### 📸 멘토 프로필 카드")

    col_p1, col_p2 = st.columns(2)

    with col_p1:
        st.markdown("##### 🔐 송지현 계장님 프로필")
        if MENTOR_PDF_SONG.exists():
            pdf_to_html_embed(MENTOR_PDF_SONG, height=420)
        else:
            st.info(f"`{MENTOR_PDF_SONG.name}` 파일을 찾을 수 없습니다.")

    with col_p2:
        st.markdown("##### ☁️ 김혁준 계장님 프로필")
        if MENTOR_PDF_KIM.exists():
            pdf_to_html_embed(MENTOR_PDF_KIM, height=420)
        else:
            st.info(f"`{MENTOR_PDF_KIM.name}` 파일을 찾을 수 없습니다.")


with tab_summary:
    st.markdown("### 📝 런치톡 Summary")

    original = load_text(SUMMARY_FILE)
    if not original:
        st.error("`lunch_talk_summary.txt` 파일을 찾을 수 없거나 내용이 비어 있습니다.")
    else:
        # HTML 줄바꿈 태그(<br/>) 등은 제거하고, 섹션별로 나눈 뒤
        # 섹션 제목만 콜아웃 박스로, 본문(Q/A)은 기본 텍스트로 표시
        clean = re.sub(r"<br\s*/?>", "", original)
        # 마크다운 굵게(** **) 제거
        clean = re.sub(r"\*\*(.*?)\*\*", r"\1", clean)
        sections = re.split(r"^## ", clean, flags=re.MULTILINE)

        # 첫 블록은 제목 및 인터뷰 개요 (그대로 출력)
        preface = sections[0].strip()
        if preface:
            st.markdown(preface)
            st.markdown("---")

        # 이후 각 섹션은 Notion 콜아웃처럼 박스 형태로 렌더링
        for sec in sections[1:]:
            sec = sec.strip()
            if not sec:
                continue
            lines = sec.splitlines()
            if not lines:
                continue

            heading = lines[0].strip()
            body_lines = lines[1:]
            body = "\n".join(body_lines).strip()
            if not body:
                continue

            # 섹션 제목 콜아웃 박스
            st.markdown(
                f"""
<div class="summary-callout">
💡 {heading}
</div>
""",
                unsafe_allow_html=True,
            )

            # 섹션 본문(Q/A)은 Q/A 한 쌍씩 박스 형태로 렌더링
            render_qa_body(body)
            st.markdown("")  # 섹션 간 여백


with tab_blog:
    st.markdown("### 📰 블로그형 정리")
    blog_text = load_text(BLOG_FILE)

    if blog_text.strip():
        pretty_blog = format_blog_text(blog_text)

        # 제목(첫 줄)과 나머지 본문을 분리해서 카드 형태로 렌더링
        lines = pretty_blog.splitlines()
        title = ""
        body_lines = []
        for line in lines:
            if line.strip().startswith("## ") and not title:
                title = line.strip().lstrip("#").strip()
            else:
                body_lines.append(line)
        body_md = "\n".join(body_lines).strip()

        # 메인 카드
        st.markdown(
            f"""
<div class="section-card">
  <h2 style="margin-top:0; margin-bottom:0.5rem;">📘 {title}</h2>
  <p class="hero-sub" style="margin-bottom:1.2rem;">
    런치톡에서 나왔던 금융 IT 취업 인사이트를 블로그 형식으로 정리한 글입니다.
  </p>
</div>
""",
            unsafe_allow_html=True,
        )

        # 본문은 약간 좁은 폭으로 중앙 정렬
        st.markdown(
            f"""
<div style="max-width: 880px; margin: 0 auto 2rem auto; line-height: 1.7; font-size: 0.98rem;">
{body_md}
</div>
""",
            unsafe_allow_html=True,
        )
    else:
        st.warning("`google_nootbook_blog.txt` 파일이 비어 있거나 내용을 찾을 수 없습니다. 파일에 내용을 채워두면 이 탭에서 자동으로 보여드립니다.")


with tab_audio:
    st.markdown("### 🎧 런치톡 팟캐스트 듣기")
    st.caption("런치톡 내용을 토대로 AI 팟캐스트를 만들어봤습니다. 이동하면서 한번 들어보세요!")

    if AUDIO_FILE.exists():
        with st.container():
            st.audio(str(AUDIO_FILE), format="audio/mpeg")
    else:
        st.error(f"오디오 파일을 찾을 수 없습니다: {AUDIO_FILE.name}")


with tab_pdf:
    st.markdown("### 📑 현직 선배의 금융 IT 공략집 (PDF)")
    if PDF_FILE.exists():
        pdf_to_html_embed(PDF_FILE, height=720)
    else:
        st.error(f"PDF 파일을 찾을 수 없습니다: {PDF_FILE.name}")
