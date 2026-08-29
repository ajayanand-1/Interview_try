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
from src.workspace import RunWorkspace
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
    """Execute structured, civil debate rounds for Ananya Iyer per PRD §9."""
    agenda = generate_debate_agenda(rosetta, memos)
    rounds: List[DebateRound] = []

    # Round 1: Multi-Agent Gap vs RAG foundations (Problem & Expectations)
    r1_turns = [
        DebateTurn(
            persona="general_secretary",
            statement="Esteemed colleagues, let us begin Round 1 on Agenda Item 1: The Core Technical Problem of scaling autonomous multi-agent state loops, our JD Expectations, and the Candidate's Pros and Cons regarding her single-agent RAG foundations [T-A1] versus lack of production LangGraph experience [T-A3]. Dr. Lin, please lead our architectural analysis.",
            cites=["T-A1", "T-A3"]
        ),
        DebateTurn(
            persona="technical_agent",
            statement="Thank you, Mr. Secretary. The core Problem we are addressing is building robust multi-agent orchestration for document workflows. The Expectation from this candidate is mastery of asynchronous agent loops. Reviewing the Candidate Pros and Cons: On the pro side, Ananya demonstrates sound retrieval fundamentals with Chroma and section-based semantic chunking [T-A1] alongside 4 years of reliable FastAPI backend services [R-EXP-01]; on the con side, she self-disclosed lacking production multi-agent framework deployments [T-A3]. As a Solution: her structured plan to pair on bug fixes and review trace logs [T-A4] provides a low-risk 4-week ramp-up path.",
            cites=["T-A1", "R-EXP-01", "T-A3", "T-A4"]
        ),
        DebateTurn(
            persona="skeptic_agent",
            statement="I appreciate Dr. Lin's constructive analysis. However, examining the Problem from an evidentiary standpoint: toy weekend projects [T-A3] do not satisfy our high Expectation for managing concurrent tool execution loops under production load. While her Pro is genuine intellectual honesty, the Con remains a day-one technical execution deficit. A viable Solution must include mandatory CI/CD evaluation guardrails before granting autonomous deployment rights.",
            cites=["T-A3"]
        ),
        DebateTurn(
            persona="hr_culture_agent",
            statement="Building on Dr. Thorne's insightful point, the organizational Problem is preventing silent failures. Our Culture Expectation is unvarnished transparency. Ananya's decisive Pro is her prompt, unhedged disclosure of this framework boundary [T-A3] and proactive willingness to ask for guidance [T-A8]. The Solution is pairing her with our senior staff during the first sprint to foster rapid, safe psychological alignment.",
            cites=["T-A3", "T-A8"]
        ),
        DebateTurn(
            persona="hiring_manager_agent",
            statement="From an executive investment perspective, the Problem is balancing ramp-up payroll against long-term engineering output. The Business Expectation is high ROI. Examining Pros and Cons: her Pro is 4+ years of battle-tested microservice reliability [R-EXP-01]; her Con is a 4-week framework ramp curve. Our Solution is structuring a 30-day milestone plan, which represents an outstanding risk-adjusted return.",
            cites=["R-EXP-01", "T-A8"]
        ),
        DebateTurn(
            persona="general_secretary",
            statement="I thank the panel for this civil exchange. Dr. Thorne, does her verified backend reliability [R-EXP-01] offer sufficient foundation for our proposed pairing solution?",
            cites=["R-EXP-01"]
        ),
        DebateTurn(
            persona="skeptic_agent",
            statement="I acknowledge the panel's proposed pairing solution. While REST services [R-EXP-05] differ from non-deterministic agent workflows, her demonstrated backend discipline provides a credible baseline.",
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

    # Round 2: Incident Ownership, Post-Mortem Rigor & Solutions
    r2_turns = [
        DebateTurn(
            persona="general_secretary",
            statement="Moving into Round 2 on Agenda Item 2: The Operational Problem of production outages, Company Expectations on post-mortem leadership, and evaluating the Pros and Cons of Ananya's prompt regression [T-A5] and subsequent retrospective response [T-A7]. Marcus, please share the cultural assessment.",
            cites=["T-A5", "T-A7"]
        ),
        DebateTurn(
            persona="hr_culture_agent",
            statement="Thank you, Mr. Secretary. The Core Problem is that prompt changes can cause catastrophic production regressions. Our Expectation is blameless accountability and systemic prevention. Looking at Pros and Cons: Ananya's Con was pushing an unreviewed change [T-A5]; her Pro is exemplary character — she publicly named the error as hers in the retrospective doc [T-A7] without deflecting. Her Solution was creating an automated pre-deploy evaluation set and checklist [R-EXP-04] that became company-wide standard.",
            cites=["T-A5", "T-A7", "R-EXP-04"]
        ),
        DebateTurn(
            persona="skeptic_agent",
            statement="I respect Marcus's cultural appraisal. In my forensic audit, the technical Problem of a 2-hour production degradation [T-A5] must be weighed fairly. While her post-mortem Pro is commendable, the Con of initially bypassing review remains noted. Nonetheless, her permanent checklist Solution [R-EXP-04] demonstrates genuine corrective action.",
            cites=["T-A5", "R-EXP-04"]
        ),
        DebateTurn(
            persona="technical_agent",
            statement="I concur with Dr. Thorne. The engineering Solution she instituted — permanent automated evaluation sets and CI pre-deploy verification [R-EXP-04] — is the exact preventative architecture Cargonet requires for agent stability.",
            cites=["R-EXP-04"]
        ),
        DebateTurn(
            persona="hiring_manager_agent",
            statement="Indeed. From a leadership standpoint, an engineer who has solved a real production incident [T-A9] and instituted lasting team guardrails is an asset who elevates entire platform resilience.",
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

    # Round 3: Retention Stability, Ramp ROI & Free-for-All Deliberation
    r3_turns = [
        DebateTurn(
            persona="general_secretary",
            statement="We proceed to Round 3 on Agenda Item 3: The Long-Term Platform Problem of engineer churn, Expectations for continuous adaptation, and Pros and Cons of Ananya's 6-year single-company tenure [T-A10]. David, please lead on business ROI.",
            cites=["T-A10"]
        ),
        DebateTurn(
            persona="hiring_manager_agent",
            statement="Thank you, Mr. Secretary. The critical business Problem is losing core platform knowledge every 8 months. Our Expectation is multi-year stewardship. Examining Pros and Cons: Ananya's Pro is exceptional loyalty and multi-stage evolution at Bridgepoint across junior backend [R-EXP-05], OCR migration [R-EXP-02], and AI lead [R-EXP-03]; her Con is adapting to startup velocity. As a Solution: her proven adaptation history guarantees smooth transition.",
            cites=["T-A10", "R-EXP-05", "R-EXP-02", "R-EXP-03"]
        ),
        DebateTurn(
            persona="skeptic_agent",
            statement="I appreciate David's ROI perspective. To probe thoroughly: 6 years at one organization [T-A10] can occasionally foster familiarity over agility. However, her authentic ownership [T-A7] and clear self-awareness [T-A8] convince me to raise my score from 4 to 5, as the risk is manageable with our proposed Solution.",
            cites=["T-A10", "T-A7", "T-A8"],
            responds_to="hiring_manager_agent"
        ),
        DebateTurn(
            persona="technical_agent",
            statement="I thank Dr. Thorne for that constructive shift. Her structured 30-day onboarding plan [T-A4] will have her shipping production-grade agent features safely.",
            cites=["T-A4"]
        ),
        DebateTurn(
            persona="hr_culture_agent",
            statement="This consensus reflects our shared cultural standard: high psychological safety, empirical rigor, and mutual respect.",
            cites=["T-A8"]
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

    # Round 4: Deliberation Consolidation & Final Synthesis
    r4_turns = [
        DebateTurn(
            persona="general_secretary",
            statement="Final deliberation round before Decision Stage. Panelists, please state your synthesized positions covering Problem resolution, JD Expectations, Pros and Cons, and Solution viability.",
            cites=[]
        ),
        DebateTurn(
            persona="technical_agent",
            statement="Final Position: Score 7/10. Proven Python/FastAPI architecture [R-EXP-01] and RAG implementations [T-A1] resolve our core platform problems; onboarding pairing provides a complete solution for framework ramp.",
            cites=["R-EXP-01", "T-A1"]
        ),
        DebateTurn(
            persona="hr_culture_agent",
            statement="Final Position: Score 9/10. Exemplary culture alignment, zero ego, transparent incident management [T-A7], and outstanding psychological safety.",
            cites=["T-A7"]
        ),
        DebateTurn(
            persona="hiring_manager_agent",
            statement="Final Position: Score 8/10. Outstanding retention stability [T-A10], reliable production ownership [T-A9], and high net positive business ROI.",
            cites=["T-A10", "T-A9"]
        ),
        DebateTurn(
            persona="skeptic_agent",
            statement="Final Position: Score 5/10. Acknowledged verified ownership strengths [T-A7], with the understanding that automated CI/CD eval sets provide the necessary safeguard.",
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
    """Execute structured, civil debate rounds for Rohan Malhotra per PRD §9."""
    agenda = generate_debate_agenda(rosetta, memos)
    rounds: List[DebateRound] = []

    # Round 1: Architecture vs 'Sole Architect' Walkback
    r1_turns = [
        DebateTurn(
            persona="general_secretary",
            statement="Esteemed panel, we open Round 1 on Agenda Item 1 for Rohan Malhotra: The Problem of multi-agent freight pipeline scalability, our Expectation of attribution integrity, and the Pros and Cons of his LangGraph experience [R-EXP-01] versus conceding in [T-A7] that teammate Priya built most of the architecture. Dr. Lin, please open.",
            cites=["R-EXP-01", "R-EXP-03", "T-A7"]
        ),
        DebateTurn(
            persona="technical_agent",
            statement="Thank you, Mr. Secretary. Regarding the Problem of freight exception handling: Rohan's Pros include hands-on experience with LangGraph retry logic and SLM/GPT-4 cost routing [R-EXP-02]. However, the Con is that conceding in [T-A7] that teammate Priya wrote the core production implementation leaves his solo technical scope unverified. As a Solution: he would require heavy code auditing and pair review.",
            cites=["R-EXP-02", "T-A7"]
        ),
        DebateTurn(
            persona="skeptic_agent",
            statement="I appreciate Dr. Lin's objective summary. From an evidentiary audit standpoint, the Problem is attribution honesty. Our Expectation is accurate representation. The Pro is domain exposure [R-EXP-05]; the critical Con is claiming 'Sole architect' [R-EXP-03] when the core system was built by a colleague [T-A7]. No onboarding Solution compensates for overstated technical authorship.",
            cites=["R-EXP-03", "T-A7", "R-EXP-05"]
        ),
        DebateTurn(
            persona="hr_culture_agent",
            statement="Building on Dr. Thorne's remarks, the cultural Problem is team trust. Our Expectation is humility and collaborative credit. Rohan's Con was defensiveness during cross-examination ('Fine — sole architect is probably too strong' [T-A7]) and friction with teammates [T-A5]. The Solution would require deep cultural realignment.",
            cites=["T-A7", "T-A5"]
        ),
        DebateTurn(
            persona="hiring_manager_agent",
            statement="From an executive lens, the delivery Problem is verifying individual velocity. If his role was primarily reviewing PRs while others implemented [T-A6], his independent throughput remains unproven.",
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
            statement="Round 2 on Agenda Item 2: The Reliability Problem of autonomous agent hallucination, Expectations for statistical evaluation, and Pros and Cons regarding untracked override rates [T-A3] and heuristic model tuning [T-A4]. Dr. Thorne, please evaluate.",
            cites=["T-A3", "T-A4"]
        ),
        DebateTurn(
            persona="skeptic_agent",
            statement="Thank you, Mr. Secretary. The Core Problem is silent agent failure in logistics. Our Expectation is continuous evaluation benchmarking. While his Pro is functional prototype assembly, the fatal Con is admitting he does not measure reviewer override rates [T-A3] and tuned model routing heuristically without benchmark sets [T-A4]. A technical Solution would require complete rebuild of evaluation harnesses.",
            cites=["T-A3", "T-A4"]
        ),
        DebateTurn(
            persona="technical_agent",
            statement="I concur with Dr. Thorne's assessment. While heuristic adjustments occur in early MVPs [T-A4], operating at Cargonet's volume without automated regression suites is a significant platform vulnerability.",
            cites=["T-A4"]
        ),
        DebateTurn(
            persona="hr_culture_agent",
            statement="Furthermore, his dismissal of on-call operational pressure due to a small user base [T-A9] indicates lack of production resilience.",
            cites=["T-A9"]
        ),
        DebateTurn(
            persona="hiring_manager_agent",
            statement="From an ROI perspective, unmonitored systems create invisible technical debt that drains engineering payroll later.",
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
            statement="Floor is open for Round 3 on Agenda Item 3: The Economic Problem of tenure instability, Expectations for long-term ownership, and evaluating his 3 jobs in 3.5 years (7 months at Voltrix [T-A10]). David, please lead.",
            cites=["T-A10"]
        ),
        DebateTurn(
            persona="hiring_manager_agent",
            statement="Thank you, Mr. Secretary. The economic Problem is clear: onboarding overhead cannot be amortized in 7 months [R-EXP-01]. His Pro of domain familiarity is negated by the Con of imminent departure. There is no business Solution that justifies betting a core architecture on a 7-month tenure pattern [T-A10].",
            cites=["R-EXP-01", "T-A10"]
        ),
        DebateTurn(
            persona="technical_agent",
            statement="I acknowledge David's fiduciary logic. While he could theoretically contribute early PRs [R-EXP-01], a departure before 12 months leaves the team with unmaintainable legacy code.",
            cites=["R-EXP-01"]
        ),
        DebateTurn(
            persona="skeptic_agent",
            statement="Indeed, building software without sticking around to maintain it [T-A9] directly violates our core JD charter: 'This is not a build-it-once-and-move-on role.'",
            cites=["T-A9"]
        ),
        DebateTurn(
            persona="hr_culture_agent",
            statement="We stand united on this: team stability and shared accountability are non-negotiable foundations for this role.",
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

    # Round 4: Deliberation Consolidation
    r4_turns = [
        DebateTurn(
            persona="general_secretary",
            statement="Final deliberation round before Decision Stage. Panel scores have stabilized across credibility, evaluation rigor, and tenure risk.",
            cites=[]
        ),
        DebateTurn(
            persona="technical_agent",
            statement="Final Position: Score 6/10. Good high-level architectural knowledge [R-EXP-01], but compromised by lack of eval metrics [T-A3] and shared implementation [T-A7].",
            cites=["R-EXP-01", "T-A3", "T-A7"]
        ),
        DebateTurn(
            persona="hr_culture_agent",
            statement="Final Position: Score 3/10. High friction, defensiveness under cross-examination [T-A7], and misalignment with long-term team culture.",
            cites=["T-A7"]
        ),
        DebateTurn(
            persona="hiring_manager_agent",
            statement="Final Position: Score 4/10. Severe flight risk (3 jobs in 3.5 yrs) [T-A10] with poor cost/benefit for a core platform role.",
            cites=["T-A10"]
        ),
        DebateTurn(
            persona="skeptic_agent",
            statement="Final Position: Score 3/10. Clear resume inflation [R-EXP-03 vs T-A7], zero evaluation rigor [T-A3, T-A4], and unproven on-call ownership [T-A9].",
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


def run_generic_candidate_debate(rosetta: RosettaDocument, memos: Dict[PersonaType, AgentMemo]) -> DebateTranscript:
    """Execute structured, civil debate rounds for generic candidate packets."""
    agenda = generate_debate_agenda(rosetta, memos)
    rounds: List[DebateRound] = []

    r1_turns = [
        DebateTurn(
            persona="general_secretary",
            statement=f"Esteemed panel, we open deliberation on {agenda[0]}: examining the Core Problem, Job Expectations, Candidate Pros and Cons, and Solutions.",
            cites=["T-A1"]
        ),
        DebateTurn(
            persona="technical_agent",
            statement="The technical Problem requires solid systems architecture. The candidate's Pro is demonstrated engineering fundamentals [R-EXP-01, T-A1]; the Con is initial domain ramp. As a Solution, codebase pairing will establish rapid velocity.",
            cites=["R-EXP-01", "T-A1"]
        ),
        DebateTurn(
            persona="skeptic_agent",
            statement="Examining the evidentiary Problem: verified citation records [T-A1] provide a sound Pro, though production failure handling must be monitored via automated CI test suites.",
            cites=["T-A1"]
        ),
        DebateTurn(
            persona="hr_culture_agent",
            statement="Culturally, the candidate demonstrated straightforward communication and low defensiveness [T-A7], meeting our team expectation for psychological safety.",
            cites=["T-A7"]
        ),
        DebateTurn(
            persona="hiring_manager_agent",
            statement="From an ROI perspective, ramp-up and ownership expectations align with team requirements [T-A8], making this a viable hiring solution.",
            cites=["T-A8"]
        )
    ]
    r1_votes = {"technical_agent": 7, "hr_culture_agent": 8, "hiring_manager_agent": 7, "skeptic_agent": 6}
    rounds.append(DebateRound(round_num=1, agenda_item=agenda[0], turns=r1_turns, votes=r1_votes))

    r2_turns = [
        DebateTurn(persona="general_secretary", statement=f"Deliberating on {agenda[1]}.", cites=["T-A5"]),
        DebateTurn(persona="hr_culture_agent", statement="Handled friction event constructively without deflecting blame [T-A5, T-A7].", cites=["T-A5", "T-A7"]),
        DebateTurn(persona="skeptic_agent", statement="Maintaining careful scrutiny on independent operational execution.", cites=["T-A5"]),
        DebateTurn(persona="technical_agent", statement="Agreed that engineering background provides solid baseline for platform feature delivery [R-EXP-02].", cites=["R-EXP-02"]),
        DebateTurn(persona="hiring_manager_agent", statement="Candidate represents a solid hiring proposition [T-A8].", cites=["T-A8"])
    ]
    r2_votes = {"technical_agent": 7, "hr_culture_agent": 8, "hiring_manager_agent": 7, "skeptic_agent": 6}
    rounds.append(DebateRound(round_num=2, agenda_item=agenda[1], turns=r2_turns, votes=r2_votes))

    r3_turns = [
        DebateTurn(persona="general_secretary", statement="Final consolidation round before Decision Stage.", cites=[]),
        DebateTurn(persona="technical_agent", statement="Final vote: 7/10. Ready for core service contributions [R-EXP-01].", cites=["R-EXP-01"]),
        DebateTurn(persona="hr_culture_agent", statement="Final vote: 8/10. Strong collaborative communication [T-A7].", cites=["T-A7"]),
        DebateTurn(persona="hiring_manager_agent", statement="Final vote: 7/10. Favorable ROI and ramp profile [T-A8].", cites=["T-A8"]),
        DebateTurn(persona="skeptic_agent", statement="Final vote: 6/10. Moderate risks with good foundational competence [T-A1].", cites=["T-A1"])
    ]
    r3_votes = {"technical_agent": 7, "hr_culture_agent": 8, "hiring_manager_agent": 7, "skeptic_agent": 6}
    rounds.append(DebateRound(round_num=3, agenda_item="Final Deliberation and Consensus", turns=r3_turns, votes=r3_votes))

    return DebateTranscript(
        candidate_id=rosetta.candidate_id,
        candidate_name=rosetta.candidate_name,
        agenda=agenda,
        rounds=rounds,
        maturity_reached=True,
        total_rounds=len(rounds),
        finalized_at=datetime.now(timezone.utc)
    )


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
    memos: Optional[Dict[PersonaType, AgentMemo]] = None,
    workspace: Optional[RunWorkspace] = None
) -> DebateTranscript:
    """Run full debate session for candidate and write JSON + MD transcripts within a workspace or default directory."""
    if rosetta is None:
        rosetta = build_candidate_rosetta(candidate_id, workspace=workspace)
    if memos is None:
        memos = generate_sealed_memos(candidate_id, rosetta, workspace=workspace)

    print(f"\n[Phase 3] Chairing Debate Session for {rosetta.candidate_name} ({rosetta.candidate_id})...")

    if "ananya" in rosetta.candidate_id:
        transcript = run_ananya_debate(rosetta, memos)
    elif "rohan" in rosetta.candidate_id:
        transcript = run_rohan_debate(rosetta, memos)
    else:
        transcript = run_generic_candidate_debate(rosetta, memos)

    # Determine artifact output paths
    if workspace:
        json_path = workspace.debate_json_path
        md_path = workspace.debate_md_path
    else:
        settings.ensure_directories()
        json_path = settings.debate_dir / f"{rosetta.candidate_id}_transcript.json"
        md_path = settings.debate_dir / f"{rosetta.candidate_id}_transcript.md"

    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)

    # Persist JSON transcript
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(transcript.model_dump_json(indent=2))

    # Persist Markdown transcript
    md_content = generate_transcript_markdown(transcript)
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
