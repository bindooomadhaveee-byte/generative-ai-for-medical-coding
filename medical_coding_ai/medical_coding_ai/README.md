# Generative AI for Medical Coding (base project)

Suggests ICD-10 codes from a clinical note using an LLM, grounded by a retrieval step and validated against a code list.

## Setup
    pip install -r requirements.txt
    export ANTHROPIC_API_KEY="your_key"      # Windows: set ANTHROPIC_API_KEY=your_key

## Run
    python coder.py          # command-line demo
    streamlit run app.py     # web UI

## Files
- `icd10_sample.py` - small demo ICD-10 reference set (swap in the full official list)
- `coder.py` - retrieval + LLM coding + validation
- `app.py` - Streamlit interface

## Ideas to extend
- Load the full ICD-10-CM / CPT code files and use embeddings for retrieval
- Add CPT/procedure coding, and human-review/approval workflow
- Evaluate against labelled data (e.g. MIMIC-IV, with proper data access)

> Demo only. Never use real patient data without proper compliance (HIPAA etc.); coding output needs review by a certified coder.
