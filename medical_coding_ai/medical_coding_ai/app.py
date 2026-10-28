"""Streamlit UI:  streamlit run app.py"""
import streamlit as st
from coder import suggest_codes

st.set_page_config(page_title="AI Medical Coder", page_icon="🩺")
st.title("🩺 Generative AI for Medical Coding")
st.caption("Paste a clinical note and get suggested ICD-10 codes. Demo only; a certified coder must review.")

note = st.text_area("Clinical note", height=220,
                    placeholder="e.g. Patient with type 2 diabetes and hypertension presents with fever...")

if st.button("Suggest codes", type="primary") and note.strip():
    with st.spinner("Analyzing note..."):
        try:
            results = suggest_codes(note)
        except Exception as e:
            st.error(f"Error: {e}")
            results = []
    for r in results:
        icon = "✅" if r["verified"] else "⚠️ not in reference set"
        st.markdown(f"**{r['code']}** - {r['description']}  {icon}")
        st.caption(f"Evidence: \"{r['evidence']}\" | Confidence: {r['confidence']}")
