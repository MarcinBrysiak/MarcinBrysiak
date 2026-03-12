"""Agent Monitor Dashboard.

Minimal Streamlit dashboard for running the content writer agent
and viewing its output. First dashboard to ship — extend as needed.

Run:
    streamlit run dashboards/agent_monitor/app.py
"""

import streamlit as st

from agents.content_writer import ContentWriterAgent
from config.feature_flags import is_enabled
from config.models import DEFAULT_MODEL, HAIKU, SONNET

st.set_page_config(
    page_title="Marketing AI — Agent Monitor",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 Marketing AI — Agent Monitor")
st.caption("Internal tool · not for external distribution")

# ── Sidebar ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.header("Settings")

    model_options = {
        "Opus 4.6 (default — best quality)": DEFAULT_MODEL.id,
        "Sonnet 4.6 (balanced)": SONNET.id,
        "Haiku 4.5 (fast / cheap)": HAIKU.id,
    }
    selected_label = st.selectbox("Model", list(model_options.keys()))
    selected_model = model_options[selected_label]

    dry_run = st.toggle("Dry run (don't save files)", value=True)

    st.divider()
    st.subheader("Feature Flags")
    for flag in ["content_writer", "campaign_analyst", "lead_scorer"]:
        status = "✅ enabled" if is_enabled(flag) else "❌ disabled"
        st.text(f"{flag}: {status}")

# ── Content Writer Tab ─────────────────────────────────────────────────────────

tab_writer, tab_coming_soon = st.tabs(["✍️ Content Writer", "📊 Coming Soon"])

with tab_writer:
    if not is_enabled("content_writer"):
        st.warning("Content Writer feature is disabled. Set FEATURE_CONTENT_WRITER=true in .env")
        st.stop()

    col1, col2 = st.columns(2)

    with col1:
        topic = st.text_input("Topic", placeholder="How AI is transforming B2B marketing")
        target_audience = st.selectbox(
            "Target audience",
            ["Marketing Manager", "CMO", "Content Specialist"],
        )
        word_count = st.slider("Word count", 400, 1600, 800, 100)

    with col2:
        keywords = st.text_input(
            "SEO keywords (comma-separated)",
            placeholder="AI marketing, marketing automation",
        )
        tone_notes = st.text_area(
            "Additional tone notes",
            placeholder="Make it more conversational than usual",
            height=80,
        )

    if st.button("✨ Generate draft", type="primary", disabled=not topic):
        with st.spinner("Writing…"):
            agent = ContentWriterAgent(model=selected_model, dry_run=dry_run)
            draft = agent.write_blog_post(
                topic=topic,
                target_audience=target_audience,
                word_count=word_count,
                keywords=keywords,
                tone_notes=tone_notes,
            )

        st.success(f"Done! {draft.input_tokens} input / {draft.output_tokens} output tokens")

        with st.expander("Tools called", expanded=False):
            st.write(draft.tool_calls if draft.tool_calls else "None")

        st.divider()
        st.subheader("Draft output")
        st.markdown(draft.content)

        if dry_run:
            st.info("Dry run mode — draft was not saved to disk.")
        else:
            st.info("Draft saved to outputs/drafts/")

with tab_coming_soon:
    st.info("Campaign Analyst and Lead Scorer dashboards are coming soon.")
