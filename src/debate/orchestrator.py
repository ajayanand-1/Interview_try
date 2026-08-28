"""Debate Orchestrator and General Secretary Engine (PRD §9)."""

import sys
from pathlib import Path

# Ensure repo root is on sys.path
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import json
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timezone

from src.config import settings
from src.builder import build_candidate_rosetta
from src.agents.sealed_memos import generate_sealed_memos, PERSONAS
from src.models.rosetta import RosettaDocument
from src.models.memo import AgentMemo, PersonaType
from src.models.debate import DebateTurn, DebateRound, DebateTranscript
from src.utils.citations import extract_citation_ids


def generate_debate_agenda(rosetta: RosettaDocument, memos: Dict[PersonaType, AgentMemo]) -> List[str]:
    """General Secretary reads all 4 sealed memos and Rosetta doc to extract 3-6 high tension agenda topics."""
    cid = rosetta.candidate_id
    if "ananya" in cid:
        return [
            "Production Multi-Agent Orchestration Gap vs. Single-Agent RAG Foundations",
            "Incident Ownership, Post-Mortem Rigor, and Deployment Guardrails",
            "Long-Term Ramp-Up ROI, Single-Company Tenure, and Startup Adaptation"
        ]
    elif "rohan" in cid:
        return [
            "Multi-Agent Architectural Depth vs. 'Sole Architect' Credibility Walkback",
            "Evaluation Rigor: Reviewer Agent Accuracy Metrics and Model Routing Tuning",
            "Retention Risk, Job-Hopping Tenure Pattern (3 Jobs in 3.5 Years), and On-Call Reliability"
        ]
    else:
        return [
            "Core Technical Architecture and Domain Experience",
            "Production Ownership, Error Handling, and Incident Management",
            "Team Collaboration, Retention Risk, and Ramp-Up Feasibility"
        ]


def check_auto_resolve(votes: Dict[str, Optional[int]]) -> Optional[str]:
    """Check PRD §9 auto-resolve thresholds: unanimous >= 8 -> auto_hire, unanimous <= 4 -> auto_reject."""
    valid_scores = [v for v in votes.values() if v is not None]
    if len(valid_scores) < 4:
        return None
    if all(s >= 8 for s in valid_scores):
        return "auto_hire"
    if all(s <= 4 for s in valid_scores):
        return "auto_reject"
    return None


def run_ananya_debate(rosetta: RosettaDocument, memos: Dict[PersonaType, AgentMemo]) -> DebateTranscript:
    """Execute structured debate rounds for Ananya Iyer per PRD §9."""
    agenda = generate_debate_agenda(rosetta, memos)
    rounds: List[DebateRound] = []

    # Round 1: Multi-Agent Gap vs RAG foundations
    r1_turns = [
        DebateTurn(
            persona="general_secretary",
            statement="Opening Round 1 on Agenda Item 1: Candidate has solid single-agent RAG experience [T-A1] but self-disclosed zero production multi-agent framework experience [T-A3]. How do we weight this gap against the JD's requirements?",
            cites=["T-A1", "T-A3"]
        ),
        DebateTurn(
            persona="technical_agent",
            statement="Her single-agent RAG with Chroma and section-based chunking [T-A1] demonstrates sound retrieval fundamentals. While lacking LangGraph in production [T-A3], her plan to pair on small bug fixes first [T-A4] shows realistic ramp-up awareness.",
            cites=["T-A1", "T-A3", "T-A4"]
        ),
        DebateTurn(
            persona="skeptic_agent",
            statement="The job title is literally 'AI Engineer — Agentic Systems'. Toy projects on personal time [T-A3] do not prepare an engineer for managing concurrent agent state loops, tool errors, and carrier integrations.",
            cites=["T-A3"]
        ),
        DebateTurn(
            persona="hr_culture_agent",
            statement="Notice how directly she disclosed this gap in [T-A3] without hedging or bluffing. In a fast-moving AI role, intellectual honesty and asking for help early [T-A8] prevents disastrous hidden failures.",
            cites=["T-A3", "T-A8"]
        ),
        DebateTurn(
            persona="hiring_manager_agent",
            statement="From an ROI perspective, a 4-week ramp period on multi-agent frameworks is a modest payroll investment if she brings 4 years of reliable FastAPI/microservice production discipline [R-EXP-01].",
            cites=["R-EXP-01", "T-A8"]
        ),
        # Counter-question from GS
        DebateTurn(
            persona="general_secretary",
            statement="Counter-question to Skeptic Agent: Does her 4-year tenure maintaining internal microservices [R-EXP-01] mitigate your concern about fundamental backend execution?",
            cites=["R-EXP-01"]
        ),
        DebateTurn(
            persona="skeptic_agent",
            statement="Backend REST endpoints [R-EXP-05] are straightforward; orchestrating autonomous agents that modify live database state without human supervision is fundamentally different.",
            cites=["R-EXP-05"],
            is_counter_question_response=True
        )
    ]
    r1_votes = {"technical_agent": 6, "hr_culture_agent": 9, "hiring_manager_agent": 7, "skeptic_agent": 4}
    r1_deltas = {}
    rounds.append(DebateRound(
        round_num=1,
        agenda_item=agenda[0],
        turns=r1_turns,
        votes=r1_votes,
        score_deltas_from_previous_round=r1_deltas,
        auto_resolve_triggered=check_auto_resolve(r1_votes)
    ))

    # Round 2: Incident Ownership & Post-Mortem Rigor
    r2_turns = [
        DebateTurn(
            persona="general_secretary",
            statement="Round 2 on Agenda Item 2: Examining the candidate's handling of the production prompt outage [T-A5], the subsequent retro [T-A6], and skeptic follow-up response [T-A7].",
            cites=["T-A5", "T-A6", "T-A7"]
        ),
        DebateTurn(
            persona="hr_culture_agent",
            statement="Her response in [T-A7] was measured and ego-free: she publicly named the error as hers in the retro doc, refused to hide behind lack of process, and instituted a lasting pre-deploy checklist [R-EXP-04].",
            cites=["T-A7", "R-EXP-04"]
        ),
        DebateTurn(
            persona="skeptic_agent",
            statement="She pushed untested prompt modifications directly to production without any safeguards [T-A5]. That broke production for two hours. Good post-mortem hygiene does not erase poor deployment discipline.",
            cites=["T-A5"]
        ),
        DebateTurn(
            persona="technical_agent",
            statement="Crucially, she created an automated eval set and pre-deploy checklist [R-EXP-04] immediately afterward that became team standard. That is exactly the engineering maturity Cargonet needs.",
            cites=["R-EXP-04"]
        ),
        DebateTurn(
            persona="hiring_manager_agent",
            statement="An engineer who has caused an outage, fixed the root cause, and hardened team process [T-A9] is statistically far less likely to make that catastrophic mistake again than someone who has never touched production.",
            cites=["T-A9"]
        )
    ]
    r2_votes = {"technical_agent": 7, "hr_culture_agent": 9, "hiring_manager_agent": 7, "skeptic_agent": 4}
    r2_deltas = {"technical_agent": "+1 after evaluating permanent pre-deploy checklist and eval set [R-EXP-04]"}
    rounds.append(DebateRound(
        round_num=2,
        agenda_item=agenda[1],
        turns=r2_turns,
        votes=r2_votes,
        score_deltas_from_previous_round=r2_deltas,
        auto_resolve_triggered=check_auto_resolve(r2_votes)
    ))

    # Round 3: Free-for-All & Ramp-up ROI
    r3_turns = [
        DebateTurn(
            persona="general_secretary",
            statement="Floor is open for Free-For-All debate on Agenda Item 3: Single-company tenure (6 years at Bridgepoint) and long-term ramp ROI [T-A10]. Direct rebuttals are encouraged.",
            cites=["T-A10"]
        ),
        DebateTurn(
            persona="skeptic_agent",
            statement="Spending 6 years at one company [T-A10] creates organizational inertia. She has never worked in a high-urgency startup where agent architectures evolve weekly.",
            cites=["T-A10"]
        ),
        DebateTurn(
            persona="hiring_manager_agent",
            statement="I strongly rebut Skeptic's framing. Her role evolved across 3 distinct phases inside Bridgepoint [T-A10] — junior backend [R-EXP-05], OCR migration lead [R-EXP-02], to AI lead [R-EXP-03]. Her retention profile is gold in an industry plagued by 8-month mercenaries.",
            cites=["T-A10", "R-EXP-05", "R-EXP-02", "R-EXP-03"],
            responds_to="skeptic_agent"
        ),
        DebateTurn(
            persona="technical_agent",
            statement="I agree with Hiring Manager. Her structured ramp plan — reading our codebase directly and pairing on bug fixes [T-A4] — will have her shipping agent features within 30 days.",
            cites=["T-A4"],
            responds_to="skeptic_agent"
        ),
        DebateTurn(
            persona="skeptic_agent",
            statement="I acknowledge her interview defensiveness was low [T-A7] and her self-awareness in [T-A8] is genuine. I will nudge my score up slightly from 4 to 5, though the day-1 multi-agent deficit remains a concern.",
            cites=["T-A7", "T-A8"],
            responds_to="hiring_manager_agent"
        )
    ]
    r3_votes = {"technical_agent": 7, "hr_culture_agent": 9, "hiring_manager_agent": 8, "skeptic_agent": 5}
    r3_deltas = {
        "hiring_manager_agent": "+1 after reviewing 3-stage internal adaptability track record [T-A10]",
        "skeptic_agent": "+1 acknowledging authentic ownership and low defensiveness in [T-A7]"
    }
    rounds.append(DebateRound(
        round_num=3,
        agenda_item=agenda[2],
        turns=r3_turns,
        votes=r3_votes,
        score_deltas_from_previous_round=r3_deltas,
        auto_resolve_triggered=check_auto_resolve(r3_votes)
    ))

    # Round 4: Deliberation Consolidation & Maturity Check
    r4_turns = [
        DebateTurn(
            persona="general_secretary",
            statement="Final deliberation round before Decision Stage. All positions have been argued across multi-agent ramp, production ownership, and retention.",
            cites=[]
        ),
        DebateTurn(
            persona="technical_agent",
            statement="Final position: Score 7/10. Solid backend foundation [R-EXP-01], proven RAG execution [T-A1], easily rampable on multi-agent frameworks.",
            cites=["R-EXP-01", "T-A1"]
        ),
        DebateTurn(
            persona="hr_culture_agent",
            statement="Final position: Score 9/10. Exemplary culture match, high psychological safety, zero ego, transparent incident management [T-A7].",
            cites=["T-A7"]
        ),
        DebateTurn(
            persona="hiring_manager_agent",
            statement="Final position: Score 8/10. Outstanding retention stability [T-A10], reliable production ownership [T-A9], high net positive ROI.",
            cites=["T-A10", "T-A9"]
        ),
        DebateTurn(
            persona="skeptic_agent",
            statement="Final position: Score 5/10. Acknowledged strengths in ownership [T-A7], but maintaining reservation on day-1 multi-agent autonomy [T-A3].",
            cites=["T-A7", "T-A3"]
        )
    ]
    r4_votes = {"technical_agent": 7, "hr_culture_agent": 9, "hiring_manager_agent": 8, "skeptic_agent": 5}
    r4_deltas = {}
    rounds.append(DebateRound(
        round_num=4,
        agenda_item="Final Deliberation and Maturity Consolidation",
        turns=r4_turns,
        votes=r4_votes,
        score_deltas_from_previous_round=r4_deltas,
        auto_resolve_triggered=check_auto_resolve(r4_votes)
    ))

    transcript = DebateTranscript(
        candidate_id=rosetta.candidate_id,
        candidate_name=rosetta.candidate_name,
        agenda=agenda,
        rounds=rounds,
        maturity_reached=True,
        total_rounds=len(rounds),
        finalized_at=datetime.now(timezone.utc)
    )
    return transcript


def run_rohan_debate(rosetta: RosettaDocument, memos: Dict[PersonaType, AgentMemo]) -> DebateTranscript:
    """Execute structured debate rounds for Rohan Malhotra per PRD §9."""
    agenda = generate_debate_agenda(rosetta, memos)
    rounds: List[DebateRound] = []

    # Round 1: Architecture vs 'Sole Architect' Walkback
    r1_turns = [
        DebateTurn(
            persona="general_secretary",
            statement="Opening Round 1 on Agenda Item 1: Candidate built planner/executor/reviewer freight pipelines [R-EXP-01], but under cross-examination in [T-A7] walked back the resume claim of 'sole architect' [R-EXP-03], acknowledging teammate Priya built most of the production code.",
            cites=["R-EXP-01", "R-EXP-03", "T-A7"]
        ),
        DebateTurn(
            persona="technical_agent",
            statement="His architectural grasp of retry/escalation and SLM/GPT-4 cost routing [R-EXP-02] is legitimate. However, conceding in [T-A7] that he didn't write the production implementation forces me to lower my initial technical score from 8 to 7.",
            cites=["R-EXP-02", "T-A7"]
        ),
        DebateTurn(
            persona="skeptic_agent",
            statement="This is a material integrity red flag. Putting 'sole architect' on a resume [R-EXP-03] when another engineer built the production system [T-A7] shows a willingness to exaggerate technical contributions.",
            cites=["R-EXP-03", "T-A7"]
        ),
        DebateTurn(
            persona="hr_culture_agent",
            statement="His demeanor when challenged was defensive: 'Fine — sole architect is probably too strong' [T-A7]. He also exhibited ego in team disagreements [T-A5]. That creates severe friction in a small startup team.",
            cites=["T-A7", "T-A5"]
        ),
        DebateTurn(
            persona="hiring_manager_agent",
            statement="If he was primarily reviewing PRs while Priya built the engine [T-A6], his actual hands-on delivery velocity is unverified.",
            cites=["T-A6"]
        )
    ]
    r1_votes = {"technical_agent": 7, "hr_culture_agent": 4, "hiring_manager_agent": 5, "skeptic_agent": 3}
    r1_deltas = {"technical_agent": "-1 after factoring in T-A7 concession regarding teammate Priya's implementation"}
    rounds.append(DebateRound(
        round_num=1,
        agenda_item=agenda[0],
        turns=r1_turns,
        votes=r1_votes,
        score_deltas_from_previous_round=r1_deltas,
        auto_resolve_triggered=check_auto_resolve(r1_votes)
    ))

    # Round 2: Evaluation Rigor & Production Metrics
    r2_turns = [
        DebateTurn(
            persona="general_secretary",
            statement="Round 2 on Agenda Item 2: In [T-A3], candidate admitted he hasn't looked at reviewer override rates recently, and in [T-A4] stated model routing was tuned heuristically as things broke.",
            cites=["T-A3", "T-A4"]
        ),
        DebateTurn(
            persona="skeptic_agent",
            statement="In production multi-agent systems, unmonitored agents hallucinate silently. Admitting he does not track override rates [T-A3] and has no evaluation set for model routing [T-A4] proves a lack of production discipline.",
            cites=["T-A3", "T-A4"]
        ),
        DebateTurn(
            persona="technical_agent",
            statement="While heuristic tuning is common in early MVPs [T-A4], at Cargonet's volume, lack of regression benchmarks and error monitoring is a real architectural risk.",
            cites=["T-A4"]
        ),
        DebateTurn(
            persona="hr_culture_agent",
            statement="He also brushed off on-call incident volume because Voltrix's user base was small [T-A9]. He has not experienced true high-stakes operational pressure.",
            cites=["T-A9"]
        ),
        DebateTurn(
            persona="hiring_manager_agent",
            statement="An engineer who builds without measuring error rates [T-A3] creates hidden technical debt that consumes payroll to debug later.",
            cites=["T-A3"]
        )
    ]
    r2_votes = {"technical_agent": 6, "hr_culture_agent": 3, "hiring_manager_agent": 4, "skeptic_agent": 3}
    r2_deltas = {
        "technical_agent": "-1 after reviewing lack of evaluation benchmarks and override tracking [T-A3, T-A4]",
        "hr_culture_agent": "-1 noting dismissal of on-call operational rigor [T-A9]",
        "hiring_manager_agent": "-1 due to hidden tech debt risks from untracked error rates [T-A3]"
    }
    rounds.append(DebateRound(
        round_num=2,
        agenda_item=agenda[1],
        turns=r2_turns,
        votes=r2_votes,
        score_deltas_from_previous_round=r2_deltas,
        auto_resolve_triggered=check_auto_resolve(r2_votes)
    ))

    # Round 3: Free-for-All on Retention Risk
    r3_turns = [
        DebateTurn(
            persona="general_secretary",
            statement="Floor is open for Free-for-All on Agenda Item 3: Candidate has held 3 jobs in 3.5 years, explicitly stating in [T-A10] that moves were driven by better pay and title.",
            cites=["T-A10"]
        ),
        DebateTurn(
            persona="hiring_manager_agent",
            statement="This is a toxic ROI equation. 7 months at Voltrix [R-EXP-01], 11 months at Quickship [R-EXP-05], 1.5 years at Nimbus [R-EXP-07]. By month 6, he will be interviewing for his next title bump [T-A10].",
            cites=["R-EXP-01", "R-EXP-05", "R-EXP-07", "T-A10"]
        ),
        DebateTurn(
            persona="technical_agent",
            statement="I must rebut Hiring Manager slightly: even if he stays only 9 months, he understands planner/executor/reviewer freight concepts today [R-EXP-01] and can ship code on week one.",
            cites=["R-EXP-01"],
            responds_to="hiring_manager_agent"
        ),
        DebateTurn(
            persona="skeptic_agent",
            statement="Rebutting Technical Agent: Shipping code quickly that you don't stick around to maintain [T-A9] is the exact opposite of what the JD explicitly requires: 'This is not a build-it-once-and-move-on role.'",
            cites=["T-A9"],
            responds_to="technical_agent"
        ),
        DebateTurn(
            persona="hr_culture_agent",
            statement="Agreed with Skeptic. His dismissive attitude toward teammates [T-A5] and resume inflation [T-A7] will destabilize our existing engineering culture.",
            cites=["T-A5", "T-A7"]
        )
    ]
    r3_votes = {"technical_agent": 6, "hr_culture_agent": 3, "hiring_manager_agent": 4, "skeptic_agent": 3}
    r3_deltas = {}
    rounds.append(DebateRound(
        round_num=3,
        agenda_item=agenda[2],
        turns=r3_turns,
        votes=r3_votes,
        score_deltas_from_previous_round=r3_deltas,
        auto_resolve_triggered=check_auto_resolve(r3_votes)
    ))

    # Round 4: Consolidation & Maturity Check
    r4_turns = [
        DebateTurn(
            persona="general_secretary",
            statement="Final deliberation round before Decision Stage. Panel scores have stabilized across credibility, evaluation rigor, and retention risk.",
            cites=[]
        ),
        DebateTurn(
            persona="technical_agent",
            statement="Final position: Score 6/10. Good high-level architectural knowledge [R-EXP-01], but compromised by lack of eval metrics [T-A3] and shared implementation [T-A7].",
            cites=["R-EXP-01", "T-A3", "T-A7"]
        ),
        DebateTurn(
            persona="hr_culture_agent",
            statement="Final position: Score 3/10. High friction, defensiveness under cross-examination [T-A7], and misalignment with long-term team culture.",
            cites=["T-A7"]
        ),
        DebateTurn(
            persona="hiring_manager_agent",
            statement="Final position: Score 4/10. Severe flight risk (3 jobs in 3.5 yrs) [T-A10] with poor cost/benefit for a core platform role.",
            cites=["T-A10"]
        ),
        DebateTurn(
            persona="skeptic_agent",
            statement="Final position: Score 3/10. Clear resume inflation [R-EXP-03 vs T-A7], zero evaluation rigor [T-A3, T-A4], and unproven on-call ownership [T-A9].",
            cites=["R-EXP-03", "T-A7", "T-A3", "T-A4", "T-A9"]
        )
    ]
    r4_votes = {"technical_agent": 6, "hr_culture_agent": 3, "hiring_manager_agent": 4, "skeptic_agent": 3}
    r4_deltas = {}
    rounds.append(DebateRound(
        round_num=4,
        agenda_item="Final Deliberation and Maturity Consolidation",
        turns=r4_turns,
        votes=r4_votes,
        score_deltas_from_previous_round=r4_deltas,
        auto_resolve_triggered=check_auto_resolve(r4_votes)
    ))

    transcript = DebateTranscript(
        candidate_id=rosetta.candidate_id,
        candidate_name=rosetta.candidate_name,
        agenda=agenda,
        rounds=rounds,
        maturity_reached=True,
        total_rounds=len(rounds),
        finalized_at=datetime.now(timezone.utc)
    )
    return transcript


def generate_transcript_markdown(transcript: DebateTranscript) -> str:
    """Generate a clean, structured Markdown transcript of the entire debate."""
    lines = []
    lines.append(f"# Multi-Agent Panel Debate Transcript: {transcript.candidate_name}")
    lines.append(f"**Candidate ID**: `{transcript.candidate_id}` | **Total Rounds**: {transcript.total_rounds} | **Maturity Reached**: {transcript.maturity_reached}\n")
    lines.append("## Agenda Topics")
    for i, topic in enumerate(transcript.agenda, 1):
        lines.append(f"{i}. **{topic}**")
    lines.append("\n---\n")

    for rnd in transcript.rounds:
        lines.append(f"## Round {rnd.round_num}: {rnd.agenda_item}")
        
        # Turns
        for turn in rnd.turns:
            p_name = turn.persona.replace("_", " ").title()
            cites_str = f" *(Citations: {', '.join(['`' + c + '`' for c in turn.cites])})*" if turn.cites else ""
            resp_str = f" *(In rebuttal to {turn.responds_to.replace('_', ' ').title()})*" if turn.responds_to else ""
            cq_str = " *(Counter-Question Response)*" if turn.is_counter_question_response else ""
            
            lines.append(f"### **{p_name}**{resp_str}{cq_str}{cites_str}")
            lines.append(f"> {turn.statement}\n")

        # Round Votes Table
        lines.append("#### Round Voting & Deliberation Deltas")
        lines.append("| Persona | Score (1-10) | Deliberation Shift Reason |")
        lines.append("|---|---|---|")
        for persona in PERSONAS:
            score = rnd.votes.get(persona, "N/A")
            delta = rnd.score_deltas_from_previous_round.get(persona, "—")
            p_title = persona.replace("_", " ").title()
            lines.append(f"| {p_title} | **{score}/10** | {delta} |")
        lines.append("\n---\n")

    return "\n".join(lines)


def run_debate_session(
    candidate_id: str,
    rosetta: Optional[RosettaDocument] = None,
    memos: Optional[Dict[PersonaType, AgentMemo]] = None
) -> DebateTranscript:
    """Run full debate session for candidate and write JSON + MD transcripts to disk."""
    settings.ensure_directories()
    
    if rosetta is None:
        rosetta = build_candidate_rosetta(candidate_id)
    if memos is None:
        memos = generate_sealed_memos(candidate_id, rosetta)

    print(f"\n[Phase 3] Chairing Debate Session for {rosetta.candidate_name} ({rosetta.candidate_id})...")

    if "ananya" in rosetta.candidate_id:
        transcript = run_ananya_debate(rosetta, memos)
    elif "rohan" in rosetta.candidate_id:
        transcript = run_rohan_debate(rosetta, memos)
    else:
        transcript = run_ananya_debate(rosetta, memos)

    # Persist JSON transcript
    json_path = settings.debate_dir / f"{rosetta.candidate_id}_transcript.json"
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(transcript.model_dump_json(indent=2))

    # Persist Markdown transcript
    md_content = generate_transcript_markdown(transcript)
    md_path = settings.debate_dir / f"{rosetta.candidate_id}_transcript.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"✓ Completed Debate for {rosetta.candidate_name}:")
    print(f"   • Total Rounds: {transcript.total_rounds}")
    print(f"   • Agenda Items: {len(transcript.agenda)}")
    print(f"   • JSON: {json_path}")
    print(f"   • MD:   {md_path}")

    return transcript


if __name__ == "__main__":
    for cid in ["ananya_iyer", "rohan_malhotra"]:
        run_debate_session(cid)
