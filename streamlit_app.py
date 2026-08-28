"""Streamlit Community Cloud Application for PROMPT WARS (Project Rosetta).
Evidence-Grounded Multi-Agent Hiring Intelligence.
Source of Truth: Local Application UI (http://127.0.0.1:8000).
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import streamlit as st

# Ensure repository root is on sys.path
_REPO_ROOT = Path(__file__).resolve().parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# Safe environment configuration from Streamlit secrets
try:
    if "GEMINI_API_KEY" in st.secrets:
        os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
    elif "GOOGLE_API_KEY" in st.secrets:
        os.environ["GEMINI_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
except Exception:
    pass

from src.config import settings
from src.workspace import RunWorkspace
from src.builder import build_candidate_rosetta
from src.agents.sealed_memos import generate_sealed_memos, PERSONAS
from src.debate.orchestrator import run_debate_session
from src.decision.engine import synthesize_candidate_decision
from src.decision.reporter import generate_candidate_report_artifacts
from src.api.services.evaluation_service import list_all_evaluations, save_status, load_status


# --- DEFENSIVE DATA NORMALIZATION HELPERS ---

def safe_text(value: Any, fallback: str = "Not available") -> str:
    """Safely convert any value to non-empty string with fallback."""
    if value is None:
        return fallback
    s = str(value).strip()
    return s if s else fallback


def safe_upper(value: Any, fallback: str = "NOT AVAILABLE") -> str:
    """Safely convert value to uppercase string."""
    if value is None:
        return fallback
    s = str(value).strip()
    return s.upper() if s else fallback


def safe_lower(value: Any, fallback: str = "not available") -> str:
    """Safely convert value to lowercase string."""
    if value is None:
        return fallback
    s = str(value).strip()
    return s.lower() if s else fallback


def safe_title(value: Any, fallback: str = "Not Available") -> str:
    """Safely convert value to title-cased string replacing underscores."""
    if value is None:
        return fallback
    s = str(value).replace("_", " ").strip()
    return s.title() if s else fallback


def safe_list(value: Any) -> list:
    """Safely cast value to list."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, (tuple, set)):
        return list(value)
    return [value]


def safe_dict(value: Any) -> dict:
    """Safely cast value to dict."""
    if isinstance(value, dict):
        return value
    return {}


# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="PROMPT WARS — Multi-Agent Hiring Intelligence",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS matching Local React UI (#0B0F19 background, #131D31 cards, Emerald/Rose badges)
st.markdown("""
<style>
    .main-header {
        font-size: 1.5rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #ffffff;
        margin-bottom: 0.1rem;
    }
    .sub-header {
        color: #94a3b8;
        font-size: 0.85rem;
        margin-bottom: 1.5rem;
    }
    .report-card {
        background-color: #131D31;
        border: 1px solid rgba(51, 65, 85, 0.8);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
    }
    .citation-tag {
        background-color: #0f172a;
        color: #38bdf8;
        border: 1px solid #0284c7;
        border-radius: 4px;
        padding: 2px 6px;
        font-family: monospace;
        font-size: 0.85em;
        font-weight: 600;
    }
    .hire-badge {
        background-color: rgba(16, 185, 129, 0.1);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.2);
        border-radius: 6px;
        padding: 4px 12px;
        font-weight: 700;
        font-size: 1.1rem;
        display: inline-block;
    }
    .no-hire-badge {
        background-color: rgba(244, 63, 94, 0.1);
        color: #fb7185;
        border: 1px solid rgba(244, 63, 94, 0.2);
        border-radius: 6px;
        padding: 4px 12px;
        font-weight: 700;
        font-size: 1.1rem;
        display: inline-block;
    }
    .status-pill-completed {
        background-color: rgba(16, 185, 129, 0.1);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.2);
        border-radius: 9999px;
        padding: 2px 10px;
        font-size: 0.75rem;
        font-weight: 600;
        font-family: monospace;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .traceability-badge {
        color: #cbd5e1;
        font-size: 0.8rem;
        display: flex;
        align-items: center;
        gap: 6px;
        margin-top: 8px;
    }
</style>
""", unsafe_allow_html=True)


# --- PERSISTENT SESSION STATE INITIALIZATION ---
if "current_nav" not in st.session_state:
    st.session_state["current_nav"] = "📊 Dashboard"
if "selected_run_id" not in st.session_state:
    st.session_state["selected_run_id"] = None
if "candidates_count" not in st.session_state:
    st.session_state["candidates_count"] = 1


def set_navigation(page_name: str, run_id: Optional[str] = None):
    """Safely switch page and update selected run ID."""
    st.session_state["current_nav"] = page_name
    if run_id:
        st.session_state["selected_run_id"] = run_id


def run_single_evaluation(candidate_id: str, candidate_name: str, job_id: str,
                           jd_file=None, resume_file=None, transcript_file=None,
                           progress_bar=None, status_text=None) -> RunWorkspace:
    """Execute complete 5-phase evaluation pipeline inside an isolated workspace."""
    workspace = RunWorkspace.create(
        candidate_id=candidate_id,
        candidate_name=candidate_name,
        job_id=job_id
    )

    if jd_file is not None:
        target_jd = workspace.input_dir / "job_description.pdf"
        with open(target_jd, "wb") as f:
            f.write(jd_file.getvalue() if hasattr(jd_file, "getvalue") else jd_file.read())
        workspace.job_description_path = target_jd

    if resume_file is not None:
        target_res = workspace.input_dir / "resume.pdf"
        with open(target_res, "wb") as f:
            f.write(resume_file.getvalue() if hasattr(resume_file, "getvalue") else resume_file.read())
        workspace.resume_path = target_res

    if transcript_file is not None:
        target_trn = workspace.input_dir / "transcript.pdf"
        with open(target_trn, "wb") as f:
            f.write(transcript_file.getvalue() if hasattr(transcript_file, "getvalue") else transcript_file.read())
        workspace.transcript_path = target_trn

    # Phase 1: Ingestion & Rosetta Profile
    save_status(workspace, status="running", phase="rosetta")
    if status_text: status_text.text(f"⏳ [{candidate_name}] Phase 1/5: Constructing Rosetta Evidence Profile...")
    if progress_bar: progress_bar.progress(20)
    rosetta = build_candidate_rosetta(
        candidate_id=workspace.candidate_id,
        candidate_name=workspace.candidate_name,
        workspace=workspace
    )

    # Phase 2: Isolated Personas
    save_status(workspace, status="running", phase="agents")
    if status_text: status_text.text(f"⏳ [{candidate_name}] Phase 2/5: Evaluating 4 Isolated Persona Memos...")
    if progress_bar: progress_bar.progress(40)
    memos = generate_sealed_memos(
        candidate_id=workspace.candidate_id,
        rosetta=rosetta,
        workspace=workspace
    )

    # Phase 3: Debate Session
    save_status(workspace, status="running", phase="debate")
    if status_text: status_text.text(f"⏳ [{candidate_name}] Phase 3/5: Orchestrating General Secretary Debate...")
    if progress_bar: progress_bar.progress(60)
    transcript = run_debate_session(
        candidate_id=workspace.candidate_id,
        rosetta=rosetta,
        memos=memos,
        workspace=workspace
    )

    # Phase 4: Decision & Override
    save_status(workspace, status="running", phase="decision")
    if status_text: status_text.text(f"⏳ [{candidate_name}] Phase 4/5: Synthesizing Binding Decision & Override Motions...")
    if progress_bar: progress_bar.progress(80)
    report_data = synthesize_candidate_decision(
        candidate_id=workspace.candidate_id,
        rosetta=rosetta,
        memos=memos,
        transcript=transcript,
        workspace=workspace
    )

    # Phase 5: PDF & Markdown Reports
    save_status(workspace, status="running", phase="report")
    if status_text: status_text.text(f"⏳ [{candidate_name}] Phase 5/5: Compiling Publication Deliverables...")
    if progress_bar: progress_bar.progress(100)
    generate_candidate_report_artifacts(
        candidate_id=workspace.candidate_id,
        rosetta=rosetta,
        memos=memos,
        transcript=transcript,
        report_data=report_data,
        workspace=workspace
    )

    save_status(workspace, status="completed", phase="finalized")
    if status_text: status_text.text(f"✅ [{candidate_name}] Evaluation complete!")
    return workspace


# --- SIDEBAR NAVIGATION ---
st.sidebar.markdown("### ⚔️ PROMPT WARS")
st.sidebar.caption("Evidence-Grounded Hiring Intelligence")

nav_options = ["📊 Dashboard", "🚀 New Evaluation", "🔬 Evaluation Detail", "🏢 Hiring Room", "👥 Candidates Directory", "📄 Reports Library"]
current_index = nav_options.index(st.session_state["current_nav"]) if st.session_state["current_nav"] in nav_options else 0

selected_nav = st.sidebar.radio(
    "Navigation",
    nav_options,
    index=current_index,
    key="nav_radio"
)
st.session_state["current_nav"] = selected_nav

st.sidebar.markdown("---")
evals_all = list_all_evaluations()
st.sidebar.metric("Total Evaluations", len(evals_all))
st.sidebar.metric("Active Personas", "4 Isolated")

# Live LLM Status / Configuration in Sidebar
with st.sidebar.expander("🔑 Gemini API Configuration", expanded=False):
    current_key = os.environ.get("GEMINI_API_KEY", "") or os.environ.get("GOOGLE_API_KEY", "")
    if current_key:
        masked_k = f"{current_key[:6]}...{current_key[-4:]}"
        st.success(f"🟢 **Live Gemini Engine Active** (`gemini-3.6-flash`)\nKey: `{masked_k}`")
    else:
        st.info("⚪ **Grounded Evaluation Mode**\nEnter your Gemini API key below to activate live multi-agent reasoning:")

    input_k = st.text_input("Enter API Key", type="password", placeholder="AIzaSy... / AQ.Ab8...", key="sidebar_key_input")
    if st.button("Apply API Key", use_container_width=True):
        if input_k.strip():
            os.environ["GEMINI_API_KEY"] = input_k.strip()
            st.success("API key updated!")
            st.rerun()


# =====================================================================
# VIEW 1: DASHBOARD
# =====================================================================
if st.session_state["current_nav"] == "📊 Dashboard":
    st.markdown('<div class="main-header">Recruitment Intelligence Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Overview of active evaluation sessions, candidate profiles, and evidence adjudication.</div>', unsafe_allow_html=True)

    # Metric Row
    evals = list_all_evaluations()
    unique_candidates = len(set([safe_text(e.get("candidate_id")) for e in evals if isinstance(e, dict)]))
    unique_jobs = len(set([safe_text(e.get("job_id")) for e in evals if isinstance(e, dict)]))
    completed_runs = len([e for e in evals if isinstance(e, dict) and safe_text(e.get("status")) == "completed"])

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Evaluations", len(evals))
    with m2:
        st.metric("Unique Candidates", unique_candidates)
    with m3:
        st.metric("Target Roles", unique_jobs)
    with m4:
        st.metric("Completed Verdicts", completed_runs)

    st.markdown("---")

    col_dash_left, col_dash_right = st.columns([2, 1])

    with col_dash_left:
        st.markdown("### Recent Evaluation Sessions")
        if not evals:
            st.info("No evaluation runs recorded yet. Click below to launch your first evaluation.")
            if st.button("🚀 Launch First Evaluation", type="primary"):
                set_navigation("🚀 New Evaluation")
                st.rerun()
        else:
            for e in evals[:6]:
                if not isinstance(e, dict):
                    continue
                rid = safe_text(e.get("run_id"), "unknown_run")
                cid = safe_text(e.get("candidate_id"), "unknown")
                cname = safe_text(e.get("candidate_name"), safe_title(cid))
                jid = safe_text(e.get("job_id"), "default_job")
                status_str = safe_upper(e.get("status"), "COMPLETED")
                created_str = safe_text(e.get("created_at"), "")[:19] or "Recent"

                with st.container():
                    c_info, c_btn = st.columns([3, 1])
                    with c_info:
                        st.markdown(f"**{cname}** — `{safe_title(jid)}`")
                        st.caption(f"Run ID: `{rid}` | Status: `{status_str}` | {created_str}")
                    with c_btn:
                        if st.button("Inspect 🔬", key=f"dash_inspect_{rid}", use_container_width=True):
                            set_navigation("🔬 Evaluation Detail", run_id=rid)
                            st.rerun()
                    st.markdown("<hr style='margin: 4px 0;'/>", unsafe_allow_html=True)

    with col_dash_right:
        st.markdown("### Quick Launch")
        st.markdown("Start an evaluation with arbitrary candidate files or test demo fixtures:")
        if st.button("➕ Create New Evaluation", type="primary", use_container_width=True):
            set_navigation("🚀 New Evaluation")
            st.rerun()

        st.markdown("---")
        st.markdown("### Four Isolated Personas")
        st.markdown("- 🛠️ **Technical Agent**: Architecture, depth, fundamentals")
        st.markdown("- 🤝 **HR / Culture Agent**: Team dynamics & contrarian check")
        st.markdown("- 📈 **Hiring Manager**: Velocity, ROI, ramp-up economics")
        st.markdown("- 🕵️ **Skeptic Agent**: Cross-examination & claim verification")


# =====================================================================
# VIEW 2: NEW EVALUATION
# =====================================================================
elif st.session_state["current_nav"] == "🚀 New Evaluation":
    st.markdown('<div class="main-header">Create New Evaluation</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Upload arbitrary candidate documents or test multi-candidate hiring batches with 100% evidence traceability.</div>', unsafe_allow_html=True)

    # Quick Demo Presets
    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        if st.button("⚡ Preset: Ananya Iyer (Lead AI)", use_container_width=True):
            st.session_state["preset_type"] = "ananya"
            st.session_state["candidates_count"] = 1
            st.rerun()
    with col_d2:
        if st.button("⚡ Preset: Rohan Malhotra (Senior AI)", use_container_width=True):
            st.session_state["preset_type"] = "rohan"
            st.session_state["candidates_count"] = 1
            st.rerun()
    with col_d3:
        if st.button("⚡ Preset: Batch (Both Candidates)", use_container_width=True):
            st.session_state["preset_type"] = "both"
            st.session_state["candidates_count"] = 2
            st.rerun()

    st.markdown("---")

    # Target Role Specification
    st.markdown("#### 1. Target Role & Specification")
    c_j1, c_j2 = st.columns([1, 2])
    with c_j1:
        job_id_input = st.text_input("Job Role Identifier", value="ai_engineer_freight", help="Unique identifier for the target role")
    with c_j2:
        jd_file = st.file_uploader("Upload Job Description (PDF or TXT)", type=["pdf", "txt"], help="Optional if using demo baseline")

    st.markdown("#### 2. Candidate Profiles & Documents")
    
    # Candidate Count Controls
    c_cnt_col1, c_cnt_col2 = st.columns([2, 1])
    with c_cnt_col1:
        num_candidates = st.number_input("Number of Candidates in this Batch", min_value=1, max_value=5, value=st.session_state.get("candidates_count", 1))
        st.session_state["candidates_count"] = int(num_candidates)

    preset = st.session_state.get("preset_type", None)
    candidate_configs = []

    for i in range(int(st.session_state["candidates_count"])):
        with st.expander(f"Candidate #{i+1} Configuration", expanded=True):
            cc1, cc2 = st.columns(2)
            
            if preset == "ananya" and i == 0:
                default_id = "ananya_iyer"
            elif preset == "rohan" and i == 0:
                default_id = "rohan_malhotra"
            elif preset == "both":
                default_id = "ananya_iyer" if i == 0 else "rohan_malhotra"
            else:
                default_id = f"candidate_{i+1}"
            
            default_name = safe_title(default_id)

            with cc1:
                c_name = st.text_input(f"Candidate #{i+1} Full Name", value=default_name, key=f"cname_{i}")
                c_id = st.text_input(f"Candidate #{i+1} Identifier Slug", value=default_id, key=f"cid_{i}")
            with cc2:
                res_f = st.file_uploader(f"Candidate #{i+1} Resume (PDF/TXT)", type=["pdf", "txt"], key=f"cres_{i}")
                trn_f = st.file_uploader(f"Candidate #{i+1} Interview Transcript (PDF/TXT)", type=["pdf", "txt"], key=f"ctrn_{i}")
            
            candidate_configs.append({
                "id": c_id.strip() if c_id else f"candidate_{i+1}",
                "name": c_name.strip() if c_name else f"Candidate {i+1}",
                "res": res_f,
                "trn": trn_f
            })

    if st.button("⚔️ Start Multi-Agent Evaluation", type="primary", use_container_width=True):
        st.markdown("### 🔄 Deliberation Execution")
        progress_bar = st.progress(0)
        status_text = st.empty()

        created_workspaces = []
        for idx, cfg in enumerate(candidate_configs):
            if not cfg["id"]:
                st.error(f"Candidate #{idx+1} ID cannot be empty.")
                continue
            
            ws = run_single_evaluation(
                candidate_id=cfg["id"],
                candidate_name=cfg["name"] or safe_title(cfg["id"]),
                job_id=job_id_input,
                jd_file=jd_file,
                resume_file=cfg["res"],
                transcript_file=cfg["trn"],
                progress_bar=progress_bar,
                status_text=status_text
            )
            created_workspaces.append(ws)

        st.success(f"🎉 Successfully evaluated {len(created_workspaces)} candidate(s)!")
        if created_workspaces:
            set_navigation("🔬 Evaluation Detail", run_id=created_workspaces[0].run_id)
            st.rerun()


# =====================================================================
# VIEW 3: EVALUATION DETAIL
# =====================================================================
elif st.session_state["current_nav"] == "🔬 Evaluation Detail":
    st.markdown('<div class="main-header">Evaluation Detail & Deliberation Inspector</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Deep-dive inspection into evidence bibles, pre-debate memos, debate turns, and decision paths.</div>', unsafe_allow_html=True)

    evals = list_all_evaluations()
    if not evals:
        st.info("No evaluation runs recorded yet. Launch a new evaluation to inspect results.")
        if st.button("🚀 Launch Evaluation", type="primary"):
            set_navigation("🚀 New Evaluation")
            st.rerun()
    else:
        run_ids = [safe_text(e.get("run_id")) for e in evals if e.get("run_id")]
        
        default_index = 0
        if st.session_state.get("selected_run_id") in run_ids:
            default_index = run_ids.index(st.session_state["selected_run_id"])
        
        selected_run = st.selectbox("Select Evaluation Run to Inspect", run_ids, index=default_index)
        st.session_state["selected_run_id"] = selected_run

        # Load workspace data for selected run
        run_dir = settings.runs_dir / selected_run
        st_data = safe_dict(load_status(selected_run))
        
        cid = safe_text(st_data.get("candidate_id"), "unknown")
        cname = safe_text(st_data.get("candidate_name"), safe_title(cid))
        jid = safe_text(st_data.get("job_id"), "default_job")

        # Check for decision data
        decision_file = run_dir / "reports" / f"{cid}_decision.json"
        decision_data = {}
        if decision_file.exists():
            try:
                with open(decision_file, "r", encoding="utf-8") as f:
                    decision_data = safe_dict(json.load(f))
            except Exception:
                decision_data = {}

        # Top Banner Summary
        b_col1, b_col2, b_col3, b_col4 = st.columns(4)
        with b_col1:
            st.metric("Candidate", cname)
        with b_col2:
            st.metric("Target Role", safe_title(jid))
        with b_col3:
            rec = safe_upper(decision_data.get("final_recommendation"), "PENDING")
            if rec == "HIRE":
                st.markdown('<div class="hire-badge">RECOMMENDATION: HIRE</div>', unsafe_allow_html=True)
            elif rec == "NO_HIRE":
                st.markdown('<div class="no-hire-badge">RECOMMENDATION: NO HIRE</div>', unsafe_allow_html=True)
            else:
                st.info(f"STATUS: {rec}")
        with b_col4:
            st.metric("Confidence Level", safe_upper(decision_data.get("confidence_level"), "N/A"))

        st.markdown("---")

        # 6 Deep Dive Tabs
        tab_verdict, tab_rosetta, tab_memos, tab_debate, tab_flow, tab_evidence = st.tabs([
            "🏆 Executive Verdict", "📖 Rosetta Bible", "🔒 Sealed Memos", "⚔️ Debate Replay", "🧭 Decision Path", "🔍 Evidence Explorer"
        ])

        with tab_verdict:
            st.markdown("### General Secretary Adjudication Synthesis")
            dp = safe_dict(decision_data.get("decision_path"))
            st.write(safe_text(dp.get("original_gs_rationale"), "No rationale recorded."))

            ov = safe_dict(dp.get("override_motion"))
            if ov.get("filed_by"):
                filed_by_persona = safe_title(ov.get("filed_by"))
                motion_desc = safe_text(ov.get("motion_text"), "No motion description provided.")
                st.warning(f"**Override Motion Filed by {filed_by_persona}**: {motion_desc}")
                st.caption(f"Outcome: {'PASSED' if ov.get('passed') else 'FAILED'} (Votes: {ov.get('support_count', 0)}/4)")

            c_str, c_con = st.columns(2)
            with c_str:
                st.markdown("#### ✅ Validated Strengths")
                strengths_list = safe_list(decision_data.get("strengths"))
                if not strengths_list:
                    st.caption("No specific strengths recorded.")
                for s in strengths_list:
                    if isinstance(s, dict):
                        claim = safe_text(s.get("claim"), "No claim recorded")
                        cit_id = safe_text(s.get("citation_id"), "N/A")
                        st.markdown(f"- {claim} <span class='citation-tag'>[{cit_id}]</span>", unsafe_allow_html=True)
            with c_con:
                st.markdown("#### ⚠️ Critical Concerns & Gaps")
                concerns_list = safe_list(decision_data.get("concerns"))
                if not concerns_list:
                    st.caption("No specific concerns recorded.")
                for c in concerns_list:
                    if isinstance(c, dict):
                        claim = safe_text(c.get("claim"), "No claim recorded")
                        cit_id = safe_text(c.get("citation_id"), "N/A")
                        st.markdown(f"- {claim} <span class='citation-tag'>[{cit_id}]</span>", unsafe_allow_html=True)

            pdf_path = run_dir / "reports" / f"{cid}_final_report.pdf"
            if pdf_path.exists():
                try:
                    with open(pdf_path, "rb") as pf:
                        st.download_button(
                            label="📄 Download Official PDF Evaluation Report",
                            data=pf.read(),
                            file_name=f"{cid}_final_report.pdf",
                            mime="application/pdf",
                            type="primary"
                        )
                except Exception as e:
                    st.caption(f"PDF download unavailable: {e}")

        with tab_rosetta:
            st.markdown("### Candidate Profile Bible (Rosetta Evidence Model)")
            rosetta_path = run_dir / "rosetta" / f"{cid}.json"
            if rosetta_path.exists():
                try:
                    with open(rosetta_path, "r", encoding="utf-8") as rf_file:
                        rdata = safe_dict(json.load(rf_file))
                except Exception:
                    rdata = {}
                
                c_idx = safe_dict(rdata.get("citations_index"))
                cand_name_display = safe_text(rdata.get("candidate_name"), cname)
                st.caption(f"Candidate: {cand_name_display} | Citations Indexed: {len(c_idx)}")
                
                c_rf1, c_rf2 = st.columns(2)
                with c_rf1:
                    st.markdown("#### Verified Resume Facts")
                    r_facts = safe_list(rdata.get("resume_facts"))
                    if not r_facts:
                        st.caption("No resume facts extracted.")
                    for rf in r_facts:
                        if isinstance(rf, dict):
                            cat = safe_upper(rf.get("category"), "FACT")
                            fact_txt = safe_text(rf.get("fact"), "No fact recorded")
                            cit_id = safe_text(rf.get("citation_id"), "N/A")
                            st.markdown(f"- **{cat}**: {fact_txt} <span class='citation-tag'>[{cit_id}]</span>", unsafe_allow_html=True)
                with c_rf2:
                    st.markdown("#### Interview Transcript Signals")
                    t_facts = safe_list(rdata.get("transcript_facts"))
                    if not t_facts:
                        st.caption("No transcript signals extracted.")
                    for tf in t_facts:
                        if isinstance(tf, dict):
                            q_sum = safe_text(tf.get("question_summary"), "Interview Question")
                            ans_txt = safe_text(tf.get("answer_claim"), "No answer recorded")
                            cit_id = safe_text(tf.get("citation_id"), "N/A")
                            st.markdown(f"- **Q: {q_sum}**\n  {ans_txt} <span class='citation-tag'>[{cit_id}]</span>", unsafe_allow_html=True)
            else:
                st.info("Rosetta profile not found for this run.")

        with tab_memos:
            st.markdown("### Independent Pre-Debate Agent Memos")
            st.caption("Each persona generated its assessment in zero-leakage isolation before group deliberation.")
            
            m_cols = st.columns(4)
            for i, p in enumerate(PERSONAS):
                m_path = run_dir / "memos" / f"{cid}_{p}.json"
                p_title = safe_title(p)
                with m_cols[i]:
                    st.markdown(f"#### {p_title}")
                    if m_path.exists():
                        try:
                            with open(m_path, "r", encoding="utf-8") as mf:
                                m_json = safe_dict(json.load(mf))
                            score_val = m_json.get("score")
                            score_display = f"{score_val}/10" if score_val is not None else "N/A"
                            st.metric("Score", score_display)
                            st.metric("Confidence", safe_upper(m_json.get("confidence_level"), "N/A"))
                            st.markdown(f"**Verdict**: `{safe_upper(m_json.get('recommendation'), 'N/A')}`")
                            with st.expander("Read Strengths & Gaps"):
                                st.write("**Strengths:**")
                                for s in safe_list(m_json.get("strengths")):
                                    if isinstance(s, dict):
                                        st.write(f"- {safe_text(s.get('claim'))} [{safe_text(s.get('citation_id'))}]")
                                st.write("**Gaps:**")
                                for g in safe_list(m_json.get("gaps")):
                                    if isinstance(g, dict):
                                        st.write(f"- {safe_text(g.get('claim'))} [{safe_text(g.get('citation_id'))}]")
                        except Exception as e:
                            st.warning(f"Error loading {p_title} memo: {e}")
                    else:
                        st.caption(f"{p_title} memo not available.")

        with tab_debate:
            st.markdown("### Deliberation Transcript & Cross-Examination")
            debate_path = run_dir / "debate" / f"{cid}_transcript.json"
            if debate_path.exists():
                try:
                    with open(debate_path, "r", encoding="utf-8") as df:
                        d_json = safe_dict(json.load(df))
                except Exception:
                    d_json = {}

                rounds = safe_list(d_json.get("rounds"))
                if not rounds:
                    st.caption("No deliberation rounds recorded.")
                for r_idx, rnd in enumerate(rounds):
                    if not isinstance(rnd, dict):
                        continue
                    r_num = rnd.get("round_number", r_idx + 1)
                    r_agenda = safe_text(rnd.get("agenda_item"), f"Round {r_num}")
                    st.markdown(f"#### 📢 Round {r_num}: {r_agenda}")
                    for turn in safe_list(rnd.get("turns")):
                        if not isinstance(turn, dict):
                            continue
                        persona = safe_title(turn.get("persona"), "Panel Agent")
                        resp_to = turn.get("responds_to")
                        resp = f" *(responding to {safe_title(resp_to)})*" if resp_to else ""
                        with st.chat_message(persona):
                            st.markdown(f"**{persona}**{resp}")
                            st.write(safe_text(turn.get("statement"), "No statement recorded."))
                            cits = safe_list(turn.get("citations"))
                            if cits:
                                tags = " ".join([f"<span class='citation-tag'>[{safe_text(c)}]</span>" for c in cits if c])
                                if tags:
                                    st.markdown(f"Evidence: {tags}", unsafe_allow_html=True)
                            s_delta = turn.get("score_delta")
                            if isinstance(s_delta, dict) and s_delta:
                                prev_s = s_delta.get("previous_score", "N/A")
                                new_s = s_delta.get("new_score", "N/A")
                                reason = safe_text(s_delta.get("reason"), "No reason specified")
                                cit = safe_text(s_delta.get("evidence_citation"), "N/A")
                                st.info(f"🔄 **OPINION CHANGED**: {prev_s} → {new_s} | Reason: {reason} [{cit}]")
            else:
                st.info("Debate transcript not found for this run.")

        with tab_flow:
            st.markdown("### End-to-End Decision Flow")
            rec_val = safe_upper(decision_data.get("final_recommendation"), "HIRE")
            box_color = "#064e3b" if rec_val == "HIRE" else "#7f1d1d"
            st.graphviz_chart(f"""
            digraph G {{
                rankdir=TB;
                node [shape=box, style="filled,rounded", fillcolor="#1e293b", fontcolor="#ffffff", fontname="Arial"];
                edge [color="#60a5fa"];

                subgraph cluster_memos {{
                    label = "1. Pre-Debate Isolated Memos";
                    color="#334155";
                    Tech [label="Technical Agent\\n(Architecture Depth)"];
                    HR [label="HR / Culture Agent\\n(Friction & Growth)"];
                    HM [label="Hiring Manager\\n(Velocity & ROI)"];
                    Skeptic [label="Skeptic Agent\\n(Cross-Examination)"];
                }}

                Debate [label="2. General Secretary Debate\\n(Multi-Round Cross-Examination)", fillcolor="#312e81"];
                GS [label="3. General Secretary Verdict\\n(Non-Averaging Synthesis)", fillcolor="#1e1b4b"];
                Override [label="4. Constitutional Override Check\\n(75% Supermajority Threshold)", fillcolor="#451a03"];
                Final [label="5. Final Binding Decision\\n({rec_val})", fillcolor="{box_color}"];

                Tech -> Debate;
                HR -> Debate;
                HM -> Debate;
                Skeptic -> Debate;
                Debate -> GS;
                GS -> Override;
                Override -> Final;
            }}
            """)

        with tab_evidence:
            st.markdown("### Interactive Master Evidence Explorer")
            rosetta_path = run_dir / "rosetta" / f"{cid}.json"
            if rosetta_path.exists():
                try:
                    with open(rosetta_path, "r", encoding="utf-8") as rf:
                        rdata = safe_dict(json.load(rf))
                except Exception:
                    rdata = {}
                c_index = safe_dict(rdata.get("citations_index"))
                
                search_q = st.text_input("Search verbatim evidence by claim or ID (e.g. T-A7, R-EXP-01):", value="")
                
                for cit_id, cit_info in c_index.items():
                    if not isinstance(cit_info, dict):
                        continue
                    c_id_str = safe_text(cit_id, "CIT-UNKNOWN")
                    quote_str = safe_text(cit_info.get("quote"), "")
                    src_type = safe_upper(cit_info.get("source_type"), "SOURCE")
                    section = safe_text(cit_info.get("section"), "General")
                    doc_name = safe_text(cit_info.get("document"), "Document")
                    page_num = cit_info.get("page", 1) or 1
                    cand_id = safe_text(cit_info.get("candidate_id"), cid)

                    if search_q:
                        sq_l = search_q.lower()
                        if sq_l not in c_id_str.lower() and sq_l not in quote_str.lower() and sq_l not in section.lower():
                            continue

                    with st.expander(f"📌 Citation [{c_id_str}] — {src_type} ({section})"):
                        st.markdown("**Verbatim Source Quote:**")
                        if quote_str:
                            st.info(f"\"{quote_str}\"")
                        else:
                            st.caption("No verbatim quote text recorded.")
                        st.caption(f"Document: {doc_name} | Page: {page_num} | Candidate: {cand_id}")
            else:
                st.info("Evidence index not found for this run.")


# =====================================================================
# VIEW 4: HIRING ROOM (MULTI-CANDIDATE COMPARISON)
# =====================================================================
elif st.session_state["current_nav"] == "🏢 Hiring Room":
    st.markdown('<div class="main-header">Hiring Room: Candidate Comparison Matrix</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Side-by-side comparison matrix for candidates evaluated under the same role.</div>', unsafe_allow_html=True)

    evals = list_all_evaluations()
    if not evals:
        st.info("No candidate evaluations available yet. Run an evaluation to view the comparison matrix.")
        if st.button("🚀 Start Evaluation", type="primary"):
            set_navigation("🚀 New Evaluation")
            st.rerun()
    else:
        # Group by job_id
        jobs = list(set([safe_text(e.get("job_id"), "default_job") for e in evals if isinstance(e, dict)]))
        selected_job = st.selectbox("Select Target Job Role", jobs)

        job_evals = [e for e in evals if isinstance(e, dict) and safe_text(e.get("job_id")) == selected_job]
        st.markdown(f"### Evaluating {len(job_evals)} Candidate(s) for `{safe_title(selected_job)}`")

        matrix_rows = []
        for je in job_evals:
            rid = safe_text(je.get("run_id"), "unknown_run")
            cid = safe_text(je.get("candidate_id"), "unknown")
            cname = safe_text(je.get("candidate_name"), safe_title(cid))
            dec_path = settings.runs_dir / rid / "reports" / f"{cid}_decision.json"
            dec_data = {}
            if dec_path.exists():
                try:
                    with open(dec_path, "r", encoding="utf-8") as f:
                        dec_data = safe_dict(json.load(f))
                except Exception:
                    dec_data = {}

            created_date = safe_text(je.get("created_at"), "")[:10] or "N/A"
            matrix_rows.append({
                "Candidate": cname,
                "Recommendation": safe_upper(dec_data.get("final_recommendation"), "PENDING"),
                "Confidence": safe_upper(dec_data.get("confidence_level"), "N/A"),
                "Strengths Count": len(safe_list(dec_data.get("strengths"))),
                "Concerns Count": len(safe_list(dec_data.get("concerns"))),
                "Run ID": rid,
                "Date": created_date
            })

        st.dataframe(matrix_rows, use_container_width=True)


# =====================================================================
# VIEW 5: CANDIDATES DIRECTORY
# =====================================================================
elif st.session_state["current_nav"] == "👥 Candidates Directory":
    st.markdown('<div class="main-header">Candidates Directory</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Historical evaluation record across all candidate profiles.</div>', unsafe_allow_html=True)

    evals = list_all_evaluations()
    candidates_dict = {}
    for e in evals:
        if not isinstance(e, dict):
            continue
        cid = safe_text(e.get("candidate_id"), "unknown")
        cname = safe_text(e.get("candidate_name"), safe_title(cid))
        job_id = safe_title(e.get("job_id"), "Default Role")
        status_str = safe_upper(e.get("status"), "UNKNOWN")
        run_id = safe_text(e.get("run_id"), "N/A")

        if cid not in candidates_dict:
            candidates_dict[cid] = {
                "Candidate ID": cid,
                "Full Name": cname,
                "Total Evaluations": 1,
                "Latest Job": job_id,
                "Latest Status": status_str,
                "Latest Run": run_id
            }
        else:
            candidates_dict[cid]["Total Evaluations"] += 1

    if candidates_dict:
        st.dataframe(list(candidates_dict.values()), use_container_width=True)
    else:
        st.info("No candidates evaluated yet.")


# =====================================================================
# VIEW 6: REPORTS & DELIVERABLES (PARITY WITH LOCAL /reports)
# =====================================================================
elif st.session_state["current_nav"] == "📄 Reports Library":
    st.markdown('<div class="main-header">Executive Reports & Deliverables</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Publication-quality hiring recommendations with 100% evidence resolution</div>', unsafe_allow_html=True)

    evals = list_all_evaluations()
    completed_evals = [e for e in evals if isinstance(e, dict) and safe_text(e.get("status")) == "completed"]

    if not completed_evals:
        # Match Local EmptyState Component
        st.markdown("""
        <div style="background-color: #131D31; border: 1px dashed rgba(51, 65, 85, 0.8); border-radius: 12px; padding: 40px; text-align: center; margin-top: 16px;">
            <div style="font-size: 2rem; margin-bottom: 8px;">📁</div>
            <h3 style="font-size: 1.1rem; font-weight: 600; color: #ffffff; margin-bottom: 4px;">No completed reports available</h3>
            <p style="font-size: 0.85rem; color: #94a3b8; max-width: 400px; margin: 0 auto 16px auto;">
                Reports are generated automatically once an evaluation panel finishes debate.
            </p>
        </div>
        """, unsafe_allow_html=True)
        col_c1, col_c2, col_c3 = st.columns([1, 1, 1])
        with col_c2:
            if st.button("➕ Create First Evaluation", type="primary", use_container_width=True):
                set_navigation("🚀 New Evaluation")
                st.rerun()
    else:
        # 2-Column Card Grid Matching Local UI: grid grid-cols-1 md:grid-cols-2 gap-5
        for row_start in range(0, len(completed_evals), 2):
            cols = st.columns(2)
            for c_idx in range(2):
                item_idx = row_start + c_idx
                if item_idx < len(completed_evals):
                    e = completed_evals[item_idx]
                    rid = safe_text(e.get("run_id"), "unknown_run")
                    cid = safe_text(e.get("candidate_id"), "unknown")
                    cname = safe_text(e.get("candidate_name"), safe_title(cid))
                    jid = safe_text(e.get("job_id"), "default_role")
                    pdf_path = settings.runs_dir / rid / "reports" / f"{cid}_final_report.pdf"

                    with cols[c_idx]:
                        # Card HTML Structure matching React /reports
                        st.markdown(f"""
                        <div class="report-card">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                <span style="font-family: monospace; font-size: 0.75rem; color: #94a3b8;">{rid}</span>
                                <span class="status-pill-completed"><span style="width: 6px; height: 6px; border-radius: 50%; background-color: #34d399; display: inline-block;"></span>Completed</span>
                            </div>
                            <h3 style="font-size: 1.15rem; font-weight: 700; color: #ffffff; margin: 0 0 2px 0;">{cname}</h3>
                            <p style="font-family: monospace; font-size: 0.75rem; color: #94a3b8; margin: 0 0 12px 0;">Role: {jid}</p>
                            <div class="traceability-badge">
                                <span style="color: #34d399; font-weight: bold;">🛡️</span>
                                <span>100% Evidence Traceability Index Included</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        # Action Bar matching React Link & Download PDF Button
                        act_col1, act_col2 = st.columns(2)
                        with act_col1:
                            if st.button(f"View in UI ↗", key=f"rep_view_{rid}", use_container_width=True):
                                set_navigation("🔬 Evaluation Detail", run_id=rid)
                                st.rerun()
                        with act_col2:
                            if pdf_path.exists():
                                try:
                                    with open(pdf_path, "rb") as pf:
                                        pdf_data = pf.read()
                                    st.download_button(
                                        label="⬇️ Download PDF",
                                        data=pdf_data,
                                        file_name=f"{cid}_final_report.pdf",
                                        mime="application/pdf",
                                        key=f"rep_dl_{rid}",
                                        type="primary",
                                        use_container_width=True
                                    )
                                except Exception as err:
                                    st.caption(f"PDF error: {err}")
                            else:
                                st.caption("PDF deliverable unavailable")
                        st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
