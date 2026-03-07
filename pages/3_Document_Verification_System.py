# pages/3_Document_Verification_System.py

import streamlit as st
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from PyPDF2 import PdfReader

st.set_page_config(page_title="Document Verification System", page_icon="📝", layout="wide")
st.title("📝 Document Verification System")
st.markdown("Upload a legal document (PDF) and get AI analysis with surety/confidence score and summary.")

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

uploaded_file = st.file_uploader("Upload your legal document (PDF only)", type=["pdf"])

def detect_doc_type(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text() + " "
    text_lower = text.lower()

    if "rental agreement" in text_lower or "lease" in text_lower:
        return "Rental Agreement", text
    elif "legal notice" in text_lower or "notice" in text_lower:
        return "Legal Notice", text
    elif "non-disclosure" in text_lower or "nda" in text_lower:
        return "NDA", text
    else:
        return "Other", text

if uploaded_file:
    doc_type, full_text = detect_doc_type(uploaded_file)
    st.info(f"Detected Document Type: **{doc_type}**")

    if full_text.strip() == "":
        st.warning("Could not extract text. Make sure PDF is text-based.")
    else:
        st.markdown("### Document Preview (first 500 chars):")
        st.text(full_text[:500] + "..." if len(full_text) > 500 else full_text)

        if st.button("Analyze Document"):
            with st.spinner("Analyzing document..."):
                llm = ChatGroq(
                    groq_api_key=groq_api_key,
                    model_name="llama-3.1-8b-instant",
                    temperature=0.2
                )

                prompt = f"""
You are a professional Indian legal assistant.

Analyze the following {doc_type} document:

1. Determine if the document is official and likely valid under Indian law.
2. Highlight any missing, unusual, or incomplete information.
3. Evaluate the likelihood that the document is real or fake.
4. Provide a **surety/confidence score** in percentage for the document authenticity (e.g., 0-100%).
5. Provide a **short summary** in 3-5 lines for quick understanding.
6. Provide recommendations if corrections are needed.
7. Keep the explanation simple and professional.

Document Text:
{full_text}
"""

                result = llm.invoke(prompt).content
                st.markdown("### Analysis Result:")
                st.write(result)