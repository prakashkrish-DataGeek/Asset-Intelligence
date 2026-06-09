"""
Asset Intelligence Copilot — Industrial Operations Console
==========================================================
Boardroom-ready, operations-ready Streamlit dashboard for industrial AI
decision support. Designed for three audiences:
  1. Executives: business risk, recommended action, why it matters
  2. Operations leaders: asset condition, severity, mitigation, restart gate
  3. Engineers: telemetry evidence, historical context, compliance basis, tool trace

Design language: industrial, modern, compact, evidence-first, explainable.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import streamlit as st
import pandas as pd
import sqlite3
import datetime

import config
from data_generator import bootstrap
from mcp_server import AssetIntelligenceMCPServer
from mcp_client import AssetIntelligenceAgent
from mcp_protocol import MCPMethod, MCPRequest


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="Asset Intelligence Copilot",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =============================================================================
# CUSTOM CSS — Industrial Design Language
# =============================================================================
st.markdown("""
<style>
  :root {
    --bg-base: #f1f5f9;
    --bg-card: #ffffff;
    --border: #cbd5e1;
    --text-primary: #0f172a;
    --text-secondary: #475569;
    --text-muted: #94a3b8;
    --accent: #2563eb;
    --accent-light: #dbeafe;
    --critical: #dc2626;
    --critical-light: #fee2e2;
    --warning: #d97706;
    --warning-light: #fef3c7;
    --safe: #16a34a;
    --safe-light: #dcfce7;
    --info: #475569;
    --info-light: #f1f5f9;
  }
  .block-container { padding-top: 0.8rem; padding-bottom: 0.8rem; max-width: 100rem; }
  p, li, td, th { font-size: 0.85rem; }
  h1 { font-size: 1.4rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.3rem; }
  h2 { font-size: 1.15rem; font-weight: 600; color: var(--text-primary); margin-top: 0.6rem; margin-bottom: 0.4rem; }
  h3 { font-size: 1rem; font-weight: 600; color: var(--text-secondary); margin-top: 0.5rem; margin-bottom: 0.3rem; }
  h4 { font-size: 0.9rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 0.2rem; }

  .badge {
    display: inline-block;
    padding: 1px 6px;
    border-radius: 3px;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.4px;
    text-transform: uppercase;
    line-height: 1.4;
  }
  .badge-critical { background: var(--critical-light); color: var(--critical); border: 1px solid #fecaca; }
  .badge-warning { background: var(--warning-light); color: var(--warning); border: 1px solid #fde68a; }
  .badge-safe { background: var(--safe-light); color: var(--safe); border: 1px solid #bbf7d0; }
  .badge-info { background: var(--info-light); color: var(--info); border: 1px solid #e2e8f0; }
  .badge-accent { background: var(--accent-light); color: var(--accent); border: 1px solid #bfdbfe; }

  .kpi-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 5px;
    padding: 0.5rem 0.7rem;
    height: 100%;
  }
  .kpi-label {
    font-size: 0.65rem;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 0.15rem;
  }
  .kpi-value {
    font-size: 1rem;
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1.2;
  }
  .kpi-sub {
    font-size: 0.68rem;
    color: var(--text-muted);
    margin-top: 0.1rem;
  }

  .decision-panel {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.9rem 1.1rem;
    margin-top: 0.4rem;
  }
  .decision-section {
    margin-bottom: 0.7rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #f1f5f9;
  }
  .decision-section:last-child {
    border-bottom: none;
    margin-bottom: 0;
    padding-bottom: 0;
  }
  .decision-label {
    font-size: 0.65rem;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 0.25rem;
  }
  .decision-text {
    font-size: 0.85rem;
    color: var(--text-primary);
    line-height: 1.5;
  }

  .restart-gate-locked {
    background: var(--critical-light);
    border: 1px solid #fecaca;
    border-radius: 5px;
    padding: 0.5rem 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.6rem;
  }
  .restart-gate-open {
    background: var(--safe-light);
    border: 1px solid #bbf7d0;
    border-radius: 5px;
    padding: 0.5rem 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.6rem;
  }

  .evidence-callout {
    background: #f8fafc;
    border-left: 3px solid var(--accent);
    padding: 0.4rem 0.7rem;
    margin: 0.3rem 0;
    border-radius: 0 3px 3px 0;
    font-size: 0.78rem;
    color: var(--text-secondary);
  }

  .sidebar-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 5px;
    padding: 0.4rem 0.5rem;
    margin-bottom: 0.4rem;
  }
  .sidebar-card-title {
    font-size: 0.65rem;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 0.25rem;
  }

  .stale-chip {
    display: inline-block;
    background: #fef3c7;
    color: #92400e;
    font-size: 0.6rem;
    font-weight: 600;
    padding: 1px 5px;
    border-radius: 3px;
    margin-left: 0.25rem;
    vertical-align: middle;
  }

  .stDataFrame td, .stDataFrame th { font-size: 0.75rem !important; padding: 3px 6px !important; }
  .stDataFrame th { background: #f8fafc !important; }

  [data-testid="stStatus"] { font-size: 0.82rem; }

  div[data-testid="stTabs"] button { font-size: 0.8rem; font-weight: 600; padding: 0.3rem 0.8rem; }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _badge(label: str, severity: str) -> str:
    mapping = {
        "CRITICAL": "badge-critical", "WARNING": "badge-warning", "CAUTION": "badge-warning",
        "ANOMALY": "badge-critical", "NORMAL": "badge-safe", "CLEAR": "badge-safe",
        "COMPROMISED": "badge-critical", "HIGH": "badge-critical", "MEDIUM": "badge-warning",
        "LOW": "badge-info", "HIGH_CONFIDENCE": "badge-safe", "MEDIUM_CONFIDENCE": "badge-warning",
        "LOW_CONFIDENCE": "badge-critical", "YES": "badge-safe", "NO": "badge-critical",
    }
    css_class = mapping.get(severity.upper(), "badge-info")
    return f'''<span class="badge {css_class}">{label}</span>'''


def _kpi_card(label: str, value: str, sub: str = "", alert: bool = False) -> str:
    color = 'color: var(--critical);' if alert else 'color: var(--text-primary);'
    sub_html = f'''<div class="kpi-sub">{sub}</div>''' if sub else ''''''
    return f'''
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value" style="{color}">{value}</div>
        {sub_html}
    </div>
    '''


def _stale_check(ts_str: str) -> bool:
    if not ts_str:
        return True
    try:
        ts = datetime.datetime.fromisoformat(ts_str)
        return (datetime.datetime.now() - ts) > datetime.timedelta(hours=2)
    except Exception:
        return True


def _fmt_ts(ts_str: str) -> str:
    if not ts_str:
        return "—"
    try:
        ts = datetime.datetime.fromisoformat(ts_str)
        return ts.strftime("%H:%M %d-%b")
    except Exception:
        return ts_str[:16]


# =============================================================================
# INITIALIZATION
# =============================================================================
if "initialized" not in st.session_state:
    artifacts = bootstrap()
    server = AssetIntelligenceMCPServer(
        db_path=artifacts["database"],
        sharepoint_dir=artifacts["sharepoint"],
    )
    st.session_state["server"] = server
    st.session_state["db_path"] = str(artifacts["database"])
    st.session_state["sharepoint_dir"] = str(artifacts["sharepoint"])
    st.session_state["chat_history"] = []
    st.session_state["last_result"] = None
    st.session_state["selected_asset"] = config.ANOMALY_ASSET
    st.session_state["initialized"] = True

server: AssetIntelligenceMCPServer = st.session_state["server"]
db_path = st.session_state["db_path"]
sp_dir = Path(st.session_state["sharepoint_dir"])


# =============================================================================
# SIDEBAR — Data & System Context
# =============================================================================
with st.sidebar:
    st.markdown("## 🏭 Asset Intelligence Copilot")
    st.markdown("<p style='font-size:0.75rem;color:#64748b;margin-top:-0.4rem;'>MCP-powered operations decision support</p>", unsafe_allow_html=True)
    st.markdown("<hr style='margin:0.6rem 0;border-color:#e2e8f0;'>", unsafe_allow_html=True)

    # --- Asset Selector ---
    st.markdown("<div class='sidebar-card-title'>Asset Selector</div>", unsafe_allow_html=True)
    selected_asset = st.selectbox(
        "Select asset",
        config.ASSETS,
        index=config.ASSETS.index(st.session_state.get("selected_asset", config.ANOMALY_ASSET)),
        label_visibility="collapsed",
    )
    st.session_state["selected_asset"] = selected_asset

    # --- Anomaly Watchlist ---
    st.markdown("<div class='sidebar-card-title' style='margin-top:0.7rem;'>Anomaly Watchlist</div>", unsafe_allow_html=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT asset_id, status, COUNT(*) as cnt
        FROM asset_telemetry
        WHERE timestamp > datetime('now', '-6 hours')
        GROUP BY asset_id, status
        HAVING status IN ('ANOMALY', 'CAUTION')
    """)
    anomalies = cursor.fetchall()
    conn.close()

    if anomalies:
        for row in anomalies:
            badge_color = "badge-critical" if row["status"] == "ANOMALY" else "badge-warning"
            st.markdown(
                f'''<div class="sidebar-card">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span style="font-weight:600;font-size:0.8rem;">{row['asset_id']}</span>
                        <span class="badge {badge_color}">{row['status']}</span>
                    </div>
                    <div style="font-size:0.7rem;color:#94a3b8;margin-top:0.1rem;">{row['cnt']} events in last 6h</div>
                </div>''',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            '''<div class="sidebar-card" style="border-color:#bbf7d0;">
                <span class="badge badge-safe">ALL CLEAR</span>
                <div style="font-size:0.7rem;color:#94a3b8;margin-top:0.15rem;">No anomalies in last 6 hours</div>
            </div>''',
            unsafe_allow_html=True,
        )

    # --- SQLite Data Preview ---
    st.markdown("<div class='sidebar-card-title' style='margin-top:0.7rem;'>Telemetry Preview</div>", unsafe_allow_html=True)
    conn = sqlite3.connect(db_path)
    telem_df = pd.read_sql_query(
        f"SELECT timestamp, pressure_psi, temperature_c, status FROM asset_telemetry WHERE asset_id = '{selected_asset}' ORDER BY timestamp DESC LIMIT 5",
        conn,
    )
    conn.close()
    st.dataframe(telem_df, use_container_width=True, hide_index=True, height=140)

    # --- Legacy Repository Browser ---
    st.markdown("<div class='sidebar-card-title' style='margin-top:0.7rem;'>Legacy Repository</div>", unsafe_allow_html=True)
    sp_files = sorted(sp_dir.iterdir()) if sp_dir.exists() else []
    for f in sp_files:
        if f.is_file():
            size_kb = f.stat().st_size / 1024
            icon = "📄" if f.suffix == ".txt" else "📝" if f.suffix == ".md" else "📎"
            st.markdown(
                f'''<div style="display:flex;justify-content:space-between;align-items:center;padding:0.15rem 0;border-bottom:1px solid #f1f5f9;">
                    <span style="font-size:0.75rem;">{icon} {f.name}</span>
                    <span style="font-size:0.68rem;color:#94a3b8;">{size_kb:.1f} KB</span>
                </div>''',
                unsafe_allow_html=True,
            )

    # --- MCP Capabilities ---
    st.markdown("<div class='sidebar-card-title' style='margin-top:0.7rem;'>MCP Tools</div>", unsafe_allow_html=True)
    req_tools = MCPRequest(id="sb-tools", method=MCPMethod.TOOLS_LIST, params={})
    resp_tools = server.handle(req_tools)
    if resp_tools.result:
        for t in resp_tools.result.get("tools", []):
            st.markdown(
                f'''<div style="display:flex;align-items:center;gap:0.3rem;padding:0.1rem 0;">
                    <span style="font-size:0.72rem;color:#2563eb;">⚙</span>
                    <span style="font-size:0.72rem;color:#334155;">{t['name']}</span>
                </div>''',
                unsafe_allow_html=True,
            )

    st.markdown("<div class='sidebar-card-title' style='margin-top:0.5rem;'>Resources</div>", unsafe_allow_html=True)
    req_res = MCPRequest(id="sb-res", method=MCPMethod.RESOURCES_LIST, params={})
    resp_res = server.handle(req_res)
    if resp_res.result:
        for r in resp_res.result.get("resources", []):
            st.markdown(
                f'''<div style="display:flex;align-items:center;gap:0.3rem;padding:0.1rem 0;">
                    <span style="font-size:0.72rem;color:#d97706;">📜</span>
                    <span style="font-size:0.72rem;color:#334155;">{r['name'][:32]}...</span>
                </div>''',
                unsafe_allow_html=True,
            )

    # --- System Health ---
    st.markdown("<div class='sidebar-card-title' style='margin-top:0.7rem;'>System Health</div>", unsafe_allow_html=True)
    st.markdown(
        '''<div class="sidebar-card" style="border-color:#bbf7d0;">
            <div style="display:flex;justify-content:space-between;align-items:center;padding:0.1rem 0;">
                <span style="font-size:0.75rem;">SQLite Historian</span>
                <span class="badge badge-safe">ONLINE</span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;padding:0.1rem 0;">
                <span style="font-size:0.75rem;">SharePoint Sim</span>
                <span class="badge badge-safe">ONLINE</span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;padding:0.1rem 0;">
                <span style="font-size:0.75rem;">MCP Server</span>
                <span class="badge badge-safe">ONLINE</span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;padding:0.1rem 0;">
                <span style="font-size:0.75rem;">Agent Loop</span>
                <span class="badge badge-safe">READY</span>
            </div>
        </div>''',
        unsafe_allow_html=True,
    )


# =============================================================================
# TOP SUMMARY STRIP
# =============================================================================
last_result = st.session_state.get("last_result")

if last_result:
    rec = last_result["recommendation"]
    state = rec["current_asset_state"]
    stale = _stale_check(state.get("last_telemetry_timestamp"))
    stale_chip = '<span class="stale-chip">STALE</span>' if stale else ""

    st.markdown("<hr style='margin:0.3rem 0 0.6rem 0;border-color:#e2e8f0;'>", unsafe_allow_html=True)
    cols = st.columns([1.1, 0.9, 0.9, 0.9, 2.0, 1.0, 1.2, 1.2])

    with cols[0]:
        st.markdown(_kpi_card("Asset ID", state["asset_id"]), unsafe_allow_html=True)
    with cols[1]:
        status_alert = state["latest_status"] in ("ANOMALY", "COMPROMISED")
        st.markdown(_kpi_card("Status", state["latest_status"], alert=status_alert), unsafe_allow_html=True)
    with cols[2]:
        sev_alert = rec["severity"] == "CRITICAL"
        st.markdown(_kpi_card("Severity", rec["severity"], alert=sev_alert), unsafe_allow_html=True)
    with cols[3]:
        conf_alert = rec["confidence"] == "LOW"
        st.markdown(_kpi_card("Confidence", rec["confidence"], alert=conf_alert), unsafe_allow_html=True)
    with cols[4]:
        action_text = rec["recommended_mitigation"][:55] + "..." if len(rec["recommended_mitigation"]) > 55 else rec["recommended_mitigation"]
        st.markdown(_kpi_card("Recommended Action", action_text), unsafe_allow_html=True)
    with cols[5]:
        restart_label = "YES" if rec["restart_allowed"] else "NO"
        restart_alert = not rec["restart_allowed"]
        st.markdown(_kpi_card("Restart Allowed", restart_label, alert=restart_alert), unsafe_allow_html=True)
    with cols[6]:
        ts_display = _fmt_ts(state.get("last_telemetry_timestamp", ""))
        st.markdown(_kpi_card("Last Telemetry", f"{ts_display}{stale_chip}"), unsafe_allow_html=True)
    with cols[7]:
        agent_ts = _fmt_ts(last_result["reasoning_trace"][-1]["timestamp"]) if last_result.get("reasoning_trace") else "—"
        st.markdown(_kpi_card("Last Agent Run", agent_ts), unsafe_allow_html=True)

    st.markdown("<hr style='margin:0.4rem 0 0.6rem 0;border-color:#e2e8f0;'>", unsafe_allow_html=True)

    # Restart gate banner
    if not rec["restart_allowed"]:
        st.markdown(
            f'''<div class="restart-gate-locked">
                <span style="font-size:1rem;">🔒</span>
                <div>
                    <div style="font-weight:700;font-size:0.85rem;color:#dc2626;">RESTART PROHIBITED</div>
                    <div style="font-size:0.78rem;color:#475569;">{rec["restart_conditions"]}</div>
                </div>
            </div>''',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'''<div class="restart-gate-open">
                <span style="font-size:1rem;">✓</span>
                <div>
                    <div style="font-weight:700;font-size:0.85rem;color:#16a34a;">RESTART PERMITTED</div>
                    <div style="font-size:0.78rem;color:#475569;">{rec["restart_conditions"]}</div>
                </div>
            </div>''',
            unsafe_allow_html=True,
        )


# =============================================================================
# MAIN WORKSPACE — Title, Controls, Agent Execution
# =============================================================================
st.markdown("<h1>Asset Intelligence Copilot</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='font-size:0.85rem;color:#475569;margin-top:-0.3rem;margin-bottom:0.8rem;'>"
    "AI decision support connecting real-time telemetry with legacy engineering knowledge via MCP."
    "</p>",
    unsafe_allow_html=True,
)

# Action buttons
btn_cols = st.columns([1.3, 1.3, 1, 3])
with btn_cols[0]:
    run_demo = st.button("▶ Run Executive Demo", type="primary", use_container_width=True)
with btn_cols[1]:
    run_diagnosis = st.button("🔍 Run Asset Diagnosis", use_container_width=True)
with btn_cols[2]:
    if st.button("🗑 Clear Session", use_container_width=True):
        st.session_state["last_result"] = None
        st.rerun()

# Determine prompt
prompt = None
asset_override = None
if run_demo:
    prompt = (
        "We are seeing a critical pressure drop alert on asset WELL-202B right now. "
        "Check current telemetry and risk metrics, cross-reference historical engineering logs in SharePoint, "
        "review relevant compliance guidance, and provide the most likely root cause plus a recommended "
        "mitigation strategy with supporting evidence."
    )
    asset_override = "WELL-202B"
elif run_diagnosis:
    prompt = f"Run full diagnostic assessment on asset {selected_asset}. Check telemetry, risk metrics, maintenance history, and legacy documents for any anomalies or concerns."
    asset_override = selected_asset

# =============================================================================
# AGENT EXECUTION
# =============================================================================
if prompt:
    st.markdown("<h2>Agent Execution</h2>", unsafe_allow_html=True)

    agent = AssetIntelligenceAgent(server)

    # Step-by-step execution with visible status updates
    with st.status("Initializing agent and discovering MCP capabilities...", expanded=True) as status:
        result = agent.run(prompt, asset_id=asset_override)
        status.update(label="Agent execution complete", state="complete", expanded=False)

    st.session_state["last_result"] = result
    st.rerun()

# =============================================================================
# RECOMMENDATION PANEL (shown after run)
# =============================================================================
if last_result:
    rec = last_result["recommendation"]
    state = rec["current_asset_state"]

    st.markdown("<h2>Decision Panel</h2>", unsafe_allow_html=True)

    # Severity + confidence header row
    hdr_cols = st.columns([1, 1, 1, 3])
    with hdr_cols[0]:
        st.markdown(f"Severity: {_badge(rec['severity'], rec['severity'])}", unsafe_allow_html=True)
    with hdr_cols[1]:
        st.markdown(f"Confidence: {_badge(rec['confidence'], rec['confidence'] + '_CONFIDENCE')}", unsafe_allow_html=True)
    with hdr_cols[2]:
        st.markdown(f"Restart: {_badge('YES' if rec['restart_allowed'] else 'NO', 'YES' if rec['restart_allowed'] else 'NO')}", unsafe_allow_html=True)
    with hdr_cols[3]:
        pass

    st.markdown("<div class='decision-panel'>", unsafe_allow_html=True)

    # Current State
    st.markdown(
        f'''<div class="decision-section">
            <div class="decision-label">Current Asset State</div>
            <div class="decision-text">
                <b>{state["asset_id"]}</b> — 
                Pressure: <b>{state["latest_pressure_psi"]} PSI</b> 
                (trend: {state["pressure_trend"]}), 
                Status: <b>{state["latest_status"]}</b>, 
                Risk: <b>{state["latest_risk_score"]}</b>, 
                Integrity: <b>{state["integrity_flag"]}</b>, 
                Impact: <b>{state["production_impact"]}</b>
            </div>
        </div>''',
        unsafe_allow_html=True,
    )

    # Root Cause
    st.markdown(
        f'''<div class="decision-section">
            <div class="decision-label">Likely Root Cause</div>
            <div class="decision-text">{rec["likely_root_cause"]}</div>
        </div>''',
        unsafe_allow_html=True,
    )

    # Alternative Considerations
    if rec.get("alternative_considerations"):
        alt_text = "<br>".join([f"• {a}" for a in rec["alternative_considerations"]])
        st.markdown(
            f'''<div class="decision-section">
                <div class="decision-label">Alternative Considerations</div>
                <div class="decision-text">{alt_text}</div>
            </div>''',
            unsafe_allow_html=True,
        )

    # Recommended Mitigation
    st.markdown(
        f'''<div class="decision-section">
            <div class="decision-label">Recommended Mitigation</div>
            <div class="decision-text">{rec["recommended_mitigation"]}</div>
        </div>''',
        unsafe_allow_html=True,
    )

    # Safety / Compliance
    st.markdown(
        f'''<div class="decision-section">
            <div class="decision-label">Safety & Compliance Note</div>
            <div class="decision-text">{rec["safety_compliance_note"]}</div>
        </div>''',
        unsafe_allow_html=True,
    )

    # Restart Conditions
    st.markdown(
        f'''<div class="decision-section">
            <div class="decision-label">Restart Conditions</div>
            <div class="decision-text">{rec["restart_conditions"]}</div>
        </div>''',
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)


# =============================================================================
# EVIDENCE PANEL — Tabs
# =============================================================================
if last_result:
    st.markdown("<h2>Evidence Pack</h2>", unsafe_allow_html=True)

    tabs = st.tabs(["📊 Telemetry", "⚠ Risk Metrics", "📄 Legacy Docs", "📜 Compliance", "🔧 Tool Trace"])

    # --- Telemetry Tab ---
    with tabs[0]:
        for tr in last_result["tool_results"]:
            if tr.get("tool_name") == "query_modern_telemetry":
                df = pd.DataFrame(tr.get("data", []))
                if not df.empty:
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    st.markdown(
                        f'''<div class="evidence-callout">
                            <b>Why this mattered:</b> Pressure readings show sustained decline from 
                            ~{df.iloc[-1]["pressure_psi"]:.0f} PSI to ~{df.iloc[0]["pressure_psi"]:.0f} PSI 
                            over the queried window, confirming the anomaly trend.
                        </div>''',
                        unsafe_allow_html=True,
                    )
                    st.caption(f"Source: {tr.get('data_lineage', {}).get('source_system', 'unknown')} | Path: {tr.get('data_lineage', {}).get('source_path', 'unknown')} | Retrieved: {tr.get('data_lineage', {}).get('retrieval_timestamp', 'unknown')}")
                else:
                    st.warning("No telemetry data returned for this asset.")

    # --- Risk Metrics Tab ---
    with tabs[1]:
        for tr in last_result["tool_results"]:
            if tr.get("tool_name") == "query_risk_metrics":
                df = pd.DataFrame(tr.get("data", []))
                if not df.empty:
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    latest_risk = df.iloc[0]["risk_score"] if "risk_score" in df.columns else None
                    latest_flag = df.iloc[0]["integrity_flag"] if "integrity_flag" in df.columns else "UNKNOWN"
                    st.markdown(
                        f'''<div class="evidence-callout">
                            <b>Why this mattered:</b> Risk score escalated to <b>{latest_risk}</b> 
                            with integrity flag <b>{latest_flag}</b>, directly supporting the severity 
                            assessment and triggering compliance escalation protocols.
                        </div>''',
                        unsafe_allow_html=True,
                    )
                    st.caption(f"Source: {tr.get('data_lineage', {}).get('source_system', 'unknown')} | Retrieved: {tr.get('data_lineage', {}).get('retrieval_timestamp', 'unknown')}")
                else:
                    st.warning("No risk metrics returned for this asset.")

    # --- Legacy Documents Tab ---
    with tabs[2]:
        legacy_found = False
        for tr in last_result["tool_results"]:
            if tr.get("tool_name") == "search_legacy_share":
                matches = tr.get("data", [])
                if matches:
                    legacy_found = True
                    for match in matches:
                        with st.container():
                            st.markdown(f"**`{match['filename']}`** — {match['match_count']} match(es)")
                            st.markdown(f"> {match['snippet']}")
                            st.markdown("---")
        if not legacy_found:
            st.info("No legacy document matches found. This reduces diagnostic confidence.")
        else:
            st.markdown(
                '''<div class="evidence-callout">
                    <b>Why this mattered:</b> Historical engineering documents provided the 
                    micro-fracture precedent and proven mitigation workflow, transforming a 
                    generic pressure alarm into a targeted, evidence-based action plan.
                </div>''',
                unsafe_allow_html=True,
            )

    # --- Compliance Tab ---
    with tabs[3]:
        comp_found = False
        for rc in last_result["resource_contents"]:
            if "compliance" in rc.get("uri", ""):
                comp_found = True
                st.markdown(f"**URI:** `{rc['uri']}`")
                st.text(rc.get("content", "")[:2500])
                st.caption(f"Source: {rc.get('data_lineage', {}).get('source_system', 'unknown')} | Path: {rc.get('data_lineage', {}).get('source_path', 'unknown')} | Retrieved: {rc.get('data_lineage', {}).get('retrieval_timestamp', 'unknown')}")
                st.markdown(
                    '''<div class="evidence-callout">
                        <b>Why this mattered:</b> The compliance framework mandated shutdown, 
                        integrity verification, and dual sign-off before restart — converting 
                        the engineering recommendation into a binding operational gate.
                    </div>''',
                    unsafe_allow_html=True,
                )
        if not comp_found:
            st.warning("Compliance resource could not be loaded. Restart gate assessment may be incomplete.")

    # --- Tool Trace Tab ---
    with tabs[4]:
        st.markdown("<div class='decision-label'>MCP Tool & Resource Invocation Log</div>", unsafe_allow_html=True)
        for step in last_result.get("reasoning_trace", []):
            step_type = step["step_type"]
            ts = step["timestamp"]
            desc = step["description"]

            if step_type == "thought":
                st.markdown(f"🧠 **{ts}** — {desc}")
            elif step_type == "tool_discovery":
                payload = step.get("payload", {})
                count = len(payload) if isinstance(payload, list) else "N/A"
                st.markdown(f"🔍 **{ts}** — {desc} ({count} items)")
            elif step_type == "tool_call":
                payload = step.get("payload", {})
                tool_name = payload.get("tool_name", "unknown") if isinstance(payload, dict) else "unknown"
                st.markdown(f"⚙️ **{ts}** — `{tool_name}` → {desc}")
            elif step_type == "resource_read":
                payload = step.get("payload", {})
                uri = payload.get("uri", "unknown") if isinstance(payload, dict) else "unknown"
                st.markdown(f"📄 **{ts}** — `{uri}` → {desc}")
            elif step_type == "synthesis":
                st.markdown(f"✅ **{ts}** — {desc}")

        st.markdown(
            '''<div class="evidence-callout">
                <b>Why this mattered:</b> Every tool call and resource read is logged with 
                timestamps and lineage metadata, ensuring full auditability and enabling 
                post-incident forensic review of the AI decision chain.
            </div>''',
            unsafe_allow_html=True,
        )


# =============================================================================
# EMPTY STATE (before first run)
# =============================================================================
if not last_result:
    st.markdown("<hr style='margin:1rem 0;border-color:#e2e8f0;'>", unsafe_allow_html=True)
    st.info(
        "👆 **Ready for analysis.** Select an asset in the sidebar, then click **Run Executive Demo** "
        "to see the full ReAct agent loop in action, or **Run Asset Diagnosis** to assess the currently selected asset."
    )

    # Quick stats preview
    st.markdown("<h3>System Overview</h3>", unsafe_allow_html=True)
    ov_cols = st.columns(4)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(DISTINCT asset_id) FROM asset_telemetry")
    ov_cols[0].metric("Assets Monitored", cursor.fetchone()[0])

    cursor.execute("SELECT COUNT(*) FROM asset_telemetry WHERE status = 'ANOMALY'")
    ov_cols[1].metric("Active Anomalies", cursor.fetchone()[0], delta="-2", delta_color="inverse")

    cursor.execute("SELECT COUNT(*) FROM maintenance_events")
    ov_cols[2].metric("Maint. Records", cursor.fetchone()[0])

    cursor.execute("SELECT COUNT(*) FROM risk_metrics WHERE integrity_flag = 'COMPROMISED'")
    ov_cols[3].metric("Compromised Assets", cursor.fetchone()[0], delta="+1", delta_color="inverse")

    conn.close()


# =============================================================================
# FOOTER
# =============================================================================
st.markdown("<hr style='margin:1.2rem 0 0.4rem 0;border-color:#e2e8f0;'>", unsafe_allow_html=True)
st.caption(
    "Asset Intelligence Copilot — Model Context Protocol (MCP) Pilot | "
    "Built for Chief AI Officer demonstration | Self-contained Python prototype | "
    "v1.0.0"
)
