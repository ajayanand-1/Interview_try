"""Streamlit Community Cloud Application for PROMPT WARS (Project Rosetta).
Evidence-Grounded Multi-Agent Hiring Intelligence.
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime, timezone
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

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="PROMPT WARS — Multi-Agent Hiring Intelligence",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Dark Modern Professional Theme
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        background: linear-gradient(135deg, #60a5fa 0%, #a855f7 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
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
        background-color: #064e3b;
        color: #34d399;
        border: 1px solid #059669;
        border-radius: 6px;
        padding: 4px 12px;
        font-weight: 700;
        font-size: 1.1rem;
        display: inline-block;
    }
    .no-hire-badge {
        background-color: #7f1d1d;
        color: #f87171;
        border: 1px solid #dc2626;
        border-radius: 6px;
        padding: 4px 12px;
        font-weight: 700;
        font-size: 1.1rem;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)


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

nav_choice = st.sidebar.radio(
    "Navigation",
    ["🚀 New Evaluation", "📊 Evaluation Sessions", "🏢 Hiring Room", "👥 Candidates Directory", "📄 Reports Library"]
)

st.sidebar.markdown("---")
evals_all = list_all_evaluations()
st.sidebar.metric("Total Evaluations", len(evals_all))
st.sidebar.metric("Active Personas", "4 Isolated")
st.sidebar.caption("🟢 Core Engine v1.0 Online")


# --- PAGE: NEW EVALUATION ---
if nav_choice == "🚀 New Evaluation":
    st.markdown('<div class="main-header">Create New Evaluation</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Upload arbitrary candidate documents or test multi-candidate hiring batches with 100% evidence traceability.</div>', unsafe_allow_html=True)

    # Quick Demo Fixture Buttons
    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        if st.button("⚡ Preset: Ananya Iyer (Lead AI)", use_container_width=True):
            st.session_state["preset_ananya"] = True
    with col_d2:
        if st.button("⚡ Preset: Rohan Malhotra (Senior AI)", use_container_width=True):
            st.session_state["preset_rohan"] = True
    with col_d3:
        if st.button("⚡ Preset: Batch (Both Candidates)", use_container_width=True):
            st.session_state["preset_both"] = True

    st.markdown("---")

    # Target Role Specification
    st.markdown("#### 1. Target Role & Specification")
    c_j1, c_j2 = st.columns([1, 2])
    with c_j1:
        job_id_input = st.text_input("Job Role Identifier", value="ai_engineer_freight", help="Unique identifier for the target role")
    with c_j2:
        jd_file = st.file_uploader("Upload Job Description (PDF or TXT)", type=["pdf", "txt"], help="Optional if using demo files")

    st.markdown("#### 2. Candidate Profiles & Documents")
    
    # Candidate Count selection
    num_candidates = st.number_input("Number of Candidates in this Batch", min_value=1, max_value=5, value=2 if st.session_state.get("preset_both") else 1)

    candidate_configs = []
    for i in range(num_candidates):
        with st.expander(f"Candidate #{i+1} Configuration", expanded=True):
            cc1, cc2 = st.columns(2)
            default_id = "ananya_iyer" if (i == 0 and (st.session_state.get("preset_ananya") or st.session_state.get("preset_both"))) else ("rohan_malhotra" if (i == 1 or st.session_state.get("preset_rohan")) else f"candidate_{i+1}")
            default_name = default_id.replace("_", " ").title()

            with cc1:
                c_name = st.text_input(f"Candidate #{i+1} Full Name", value=default_name, key=f"name_{i}")
                c_id = st.text_input(f"Candidate #{i+1} Identifier Slug", value=default_id, key=f"id_{i}")
            with cc2:
                res_f = st.file_uploader(f"Candidate #{i+1} Resume (PDF/TXT)", type=["pdf", "txt"], key=f"res_{i}")
                trn_f = st.file_uploader(f"Candidate #{i+1} Interview Transcript (PDF/TXT)", type=["pdf", "txt"], key=f"trn_{i}")
            
            candidate_configs.append({
                "id": c_id.strip(),
                "name": c_name.strip(),
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
                candidate_name=cfg["name"] or cfg["id"].replace("_", " ").title(),
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
            st.session_state["selected_run_id"] = created_workspaces[0].run_id
            st.rerun()


# --- PAGE: EVALUATION SESSIONS & DETAIL VIEW ---
elif nav_choice == "📊 Evaluation Sessions":
    st.markdown('<div class="main-header">Evaluation Sessions</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Deep-dive inspection into evidence bibles, pre-debate memos, debate turns, and decision paths.</div>', unsafe_allow_html=True)

    evals = list_all_evaluations()
    if not evals:
        st.info("No evaluation runs recorded yet. Start a new evaluation to inspect results.")
    else:
        run_ids = [e["run_id"] for e in evals]
        selected_run = st.selectbox("Select Evaluation Run to Inspect", run_ids, index=0)

        # Load workspace data for selected run
        run_dir = settings.runs_dir / selected_run
        st_data = load_status(selected_run)
        
        cid = st_data.get("candidate_id", "unknown") if st_data else "unknown"
        cname = st_data.get("candidate_name", cid.replace("_", " ").title()) if st_data else cid.replace("_", " ").title()
        jid = st_data.get("job_id", "default_job") if st_data else "default_job"

        # Check for decision data
        decision_file = run_dir / "reports" / f"{cid}_decision.json"
        decision_data = {}
        if decision_file.exists():
            with open(decision_file, "r", encoding="utf-8") as f:
                decision_data = json.load(f)

        # Top Banner Summary
        b_col1, b_col2, b_col3, b_col4 = st.columns(4)
        with b_col1:
            st.metric("Candidate", cname)
        with b_col2:
            st.metric("Target Role", jid.replace("_", " ").title())
        with b_col3:
            rec = decision_data.get("final_recommendation", "PENDING").upper()
            if rec == "HIRE":
                st.markdown('<div class="hire-badge">RECOMMENDATION: HIRE</div>', unsafe_allow_html=True)
            elif rec == "NO_HIRE":
                st.markdown('<div class="no-hire-badge">RECOMMENDATION: NO HIRE</div>', unsafe_allow_html=True)
            else:
                st.info(f"STATUS: {rec}")
        with b_col4:
            st.metric("Confidence Level", (decision_data.get("confidence_level") or "N/A").upper())

        st.markdown("---")

        # 6 Deep Dive Tabs
        tab_verdict, tab_rosetta, tab_memos, tab_debate, tab_flow, tab_evidence = st.tabs([
            "🏆 Executive Verdict", "📖 Rosetta Bible", "🔒 Sealed Memos", "⚔️ Debate Replay", "🧭 Decision Path", "🔍 Evidence Explorer"
        ])

        with tab_verdict:
            st.markdown("### General Secretary Adjudication Synthesis")
            dp = decision_data.get("decision_path", {})
            st.write(dp.get("original_gs_rationale", "No rationale recorded."))

            ov = dp.get("override_motion")
            if ov and ov.get("filed_by"):
                st.warning(f"**Override Motion Filed by {ov['filed_by'].replace('_', ' ').title()}**: {ov['motion_text']}")
                st.caption(f"Outcome: {'PASSED' if ov.get('passed') else 'FAILED'} (Votes: {ov.get('support_count', 0)}/4)")

            c_str, c_con = st.columns(2)
            with c_str:
                st.markdown("#### ✅ Validated Strengths")
                for s in decision_data.get("strengths", []):
                    st.markdown(f"- {s['claim']} <span class='citation-tag'>[{s['citation_id']}]</span>", unsafe_allow_html=True)
            with c_con:
                st.markdown("#### ⚠️ Critical Concerns & Gaps")
                for c in decision_data.get("concerns", []):
                    st.markdown(f"- {c['claim']} <span class='citation-tag'>[{c['citation_id']}]</span>", unsafe_allow_html=True)

            pdf_path = run_dir / "reports" / f"{cid}_final_report.pdf"
            if pdf_path.exists():
                with open(pdf_path, "rb") as pf:
                    st.download_button(
                        label="📄 Download Official PDF Evaluation Report",
                        data=pf.read(),
                        file_name=f"{cid}_final_report.pdf",
                        mime="application/pdf",
                        type="primary"
                    )

        with tab_rosetta:
            st.markdown("### Candidate Profile Bible (Rosetta Evidence Model)")
            rosetta_path = run_dir / "rosetta" / f"{cid}.json"
            if rosetta_path.exists():
                with open(rosetta_path, "r", encoding="utf-8") as rf:
                    rdata = json.load(rf)
                
                st.caption(f"Candidate: {rdata.get('candidate_name')} | Citations Indexed: {len(rdata.get('citations_index', {}))}")
                
                c_rf1, c_rf2 = st.columns(2)
                with c_rf1:
                    st.markdown("#### Verified Resume Facts")
                    for rf in rdata.get("resume_facts", []):
                        st.markdown(f"- **{rf.get('category', '').upper()}**: {rf.get('fact')} <span class='citation-tag'>[{rf.get('citation_id')}]</span>", unsafe_allow_html=True)
                with c_rf2:
                    st.markdown("#### Interview Transcript Signals")
                    for tf in rdata.get("transcript_facts", []):
                        st.markdown(f"- **Q: {tf.get('question_summary', '')}**\n  {tf.get('answer_claim')} <span class='citation-tag'>[{tf.get('citation_id')}]</span>", unsafe_allow_html=True)

        with tab_memos:
            st.markdown("### Independent Pre-Debate Agent Memos")
            st.caption("Each persona generated its assessment in zero-leakage isolation before group deliberation.")
            
            m_cols = st.columns(4)
            for i, p in enumerate(PERSONAS):
                m_path = run_dir / "memos" / f"{cid}_{p}.json"
                with m_cols[i]:
                    st.markdown(f"#### {p.replace('_', ' ').title()}")
                    if m_path.exists():
                        with open(m_path, "r", encoding="utf-8") as mf:
                            m_json = json.load(mf)
                        st.metric("Score", f"{m_json.get('score', 'N/A')}/10")
                        st.metric("Confidence", (m_json.get('confidence_level') or 'N/A').upper())
                        st.markdown(f"**Verdict**: `{m_json.get('recommendation', 'N/A').upper()}`")
                        with st.expander("Read Strengths & Gaps"):
                            st.write("**Strengths:**")
                            for s in m_json.get("strengths", []):
                                st.write(f"- {s.get('claim')} [{s.get('citation_id')}]")
                            st.write("**Gaps:**")
                            for g in m_json.get("gaps", []):
                                st.write(f"- {g.get('claim')} [{g.get('citation_id')}]")

        with tab_debate:
            st.markdown("### Deliberation Transcript & Cross-Examination")
            debate_path = run_dir / "debate" / f"{cid}_transcript.json"
            if debate_path.exists():
                with open(debate_path, "r", encoding="utf-8") as df:
                    d_json = json.load(df)

                for r_idx, rnd in enumerate(d_json.get("rounds", [])):
                    st.markdown(f"#### 📢 Round {rnd.get('round_number', r_idx+1)}: {rnd.get('agenda_item', '')}")
                    for turn in rnd.get("turns", []):
                        persona = turn.get("persona", "").replace("_", " ").title()
                        resp = f" *(responding to {turn.get('responds_to').replace('_', ' ').title()})*" if turn.get("responds_to") else ""
                        with st.chat_message(persona):
                            st.markdown(f"**{persona}**{resp}")
                            st.write(turn.get("statement", ""))
                            if turn.get("citations"):
                                tags = " ".join([f"<span class='citation-tag'>[{c}]</span>" for c in turn["citations"]])
                                st.markdown(f"Evidence: {tags}", unsafe_allow_html=True)
                            if turn.get("score_delta"):
                                d = turn["score_delta"]
                                st.info(f"🔄 **OPINION CHANGED**: {d.get('previous_score')} → {d.get('new_score')} | Reason: {d.get('reason')} [{d.get('evidence_citation')}]")

        with tab_flow:
            st.markdown("### End-to-End Decision Flow")
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
                Final [label="5. Final Binding Decision\\n({decision_data.get('final_recommendation', 'HIRE').upper()})", fillcolor="#064e3b" if decision_data.get('final_recommendation') == 'hire' else "#7f1d1d"];

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
                with open(rosetta_path, "r", encoding="utf-8") as rf:
                    rdata = json.load(rf)
                c_index = rdata.get("citations_index", {})
                
                search_q = st.text_input("Search verbatim evidence by claim or ID (e.g. T-A7, R-EXP-01):", value="")
                
                for cit_id, cit_info in c_index.items():
                    if search_q and search_q.lower() not in cit_id.lower() and search_q.lower() not in cit_info.get("quote", "").lower():
                        continue
                    with st.expander(f"📌 Citation [{cit_id}] — {cit_info.get('source_type', '').upper()} ({cit_info.get('section', '')})"):
                        st.markdown(f"**Verbatim Source Quote:**")
                        st.info(f"\"{cit_info.get('quote')}\"")
                        st.caption(f"Document: {cit_info.get('document')} | Page: {cit_info.get('page', 1)} | Candidate: {cit_info.get('candidate_id')}")


# --- PAGE: HIRING ROOM (MULTI-CANDIDATE MATRIX) ---
elif nav_choice == "🏢 Hiring Room":
    st.markdown('<div class="main-header">Hiring Room: Candidate Matrix</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Side-by-side comparison matrix for candidates evaluated under the same role.</div>', unsafe_allow_html=True)

    evals = list_all_evaluations()
    if not evals:
        st.info("No candidate evaluations available yet.")
    else:
        # Group by job_id
        jobs = list(set([e["job_id"] for e in evals]))
        selected_job = st.selectbox("Select Target Job Role", jobs)

        job_evals = [e for e in evals if e["job_id"] == selected_job]
        st.markdown(f"### Evaluating {len(job_evals)} Candidate(s) for `{selected_job.replace('_', ' ').title()}`")

        matrix_rows = []
        for je in job_evals:
            rid = je["run_id"]
            cid = je["candidate_id"]
            dec_path = settings.runs_dir / rid / "reports" / f"{cid}_decision.json"
            dec_data = {}
            if dec_path.exists():
                with open(dec_path, "r", encoding="utf-8") as f:
                    dec_data = json.load(f)

            matrix_rows.append({
                "Candidate": je["candidate_name"],
                "Recommendation": (dec_data.get("final_recommendation") or "PENDING").upper(),
                "Confidence": (dec_data.get("confidence_level") or "N/A").upper(),
                "Strengths Count": len(dec_data.get("strengths", [])),
                "Concerns Count": len(dec_data.get("concerns", [])),
                "Run ID": rid,
                "Date": je["created_at"][:10]
            })

        st.dataframe(matrix_rows, use_container_width=True)


# --- PAGE: CANDIDATES DIRECTORY ---
elif nav_choice == "👥 Candidates Directory":
    st.markdown('<div class="main-header">Candidates Directory</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Historical evaluation record across all candidate profiles.</div>', unsafe_allow_html=True)

    evals = list_all_evaluations()
    candidates_dict = {}
    for e in evals:
        cid = e["candidate_id"]
        if cid not in candidates_dict:
            candidates_dict[cid] = {
                "Candidate ID": cid,
                "Full Name": e["candidate_name"],
                "Total Evaluations": 1,
                "Latest Job": e["job_id"].replace("_", " ").title(),
                "Latest Status": e["status"].upper(),
                "Latest Run": e["run_id"]
            }
        else:
            candidates_dict[cid]["Total Evaluations"] += 1

    st.dataframe(list(candidates_dict.values()), use_container_width=True)


# --- PAGE: REPORTS LIBRARY ---
elif nav_choice == "📄 Reports Library":
    st.markdown('<div class="main-header">Publication Reports Library</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Download official evidence-backed PDF deliberation reports.</div>', unsafe_allow_html=True)

    evals = list_all_evaluations()
    for e in evals:
        rid = e["run_id"]
        cid = e["candidate_id"]
        pdf_path = settings.runs_dir / rid / "reports" / f"{cid}_final_report.pdf"
        
        with st.container():
            c1, c2, c3 = st.columns([2, 2, 1])
            with c1:
                st.markdown(f"**{e['candidate_name']}** (`{cid}`)")
                st.caption(f"Role: {e['job_id'].replace('_', ' ').title()} | Run: {rid}")
            with c2:
                st.caption(f"Evaluated on {e['created_at'][:19]}")
            with c3:
                if pdf_path.exists():
                    with open(pdf_path, "rb") as pf:
                        st.download_button(
                            label="⬇️ Download PDF",
                            data=pf.read(),
                            file_name=f"{cid}_final_report.pdf",
                            mime="application/pdf",
                            key=f"dl_{rid}"
                        )
                else:
                    st.caption("PDF generating...")
            st.markdown("---")
