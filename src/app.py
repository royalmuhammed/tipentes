import streamlit as st
import time
import pandas as pd
import base64
import os
from datetime import datetime
from logic_engine import analyze_logic
import graphviz

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="TIPENTES // THREAT INTEL",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. ROBUST IMAGE LOADER ---
def get_logo_base64():
    # Priority list of possible logo filenames
    possible_files = ["src/logo.jpg", "src/logo.png", "src/logo.jpeg", "logo.jpg", "logo.png"]

    for path in possible_files:
        if os.path.exists(path):
            with open(path, "rb") as img_file:
                encoded = base64.b64encode(img_file.read()).decode()
            mime = "image/jpeg" if path.lower().endswith((".jpg", ".jpeg")) else "image/png"
            return f"data:{mime};base64,{encoded}"
    return None

LOGO_B64 = get_logo_base64()

# HTML COMPONENTS
if LOGO_B64:
    # Navbar Logo (Height 60px)
    LOGO_NAV = f'<img src="{LOGO_B64}" style="height:60px; width:auto; margin-right:20px; vertical-align:middle; border-radius:8px;">'
    # Login Logo (Width 160px)
    LOGO_LOGIN = f'<img src="{LOGO_B64}" style="width:160px; height:auto; border-radius:16px; box-shadow:0 10px 30px rgba(0,0,0,0.5); border:3px solid #2d303e;">'
else:
    # Fallback if file not found
    LOGO_NAV = "<span style='font-size:3rem; margin-right:10px;'>🛡️</span>"
    LOGO_LOGIN = "<div style='font-size:6rem; text-align:center;'>🛡️</div>"


# --- 3. CSS STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;900&family=JetBrains+Mono:wght@500&display=swap');

    :root {
        --bg-app: #13151a; --bg-panel: #1e2029; --border: #2d303e;
        --accent: #3b82f6; --text-main: #e2e8f0; --term-text: #4ade80;
    }

    .stApp { background-color: var(--bg-app); font-family: 'Inter', sans-serif; color: var(--text-main); }
    #MainMenu, footer, header { display: none !important; }
    .block-container { padding-top: 0 !important; padding-bottom: 0 !important; max-width: 100% !important; }

    /* --- TAB FONT SIZE INCREASE --- */
    button[data-baseweb="tab"] {
        font-size: 1.5rem !important;  /* 24px */
        font-weight: 800 !important;   /* Extra Bold */
        padding: 1rem 2rem !important;
        color: #94a3b8 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #ffffff !important;
        background-color: #1e2029 !important;
        border-bottom: 3px solid #3b82f6 !important;
    }

    /* NAVBAR & BRAND */
    .nav-container { display: flex; align-items: center; padding: 20px 0; }
    .brand-text {
        font-weight: 900; font-size: 3.5rem; letter-spacing: -2px;
        color: #fff; text-transform: uppercase; line-height: 1;
    }

    /* INPUTS */
    input[type="text"], input[type="password"] {
        color: #fff !important; caret-color: #fff !important;
        background-color: #1e2029 !important; border: 1px solid #334155 !important;
    }
    div[data-testid="stForm"] {
        background: var(--bg-panel); padding: 3rem; border-radius: 16px;
        border: 1px solid var(--border); box-shadow: 0 20px 60px rgba(0,0,0,0.6);
    }

    /* UPLOAD ZONES */
    [data-testid='stFileUploader'] {
        background-color: var(--bg-panel); border: 2px dashed var(--border);
        border-radius: 8px; padding: 2rem; text-align: center;
    }
    [data-testid='stFileUploader']:hover { border-color: var(--accent); }

    /* TERMINAL */
    .terminal-panel {
        background: var(--bg-panel); border: 1px solid var(--accent);
        border-radius: 8px; height: 80vh; display: flex; flex-direction: column;
        overflow: hidden; box-shadow: 0 0 25px rgba(59, 130, 246, 0.15);
    }
    .term-body {
        background: #000; flex-grow: 1; padding: 1rem;
        font-family: 'JetBrains Mono', monospace; color: var(--term-text);
        overflow-y: auto;
    }

    /* ALERTS & BUTTONS */
    .alert-banner {
        background: #450a0a; border: 1px solid #ef4444; color: #fca5a5;
        padding: 1rem; border-radius: 6px; font-weight: 600; display: flex; align-items: center; gap: 15px;
    }
    div.stButton > button {
        background: var(--accent); color: white; border: none; padding: 0.8rem;
        font-weight: 700; border-radius: 6px; text-transform: uppercase; width: 100%;
    }
    div.stButton > button:hover { background: #2563eb; box-shadow: 0 5px 15px rgba(59, 130, 246, 0.4); }
</style>
""", unsafe_allow_html=True)

# --- 4. STATE MANAGEMENT ---
if "auth" not in st.session_state: st.session_state["auth"] = False
if "console" not in st.session_state: st.session_state["console"] = [
    "[KERNEL] TIPENTES CORE v4.0 ONLINE...",
    "[KERNEL] SECURITY SHIELD ACTIVE...",
    "> _"
]
if "scan_data" not in st.session_state: st.session_state["scan_data"] = None
if "threat_history" not in st.session_state: st.session_state["threat_history"] = []

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    st.session_state["console"].append(f"[{ts}] {msg}")

def do_logout():
    st.session_state["auth"] = False
    st.session_state["threat_history"] = []
    st.session_state["scan_data"] = None
    st.session_state["console"] = []
    st.rerun()

# --- 5. VIEWS ---

def login_view():
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown(f"""
        <div style="display: flex; justify-content: center; margin-bottom: 25px;">
            {LOGO_LOGIN}
        </div>
        <div style="text-align: center; margin-bottom: 25px;">
            <h1 style="color: #fff; margin: 0; font-size: 3.5rem; font-weight: 900; letter-spacing: -2px;">TIPENTES</h1>
            <p style="color: #94a3b8; letter-spacing: 3px; font-weight: 600;">ENTERPRISE THREAT INTELLIGENCE</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login"):
            st.markdown("<h4 style='text-align:center; color:#3b82f6;'>OPERATOR ACCESS</h4>", unsafe_allow_html=True)
            uid = st.text_input("USER ID")
            pwd = st.text_input("PASSWORD", type="password")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("AUTHENTICATE SESSION"):
                if uid == "judge" and pwd == "gemini2026":
                    st.session_state["auth"] = True
                    log(f"USER {uid.upper()} LOGGED IN.")
                    st.rerun()
                else:
                    st.error("INVALID CREDENTIALS")

def dashboard_view():
    with st.container():
        # Header Layout
        c1, c2 = st.columns([5, 1])
        with c1:
            st.markdown(f"""
            <div class="nav-container">
                {LOGO_NAV}
                <span class="brand-text">TIPENTES</span>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            with st.expander("👤 ADMIN_JUDGE", expanded=False):
                if st.button("🔴 LOGOUT"):
                    do_logout()

    st.markdown("<hr style='border-color: #2d303e; margin-top:0; margin-bottom: 20px;'>", unsafe_allow_html=True)

    # TABS
    tab_dash, tab_threats = st.tabs(["DASHBOARD", "THREAT HISTORY (SESSION)"])

    with tab_dash:
        c_work, c_term = st.columns([2, 1.2])

        # TERMINAL (Right)
        with c_term:
            lines = "<br>".join([f"{l}" for l in st.session_state["console"][-25:]])
            st.markdown(f"""
            <div class="terminal-panel">
                <div style="background:#18181b; padding:10px; border-bottom:1px solid #2d303e; font-size:0.8rem; font-weight:bold; color:#94a3b8; display:flex; justify-content:space-between;">
                    <span>LIVE KERNEL OUTPUT</span>
                    <span>● ● ●</span>
                </div>
                <div class="term-body" id="term_scroll">
                    {lines}
                </div>
            </div>
            <script>document.getElementById("term_scroll").scrollTop = document.getElementById("term_scroll").scrollHeight;</script>
            """, unsafe_allow_html=True)

        # WORKSPACE (Left)
        with c_work:
            if st.session_state["scan_data"] is None:
                st.markdown("### 📤 INGESTION PORTAL")
                v_file = st.file_uploader("Upload Session Video (MP4)", type=["mp4", "mov"])
                h_file = st.file_uploader("Upload Network Telemetry (HAR)", type=["har", "json"])

                if st.button("INITIATE ANALYSIS PROTOCOL"):
                    if v_file and h_file:
                        log("PROTOCOL INITIATED.")
                        log(f"> Mounting: {v_file.name}")
                        log(f"> Parsing: {h_file.name}")
                        time.sleep(1)
                        log("> Correlating vectors...")

                        # Process
                        with open("temp.mp4", "wb") as f: f.write(v_file.getbuffer())
                        har_data = h_file.getvalue().decode("utf-8")
                        result = analyze_logic("temp.mp4", har_data)

                        st.session_state["scan_data"] = result
                        st.session_state["threat_history"].append({
                            "timestamp": datetime.now().strftime("%H:%M:%S"),
                            "type": result.get("vulnerability_type"),
                            "severity": "CRITICAL" if result.get("vulnerability_found") else "SAFE"
                        })
                        log("> THREAT DETECTED.")
                        st.rerun()
            else:
                # Results
                res = st.session_state["scan_data"]
                if st.button("← NEW SCAN"):
                    st.session_state["scan_data"] = None
                    st.rerun()

                if res.get("vulnerability_found"):
                    st.markdown(f"""
                    <div class="alert-banner">
                        <span style="font-size: 2rem;">🚨</span>
                        <div>
                            <div style="font-size:0.9rem; color:#fca5a5;">DETECTED VULNERABILITY</div>
                            <div style="font-size:1.5rem; color:#fff;">{res.get('vulnerability_type').upper()}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                t1, t2, t3 = st.tabs(["INTELLIGENCE", "ATTACK FLOW", "EXPLOIT"])
                with t1:
                    st.info(res.get('analysis_summary'))
                    st.write("**EVIDENCE:**", res.get('evidence'))
                with t2:
                    st.markdown("#### VISUAL ATTACK PATH")
                    g = graphviz.Digraph()
                    g.attr(bgcolor='transparent')
                    g.attr('node', style='filled', shape='box', fontname='Arial', fontcolor='white')
                    with g.subgraph(name='cluster_0') as c:
                        c.attr(color='#2d303e', label='Normal Flow', fontcolor='white')
                        c.node('A','Login',fillcolor='#22c55e',fontcolor='black')
                        c.node('B','View',fillcolor='#22c55e',fontcolor='black')
                        c.edges([('A','B')])
                    with g.subgraph(name='cluster_1') as c:
                        c.attr(color='#ef4444', label='Attack Flow', fontcolor='red')
                        c.node('X','Intercept',fillcolor='#ef4444')
                        c.node('Y','Exploit',fillcolor='#ef4444')
                        c.edges([('X','Y')])
                    g.edge('B','X', style='dashed', color='white')
                    st.graphviz_chart(g)
                with t3:
                    st.code(res.get("exploit_script"), language="python")

    with tab_threats:
        st.markdown("### 📜 SESSION THREAT REGISTRY")
        if st.session_state["threat_history"]:
            st.dataframe(pd.DataFrame(st.session_state["threat_history"]), use_container_width=True)
        else:
            st.info("No active threats recorded in this session.")

if __name__ == "__main__":
    if st.session_state["auth"]:
        dashboard_view()
    else:
        login_view()
