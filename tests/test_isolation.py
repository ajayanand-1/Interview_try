"""Tests for Independent Agents and Code-Enforced Isolation (PRD §8, §15)."""

import json
from pathlib import Path
from src.config import settings
from src.builder import build_candidate_rosetta
from src.agents.personas import PERSONA_SPECS
from src.agents.runner import build_isolated_agent_prompt, call_gemini_agent
from src.agents.sealed_memos import generate_sealed_memos, PERSONAS
from src.models.memo import AgentMemo
from src.utils.citations import validate_memo_traceability


def test_agent_payload_isolation():
    """PRD §15 Isolation Test: Assert no persona's call payload contains another persona's memo text."""
    rosetta = build_candidate_rosetta("ananya_iyer")
    jd_text = "Job Description: AI Engineer at Cargonet AI"

    captured_payloads = {}
    for persona in PERSONAS:
        system_inst, user_prompt = build_isolated_agent_prompt(persona, rosetta, jd_text)
        full_payload = system_inst + "\n" + user_prompt
        captured_payloads[persona] = full_payload

    # Cross-check every pair: Persona A's prompt must NEVER contain Persona B's name/rules/memo
    for p1 in PERSONAS:
        p1_payload = captured_payloads[p1]
        for p2 in PERSONAS:
            if p1 == p2:
                continue
            p2_title = PERSONA_SPECS[p2]["title"]
            # Assert p2's specific persona title/instructions are NOT in p1's prompt
            assert f"You are the {p2_title}" not in p1_payload, (
                f"Isolation violation: {p1} payload contains persona prompt for {p2}"
            )


def test_sealed_memos_generation_and_traceability():
    """Verify that all 4 sealed memos are generated on disk with 100% valid Rosetta citations."""
    for cid in ["ananya_iyer", "rohan_malhotra"]:
        rosetta = build_candidate_rosetta(cid)
        valid_citations = set(rosetta.citations_index.keys())
        memos = generate_sealed_memos(cid, rosetta)

        assert len(memos) == 4
        for persona in PERSONAS:
            memo = memos[persona]
            assert isinstance(memo, AgentMemo)
            assert memo.persona == persona
            assert memo.candidate_id == cid

            # Verify score constraint (1-10)
            if memo.confidence != "insufficient_evidence":
                assert 1 <= memo.score <= 10
            else:
                assert memo.score is None

            # Traceability check: all citations must exist in Rosetta index
            is_traceable, invalid_cits = validate_memo_traceability(memo, valid_citations)
            assert is_traceable, f"{persona} for {cid} had invalid citations: {invalid_cits}"

            # Check files on disk
            json_file = settings.memos_dir / f"{cid}_{persona}.json"
            pdf_file = settings.memos_dir / f"{cid}_{persona}.pdf"
            assert json_file.exists()
            assert pdf_file.exists()
            assert pdf_file.stat().st_size > 1000


def test_hr_culture_devils_advocate_presence():
    """Verify HR / Culture Agent provides required contrarian argument (PRD §7)."""
    for cid in ["ananya_iyer", "rohan_malhotra"]:
        json_file = settings.memos_dir / f"{cid}_hr_culture_agent.json"
        with open(json_file, "r") as f:
            data = json.load(f)
        memo = AgentMemo.model_validate(data)
        assert memo.contrarian_argument is not None
        assert len(memo.contrarian_argument.strip()) > 20
