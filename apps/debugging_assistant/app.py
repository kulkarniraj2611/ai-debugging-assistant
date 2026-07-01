import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import streamlit as st
from utils.llm_client import GroqClient
from utils.debugging_helper import (
    build_debugging_prompt,
    analyze_code_complexity,
    extract_severity,
    extract_fixed_code
)
from datetime import datetime

# ── Page Config ──
st.set_page_config(
    page_title="AI Debugging Assistant",
    page_icon="🔧",
    layout="wide"
)

# ── Custom CSS ──
st.markdown("""
<style>
    .main { background-color: #0d0f14; }
    .stTextArea textarea {
        background-color: #1e2130;
        color: #e8eaf0;
        font-family: 'Courier New', monospace;
        font-size: 14px;
        border: 1px solid #2d3148;
        border-radius: 8px;
    }
    .severity-high {
        background: #ff4b4b22;
        border-left: 4px solid #ff4b4b;
        padding: 10px 16px;
        border-radius: 6px;
        color: #ff4b4b;
        font-weight: 700;
        font-size: 16px;
    }
    .severity-medium {
        background: #ffa50022;
        border-left: 4px solid #ffa500;
        padding: 10px 16px;
        border-radius: 6px;
        color: #ffa500;
        font-weight: 700;
        font-size: 16px;
    }
    .severity-low {
        background: #00cc6622;
        border-left: 4px solid #00cc66;
        padding: 10px 16px;
        border-radius: 6px;
        color: #00cc66;
        font-weight: 700;
        font-size: 16px;
    }
    .metric-box {
        background: #1e2130;
        border: 1px solid #2d3148;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
    }
    .history-item {
        background: #1e2130;
        border: 1px solid #2d3148;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 8px;
    }
    .stButton button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ── Session State ──
if "debug_history" not in st.session_state:
    st.session_state.debug_history = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None


def run_debug(code: str):
    """Run AI debugging and store result."""
    complexity = analyze_code_complexity(code)
    prompt = build_debugging_prompt(code)
    client = GroqClient()
    response = client.ask(prompt)
    severity = extract_severity(response)
    fixed_code = extract_fixed_code(response)

    result = {
        "timestamp": datetime.now().strftime("%d %b %Y, %I:%M %p"),
        "code_snippet": code[:80] + "..." if len(code) > 80 else code,
        "response": response,
        "severity": severity,
        "fixed_code": fixed_code,
        "complexity": complexity
    }

    st.session_state.debug_history.insert(0, result)
    st.session_state.last_result = result
    return result


# ── Header ──
st.markdown("# 🔧 AI Debugging Assistant")
st.markdown("Paste your **Python code** or **error log** and get instant AI-powered debugging help.")
st.markdown("---")

# ── Layout: Two columns ──
col_left, col_right = st.columns([3, 2], gap="large")

with col_left:
    st.markdown("### 📝 Your Code")
    user_input = st.text_area(
        "Enter your code",
        height=280,
        placeholder="# Paste your Python code or error log here\n# Example:\nprint(Hello World)\n\n# Or paste an error:\n# TypeError: unsupported operand type(s) for +: 'int' and 'str'",
    )

    # Quick complexity preview
    if user_input.strip():
        complexity_preview = analyze_code_complexity(user_input)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Lines", complexity_preview["line_count"])
        c2.metric("Functions", complexity_preview["functions"])
        c3.metric("Loops", complexity_preview["loops"])
        c4.metric("Classes", complexity_preview["classes"])

        if not complexity_preview["syntax_ok"]:
            st.error(f"⚠️ Syntax Error detected: {complexity_preview['syntax_error']}")

    btn_col1, btn_col2 = st.columns([3, 1])
    with btn_col1:
        debug_btn = st.button("🔎 Debug My Code", type="primary", use_container_width=True)
    with btn_col2:
        clear_btn = st.button("🗑️ Clear", use_container_width=True)

    if clear_btn:
        st.rerun()

    if debug_btn:
        if not user_input.strip():
            st.warning("⚠️ Please paste some Python code or error log first!")
        else:
            with st.spinner("🤖 Analyzing your code..."):
                try:
                    result = run_debug(user_input)
                    st.success("✅ Analysis complete!")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# ── Right Column: Results ──
with col_right:
    st.markdown("### 📊 Code Analysis")

    if st.session_state.last_result:
        result = st.session_state.last_result
        complexity = result["complexity"]

        # Severity badge
        severity = result["severity"]
        if severity == "HIGH":
            st.markdown('<div class="severity-high">🔴 Severity: HIGH — Critical Error</div>', unsafe_allow_html=True)
        elif severity == "MEDIUM":
            st.markdown('<div class="severity-medium">🟡 Severity: MEDIUM — Logic Issue</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="severity-low">🟢 Severity: LOW — Minor Issue</div>', unsafe_allow_html=True)

        st.markdown("")

        # Complexity
        st.markdown(f"**Complexity:** {complexity['complexity']} ({complexity['line_count']} lines)")

        st.markdown("---")
        st.markdown("### 🧠 AI Debug Report")
        st.markdown(result["response"])

        # Fixed code section
        if result["fixed_code"]:
            st.markdown("---")
            st.markdown("### ✅ Fixed Code")
            st.code(result["fixed_code"], language="python")
            st.download_button(
                label="⬇️ Download Fixed Code",
                data=result["fixed_code"],
                file_name="fixed_code.py",
                mime="text/plain",
                use_container_width=True
            )
    else:
        st.info("👈 Paste your code on the left and click **Debug My Code** to get started!")
        st.markdown("""
        **What this tool does:**
        - 🔍 Identifies bugs and errors in your Python code
        - 📊 Rates error severity (Low / Medium / High)
        - 🛠️ Provides fixed code automatically
        - 📈 Analyzes code complexity
        - 📜 Keeps history of all your debug sessions
        """)

# ── Debug History ──
st.markdown("---")
st.markdown("### 📜 Debug History")

if not st.session_state.debug_history:
    st.info("No debug history yet. Start debugging to see your history here!")
else:
    st.markdown(f"**{len(st.session_state.debug_history)} session(s)** this run")

    for i, item in enumerate(st.session_state.debug_history):
        severity_emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(item["severity"], "⚪")

        with st.expander(f"{severity_emoji} [{item['timestamp']}] — {item['code_snippet']}"):
            st.markdown(f"**Severity:** {item['severity']} | **Complexity:** {item['complexity']['complexity']}")
            st.markdown("**AI Response:**")
            st.markdown(item["response"])
            if item["fixed_code"]:
                st.code(item["fixed_code"], language="python")

    if st.button("🗑️ Clear History"):
        st.session_state.debug_history = []
        st.session_state.last_result = None
        st.rerun()
