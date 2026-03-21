import json
import math
from pathlib import Path

import streamlit as st

from llm_pipeline import COMPARE_MODELS, analyze, call_openrouter

# ── Data ──────────────────────────────────────────────────────────────────
DATA_PATH = Path(__file__).parent / "data" / "proverbs.json"


@st.cache_data
def load_data() -> list[dict]:
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


DATASET = load_data()
CATEGORIES = sorted({e["category"] for e in DATASET})

# ── Page config ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Cultural Bridge",
    page_icon="🌉",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
/* Global */
.block-container { max-width: 1100px; }

/* Card */
.proverb-card {
    background: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.proverb-card h3 { margin-top: 0; }

/* Chinese text */
.zh-big {
    font-size: 2.4em;
    font-weight: 700;
    color: #C41E3A;
    line-height: 1.3;
}
.pinyin {
    font-size: 1.1em;
    color: #888;
    margin-bottom: 0.6rem;
}

/* Section labels */
.section-label {
    font-weight: 600;
    color: #555;
    margin-bottom: 0.25rem;
}

/* Russian accent */
.ru-text { color: #2E5090; font-weight: 500; }

/* Source badge */
.badge-human {
    display: inline-block;
    background: #e8f5e9;
    color: #2e7d32;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 0.85em;
    font-weight: 600;
}
.badge-ai {
    display: inline-block;
    background: #e3f2fd;
    color: #1565c0;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 0.85em;
    font-weight: 600;
}

/* Browse grid card */
.browse-card {
    background: #fff;
    border: 1px solid #e8e8e8;
    border-radius: 10px;
    padding: 1.2rem;
    text-align: center;
    min-height: 160px;
    transition: box-shadow 0.15s;
}
.browse-card:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.browse-zh { font-size: 2em; color: #C41E3A; font-weight: 700; }
.browse-py { font-size: 0.9em; color: #999; margin-top: 0.2rem; }
.browse-cat {
    font-size: 0.75em;
    color: #fff;
    background: #C41E3A;
    padding: 2px 8px;
    border-radius: 8px;
    display: inline-block;
    margin-top: 0.5rem;
}
</style>
""",
    unsafe_allow_html=True,
)

# ── Header ────────────────────────────────────────────────────────────────
st.markdown("# 文化桥 &nbsp;|&nbsp; Cultural Bridge")
st.markdown("##### Mandarin-Russian Proverb Translator")

# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Filters")
    selected_cat = st.selectbox(
        "Category",
        ["All"] + CATEGORIES,
        index=0,
    )

    st.markdown("---")
    with st.expander("About this project"):
        st.markdown(
            "This app explores how meaning shifts when Chinese proverbs "
            "are mapped to Russian equivalents. Each proverb is annotated "
            "with a literal translation, cultural context, the closest "
            "Russian saying, and an analysis of what nuance is lost in "
            "translation.\n\n"
            "*Built by Mila Tan — bilingual (Mandarin/Russian) student "
            "exploring cross-cultural NLP.*"
        )

    human_count = len(DATASET)
    st.markdown(
        f"<div style='text-align:center;color:#888;margin-top:1rem;'>"
        f"<b>{human_count}</b> human-annotated &nbsp;|&nbsp; <b>∞</b> AI-analyzed"
        f"</div>",
        unsafe_allow_html=True,
    )


# ── Helpers ───────────────────────────────────────────────────────────────
def render_result_card(data: dict, source: str) -> None:
    badge_cls = "badge-human" if "Human" in source else "badge-ai"
    source_label = "Human-annotated ✓" if "Human" in source else source

    if "error" in data:
        st.error(data["error"])
        return

    st.markdown(
        f"""
<div class="proverb-card">
  <p class="section-label">🔤 Literal Translation</p>
  <p>{data.get('literal', '—')}</p>

  <p class="section-label">💡 Meaning</p>
  <p>{data.get('meaning', '—')}</p>

  <p class="section-label">🇷🇺 Russian Equivalent</p>
  <p class="ru-text">{data.get('russian_equivalent', '—')}</p>

  <p class="section-label">⚠️ What Gets Lost</p>
  <p>{data.get('what_gets_lost', '—')}</p>

  <p class="section-label">📖 Cultural Context</p>
  <p>{data.get('cultural_context', '—')}</p>

  <p class="section-label">🏷️ Source</p>
  <span class="{badge_cls}">{source_label}</span>
</div>
""",
        unsafe_allow_html=True,
    )


# ── Tabs ──────────────────────────────────────────────────────────────────
tab_analyze, tab_browse, tab_compare = st.tabs(
    ["🔍 Analyze", "📚 Browse All", "⚖️ Compare Models"]
)

# ═══════════════════════════════ TAB 1: Analyze ═══════════════════════════
with tab_analyze:
    query = st.text_input(
        "Enter a Chinese proverb",
        placeholder="e.g. 塞翁失马, 欲速则不达 …",
    )
    if query:
        with st.spinner("Analyzing…"):
            result, source = analyze(query, DATASET)

        # Show the Chinese text prominently
        pinyin = result.get("pinyin", "")
        st.markdown(
            f'<div style="text-align:center;margin:1rem 0;">'
            f'<span class="zh-big">{query}</span><br>'
            f'<span class="pinyin">{pinyin}</span></div>',
            unsafe_allow_html=True,
        )
        render_result_card(result, source)
    else:
        st.info("Type a Chinese proverb above to get a full cultural analysis.")

# ═══════════════════════════════ TAB 2: Browse ════════════════════════════
with tab_browse:
    filtered = DATASET
    if selected_cat != "All":
        filtered = [e for e in DATASET if e["category"] == selected_cat]

    st.markdown(f"**{len(filtered)}** proverbs")

    COLS = 3
    rows = math.ceil(len(filtered) / COLS)
    for r in range(rows):
        cols = st.columns(COLS)
        for c in range(COLS):
            idx = r * COLS + c
            if idx >= len(filtered):
                break
            entry = filtered[idx]
            with cols[c]:
                st.markdown(
                    f"""
<div class="browse-card">
  <div class="browse-zh">{entry['chinese']}</div>
  <div class="browse-py">{entry['pinyin']}</div>
  <div class="browse-cat">{entry['category']}</div>
</div>
""",
                    unsafe_allow_html=True,
                )
                with st.expander("View full analysis"):
                    render_result_card(entry, "Human-annotated")

# ═══════════════════════════════ TAB 3: Compare ═══════════════════════════
with tab_compare:
    st.markdown(
        "Compare how **three different LLMs** analyze the same Chinese proverb. "
        "This reveals where models agree on translation and where cultural nuance diverges."
    )
    cmp_query = st.text_input(
        "Enter a Chinese proverb to compare",
        placeholder="e.g. 画蛇添足",
        key="compare_input",
    )
    if cmp_query:
        model_cols = st.columns(len(COMPARE_MODELS))
        results = {}

        with st.spinner("Querying all three models…"):
            for model in COMPARE_MODELS:
                results[model] = call_openrouter(cmp_query, DATASET, model=model)

        for col, model in zip(model_cols, COMPARE_MODELS):
            short_name = model.split("/")[-1].split(":")[0]
            with col:
                st.markdown(f"**{short_name}**")
                data = results[model]
                if "error" in data:
                    st.error(data["error"])
                else:
                    st.markdown(f"**Literal:** {data.get('literal', '—')}")
                    st.markdown(f"**Meaning:** {data.get('meaning', '—')}")
                    st.markdown(
                        f"**🇷🇺 Russian:** <span class='ru-text'>"
                        f"{data.get('russian_equivalent', '—')}</span>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(f"**Lost in translation:** {data.get('what_gets_lost', '—')}")
                    st.markdown(f"**Context:** {data.get('cultural_context', '—')}")

        # Agreement summary
        if all("error" not in results[m] for m in COMPARE_MODELS):
            st.markdown("---")
            st.markdown("#### Agreement Analysis")
            ru_equivs = {
                m.split("/")[-1].split(":")[0]: results[m].get("russian_equivalent", "")
                for m in COMPARE_MODELS
            }
            unique_ru = set(ru_equivs.values())
            if len(unique_ru) == 1:
                st.success("All three models chose the same Russian equivalent.")
            else:
                st.warning(
                    f"Models chose **{len(unique_ru)}** different Russian equivalents — "
                    "highlighting how cultural mapping is subjective."
                )
                for name, equiv in ru_equivs.items():
                    st.markdown(f"- **{name}:** {equiv}")
    else:
        st.info("Enter a proverb above to compare outputs from three LLMs side-by-side.")
