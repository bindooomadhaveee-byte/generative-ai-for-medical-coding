"""Generative AI for Medical Coding - core logic.

Pipeline:
 1. Retrieve candidate ICD-10 codes from a reference set (keyword retrieval).
 2. Ask the LLM to assign codes to the clinical note, grounded in candidates.
 3. Validate returned codes against the reference set and flag unknown ones.
"""
import json
import os
import re

import anthropic

from icd10_sample import ICD10_SAMPLE

MODEL = "claude-sonnet-5-5"
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are an expert medical coder (ICD-10-CM).
Given a clinical note, assign the most appropriate diagnosis codes.
Rules:
- Prefer codes from the CANDIDATE list; only suggest others if clearly needed.
- Code only conditions documented in the note. Never infer undocumented diagnoses.
- Give a short evidence quote from the note for each code.
Respond with ONLY JSON in this format:
{"codes":[{"code":"I10","description":"...","evidence":"...","confidence":0.0-1.0}]}"""


def retrieve_candidates(note: str, top_k: int = 12) -> dict:
    """Simple keyword-overlap retrieval over code descriptions."""
    words = set(re.findall(r"[a-z]{4,}", note.lower()))
    scored = []
    for code, desc in ICD10_SAMPLE.items():
        desc_words = set(re.findall(r"[a-z]{4,}", desc.lower()))
        score = len(words & desc_words)
        if score:
            scored.append((score, code))
    scored.sort(reverse=True)
    return {c: ICD10_SAMPLE[c] for _, c in scored[:top_k]}


def suggest_codes(note: str) -> list[dict]:
    candidates = retrieve_candidates(note)
    cand_text = "\n".join(f"{c}: {d}" for c, d in candidates.items()) or "(none found)"
    user_msg = f"CLINICAL NOTE:\n{note}\n\nCANDIDATE CODES:\n{cand_text}"

    resp = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )
    text = resp.content[0].text
    text = re.sub(r"```json|```", "", text).strip()
    codes = json.loads(text).get("codes", [])

    # Validation step: flag codes not found in the reference set
    for item in codes:
        item["verified"] = item["code"] in ICD10_SAMPLE
    return codes


if __name__ == "__main__":
    sample = (
        "58-year-old male with long-standing type 2 diabetes and hypertension "
        "presents with fever and productive cough. Chest X-ray shows pneumonia. "
        "BP 150/95. Continue metformin and lisinopril."
    )
    for r in suggest_codes(sample):
        flag = "OK " if r["verified"] else "?? "
        print(f"{flag}{r['code']:<8} {r['description']}  (conf {r['confidence']})")
        print(f"      evidence: {r['evidence']}")
