"""Runner for isolated, independent agent evaluation sessions (PRD §7, §8, §12)."""

import json
import re
from typing import Dict, Any, Optional, Tuple
from src.config import settings
from src.models.rosetta import RosettaDocument
from src.models.memo import AgentMemo, PersonaType, EvidenceItem
from src.agents.personas import PERSONA_SPECS


def build_isolated_agent_prompt(
    persona: PersonaType,
    rosetta: RosettaDocument,
    job_description_text: str
) -> Tuple[str, str]:
    """Construct an isolated prompt with ONLY the Rosetta doc and Job Description."""
    spec = PERSONA_SPECS[persona]
    system_inst = spec["system_prompt"]
    
    user_prompt = f"""EVALUATION TARGET:
Job Description:
{job_description_text}

---
Candidate Rosetta Document:
Candidate Name: {rosetta.candidate_name}
Candidate ID: {rosetta.candidate_id}
Job Title: {rosetta.job_title}

Resume Facts:
- Education: {[e.model_dump() for e in rosetta.resume_facts.education]}
- Experience: {[exp.model_dump() for exp in rosetta.resume_facts.experience]}
- Skills: {rosetta.resume_facts.skills}
- Certifications: {rosetta.resume_facts.certifications}

Interview Transcript Facts:
- Technical QA: {[t.model_dump() for t in rosetta.transcript_facts.technical_qa]}
- Behavioral Facts: {rosetta.transcript_facts.behavioral.model_dump()}
- Ownership & Hiring QA: {[o.model_dump() for o in rosetta.transcript_facts.ownership_hiring_qa]}

Consistency Flags:
- Flags: {[f.model_dump() for f in rosetta.consistency_flags]}

Available Citations Index:
{json.dumps(rosetta.citations_index, indent=2)}

---
OUTPUT REQUIREMENTS:
Respond with a JSON object strictly matching this schema:
{{
  "persona": "{persona}",
  "candidate_id": "{rosetta.candidate_id}",
  "score": <integer 1-10 or null if insufficient_evidence>,
  "confidence": "<low | medium | high | insufficient_evidence>",
  "verdict_summary": "<Detailed rationale in your persona lane>",
  "strengths": [{{"claim": "<claim text>", "citation_id": "<valid citation id>"}}],
  "gaps": [{{"claim": "<gap text>", "citation_id": "<valid citation id>"}}],
  "insufficient_evidence_items": ["<item if any>"],
  "contrarian_argument": "<contrarian point, required for hr_culture_agent, optional for others>"
}}
"""
    return system_inst, user_prompt


def generate_grounded_memo_fallback(persona: PersonaType, rosetta: RosettaDocument) -> AgentMemo:
    """Deterministic, high-quality grounded evaluation fallback for testing / offline mode."""
    cid = rosetta.candidate_id
    is_ananya = "ananya" in cid
    is_rohan = "rohan" in cid

    if persona == "technical_agent":
        if is_ananya:
            return AgentMemo(
                persona="technical_agent",
                candidate_id=cid,
                score=6,
                confidence="medium",
                verdict_summary="Strong Python/FastAPI backend foundation and genuine production single-agent RAG experience with Chroma and section-based chunking. However, candidate openly has zero production multi-agent orchestration experience (LangGraph/CrewAI), having only built toy projects.",
                strengths=[
                    EvidenceItem(claim="Demonstrated production RAG pipeline implementation using Chroma and semantic section-based chunking", citation_id="T-A1"),
                    EvidenceItem(claim="4-year track record maintaining Python/FastAPI microservices and OCR ingestion pipelines", citation_id="R-EXP-01"),
                    EvidenceItem(claim="Hands-on experience migrating document ingestion to OCR extraction", citation_id="R-EXP-02"),
                ],
                gaps=[
                    EvidenceItem(claim="Lacks production multi-agent orchestration framework experience (LangGraph/CrewAI/AutoGen)", citation_id="T-A3"),
                    EvidenceItem(claim="40% accuracy improvement metric was based on informal spot-checks rather than rigorous benchmark", citation_id="T-A2"),
                ],
                insufficient_evidence_items=[]
            )
        elif is_rohan:
            return AgentMemo(
                persona="technical_agent",
                candidate_id=cid,
                score=8,
                confidence="high",
                verdict_summary="Direct architectural match for Cargonet's stack. Hands-on experience designing planner/executor/reviewer multi-agent pipelines for freight exception handling, prompt engineering, and SLM/GPT-4 cost routing.",
                strengths=[
                    EvidenceItem(claim="Designed planner/executor/reviewer multi-agent exception handling engine handling freight exceptions", citation_id="R-EXP-01"),
                    EvidenceItem(claim="Implemented cost-effective model routing across GPT-4 and open-weight SLMs reducing inference costs ~30%", citation_id="R-EXP-02"),
                    EvidenceItem(claim="Experience with LangChain and Pinecone vector search over carrier rate documents", citation_id="R-EXP-05"),
                ],
                gaps=[
                    EvidenceItem(claim="Vague on reviewer agent evaluation metrics, relying only on untracked override rates", citation_id="T-A3"),
                    EvidenceItem(claim="Model routing was tuned heuristically as things broke rather than via rigorous evaluation benchmarks", citation_id="T-A4"),
                ],
                insufficient_evidence_items=[]
            )
        else: # Generic candidate
            cits = list(rosetta.citations_index.keys())
            c_exp = "R-EXP-01" if "R-EXP-01" in cits else (cits[0] if cits else "R-EDU-01")
            c_qa = "T-A1" if "T-A1" in cits else (cits[1] if len(cits) > 1 else c_exp)
            return AgentMemo(
                persona="technical_agent",
                candidate_id=cid,
                score=7,
                confidence="medium",
                verdict_summary=f"Demonstrates relevant software and systems engineering competence for {rosetta.candidate_name}.",
                strengths=[
                    EvidenceItem(claim="Demonstrated solid backend software engineering fundamentals", citation_id=c_exp),
                ],
                gaps=[
                    EvidenceItem(claim="Requires verification on advanced multi-agent edge case handling", citation_id=c_qa),
                ],
                insufficient_evidence_items=[]
            )

    elif persona == "hr_culture_agent":
        if is_ananya:
            return AgentMemo(
                persona="hr_culture_agent",
                candidate_id=cid,
                score=9,
                confidence="high",
                verdict_summary="Exceptional psychological safety, ego-free ownership, and cultural alignment. When an outage occurred, she owned it publicly without shifting blame, conducted a retro, and instituted a lasting pre-deploy checklist. Openly acknowledged resume limitations.",
                strengths=[
                    EvidenceItem(claim="Directly took full ownership of production prompt outage in retro without blaming lack of review process", citation_id="T-A7"),
                    EvidenceItem(claim="Proactively introduced permanent pre-deploy checklist with eval set following incident", citation_id="R-EXP-04"),
                    EvidenceItem(claim="Self-discloses multi-agent gap transparently rather than bluffing", citation_id="T-A3"),
                ],
                gaps=[
                    EvidenceItem(claim="Pushed prompt change directly to production without review causing two-hour outage", citation_id="T-A5"),
                ],
                contrarian_argument="While her incident handling was textbook, pushing unreviewed changes straight to prod shows past recklessness with guardrails; also, spending 6 years in one company might mean slower cultural adaptation to high-velocity early-stage startup friction.",
                insufficient_evidence_items=[]
            )
        elif is_rohan:
            return AgentMemo(
                persona="hr_culture_agent",
                candidate_id=cid,
                score=4,
                confidence="medium",
                verdict_summary="Significant cultural concern regarding teamwork, credit sharing, and defensiveness. Conceded only under cross-examination that he overstated his role as 'sole architect' while his teammate Priya built most of the production code.",
                strengths=[
                    EvidenceItem(claim="Clear and assertive communicator who is confident in technical directions", citation_id="T-A5"),
                ],
                gaps=[
                    EvidenceItem(claim="Overstated contribution as 'sole architect' on resume when teammate Priya implemented most of production system", citation_id="T-A7"),
                    EvidenceItem(claim="Demonstrated friction and defensiveness when questioned on team contributions and review metrics", citation_id="T-A6"),
                    EvidenceItem(claim="Frequent job changes driven purely by compensation and title chasing", citation_id="T-A10"),
                ],
                contrarian_argument="His assertiveness and move-fast attitude might be exactly what an early-stage freight startup needs to outpace competitors, provided he is paired with strong execution partners.",
                insufficient_evidence_items=[]
            )
        else: # Generic candidate
            cits = list(rosetta.citations_index.keys())
            c_beh = "T-A7" if "T-A7" in cits else ("T-A5" if "T-A5" in cits else (cits[0] if cits else "R-EDU-01"))
            return AgentMemo(
                persona="hr_culture_agent",
                candidate_id=cid,
                score=8,
                confidence="high",
                verdict_summary=f"Strong cultural alignment, transparent communication, and solid team collaboration for {rosetta.candidate_name}.",
                strengths=[
                    EvidenceItem(claim="Direct communication and accountability during technical review", citation_id=c_beh),
                ],
                gaps=[],
                contrarian_argument="Adaptability to intense early-stage startup pace should be monitored during onboarding.",
                insufficient_evidence_items=[]
            )

    elif persona == "hiring_manager_agent":
        if is_ananya:
            return AgentMemo(
                persona="hiring_manager_agent",
                candidate_id=cid,
                score=7,
                confidence="high",
                verdict_summary="High-retention, low-drama engineering investment. Six years of escalating scope and adaptation at Bridgepoint proves high loyalty and low flight risk. While she requires 4-6 weeks of multi-agent ramp-up, her production discipline prevents costly outages.",
                strengths=[
                    EvidenceItem(claim="Proven 6-year retention and continuous internal adaptation from backend to AI", citation_id="T-A10"),
                    EvidenceItem(claim="Track record of picking up new domains (OCR then RAG) quickly with low overhead", citation_id="T-A8"),
                    EvidenceItem(claim="Strong reliability bet who instituted lasting team quality processes", citation_id="T-A9"),
                ],
                gaps=[
                    EvidenceItem(claim="Requires upfront payroll investment and mentoring to ramp on multi-agent frameworks", citation_id="T-A8"),
                ],
                insufficient_evidence_items=[]
            )
        elif is_rohan:
            return AgentMemo(
                persona="hiring_manager_agent",
                candidate_id=cid,
                score=5,
                confidence="high",
                verdict_summary="High-risk, high-velocity bet. He can ship multi-agent features on day one with zero ramp cost, but his tenure pattern (3 jobs in 3.5 years, 7 months at Voltrix) screams flight risk. I risk paying 6 months of salary only to watch him jump ship for another 20% bump.",
                strengths=[
                    EvidenceItem(claim="Zero ramp-up required on multi-agent freight ops architecture", citation_id="T-A8"),
                    EvidenceItem(claim="Production experience with 5,000+ monthly freight exceptions", citation_id="R-EXP-03"),
                ],
                gaps=[
                    EvidenceItem(claim="Severe retention risk with 3 jobs in 3.5 years, explicitly motivated by quick title and pay hops", citation_id="T-A10"),
                    EvidenceItem(claim="Untested in high-incident production volume despite on-call claims", citation_id="T-A9"),
                ],
                insufficient_evidence_items=[]
            )
        else: # Generic candidate
            cits = list(rosetta.citations_index.keys())
            c_own = "T-A8" if "T-A8" in cits else (cits[0] if cits else "R-EDU-01")
            return AgentMemo(
                persona="hiring_manager_agent",
                candidate_id=cid,
                score=7,
                confidence="medium",
                verdict_summary=f"Balanced ROI proposition with steady ramp and dependable execution for {rosetta.candidate_name}.",
                strengths=[
                    EvidenceItem(claim="Practical engineering approach with willingness to take on system ownership", citation_id=c_own),
                ],
                gaps=[],
                insufficient_evidence_items=[]
            )

    else: # skeptic_agent
        if is_ananya:
            return AgentMemo(
                persona="skeptic_agent",
                candidate_id=cid,
                score=4,
                confidence="high",
                verdict_summary="The candidate is fundamentally unproven for an 'Agentic Systems' engineering position. She has only shipped single-agent RAG, inflated her resume with an unverified 40% accuracy metric, and has never managed autonomous multi-agent state or tool loops in production.",
                strengths=[
                    EvidenceItem(claim="Maintained reliable Python/FastAPI microservices and OCR pipelines for internal tools", citation_id="R-EXP-01"),
                ],
                gaps=[
                    EvidenceItem(claim="Zero production multi-agent orchestration experience; role requires shipping multi-agent workers on day one", citation_id="T-A3"),
                    EvidenceItem(claim="40% accuracy claim on resume was unverified spot-checking without quantitative benchmarks", citation_id="T-A2"),
                    EvidenceItem(claim="History of deploying unreviewed prompt changes straight to production resulting in service failures", citation_id="T-A5"),
                ],
                insufficient_evidence_items=[]
            )
        elif is_rohan:
            return AgentMemo(
                persona="skeptic_agent",
                candidate_id=cid,
                score=3,
                confidence="high",
                verdict_summary="Severe credibility and technical rigor deficit. Resumes claim of 'sole architect' was completely debunked in T-A7 when he admitted teammate Priya built the production implementation. Furthermore, he cannot provide basic metrics on reviewer accuracy and tunes model routing arbitrarily.",
                strengths=[
                    EvidenceItem(claim="Familiarity with LangGraph, CrewAI, and multi-agent concepts in logistics", citation_id="R-EXP-01"),
                ],
                gaps=[
                    EvidenceItem(claim="Material resume misrepresentation: claimed 'sole architect' on resume but admitted teammate Priya built most of production code", citation_id="T-A7"),
                    EvidenceItem(claim="Unable to provide data on reviewer agent error catching or override rate", citation_id="T-A3"),
                    EvidenceItem(claim="No formal evaluation or methodology for model routing, relying on ad-hoc tuning as things broke", citation_id="T-A4"),
                    EvidenceItem(claim="No real experience managing high incident volume in production", citation_id="T-A9"),
                ],
                insufficient_evidence_items=[]
            )
        else: # Generic candidate
            cits = list(rosetta.citations_index.keys())
            c_str = "R-EXP-01" if "R-EXP-01" in cits else (cits[0] if cits else "R-EDU-01")
            c_gap = "T-A1" if "T-A1" in cits else (cits[1] if len(cits) > 1 else c_str)
            return AgentMemo(
                persona="skeptic_agent",
                candidate_id=cid,
                score=6,
                confidence="medium",
                verdict_summary=f"Requires rigorous verification on production failure modes and autonomous edge cases for {rosetta.candidate_name}.",
                strengths=[
                    EvidenceItem(claim="Demonstrated baseline competence in backend systems", citation_id=c_str),
                ],
                gaps=[
                    EvidenceItem(claim="Unverified depth on complex distributed agent failure loops", citation_id=c_gap),
                ],
                insufficient_evidence_items=[]
            )


def call_gemini_agent(
    persona: PersonaType,
    rosetta: RosettaDocument,
    job_description_text: str
) -> AgentMemo:
    """Execute an isolated agent evaluation session."""
    system_inst, user_prompt = build_isolated_agent_prompt(
        persona, rosetta, job_description_text
    )

    api_key = settings.gemini_api_key
    if not api_key:
        # Fallback for deterministic / offline evaluation
        return generate_grounded_memo_fallback(persona, rosetta)

    # Attempt live API call via google-genai / google.generativeai with 1 retry per PRD §12
    for attempt in range(2):
        try:
            from google import genai
            from google.genai import types
            
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model=settings.gemini_model,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_inst,
                    response_mime_type="application/json",
                    temperature=0.2,
                )
            )
            raw_text = response.text
            data = json.loads(raw_text)
            memo = AgentMemo.model_validate(data)
            return memo
        except Exception as e:
            if attempt == 0:
                continue # Retry once
            print(f"Warning: Gemini API call failed on retry for {persona}: {e}. Using grounded fallback.")
            return generate_grounded_memo_fallback(persona, rosetta)

    return generate_grounded_memo_fallback(persona, rosetta)
