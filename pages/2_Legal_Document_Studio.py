import streamlit as st
import os
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
import tempfile

st.set_page_config(page_title="Legal Document Studio", page_icon="📄", layout="wide")

st.title("📄 Legal Document Studio")
st.markdown("Generate structured Indian legal documents with guided professional inputs.")

# Load API key (Streamlit Cloud or local)
groq_api_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    api_key=groq_api_key,
    model_name="llama-3.1-8b-instant",
    temperature=0.2
)

today_date = datetime.today().strftime("%d %B %Y")

# ---------------- CLEAN MARKDOWN ----------------
def clean_markdown(text):
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
    return text

# ---------------- DOCUMENT TYPES ----------------
doc_type = st.selectbox(
    "Select Document Type",
    [
        "Legal Notice",
        "Rental Agreement",
        "Leave & License Agreement",
        "Affidavit",
        "Power of Attorney",
        "Bail Application",
        "FIR Draft",
        "Consumer Court Complaint",
        "Employment Agreement",
        "Non-Disclosure Agreement (NDA)",
        "Partnership Deed"
    ]
)

st.divider()
generated_doc = None

# =====================================================
# LEGAL NOTICE
# =====================================================
if doc_type == "Legal Notice":
    sender = st.text_input("Sender Name")
    sender_address = st.text_area("Sender Address")
    receiver = st.text_input("Receiver Name")
    receiver_address = st.text_area("Receiver Address")
    reason = st.text_area("Reason for Notice")
    demand = st.text_area("Relief / Demand")
    notice_days = st.number_input("Notice Period (Days)", value=15)

    if st.button("Generate Legal Notice"):
        prompt = f"""
Draft a professional LEGAL NOTICE under Indian law.
Use proper legal formatting, numbered paragraphs and signature section.

Sender: {sender}
Address: {sender_address}

Receiver: {receiver}
Address: {receiver_address}

Reason: {reason}
Demand: {demand}
Notice Period: {notice_days} days
Date: {today_date}
"""
        generated_doc = llm.invoke(prompt).content

# =====================================================
# RENTAL AGREEMENT
# =====================================================
elif doc_type == "Rental Agreement":
    landlord = st.text_input("Landlord Name")
    tenant = st.text_input("Tenant Name")
    property_address = st.text_area("Property Address")
    rent = st.number_input("Monthly Rent ₹")
    deposit = st.number_input("Security Deposit ₹")
    duration = st.number_input("Lease Duration (Months)", value=11)

    if st.button("Generate Rental Agreement"):
        prompt = f"""
Draft a RENTAL AGREEMENT under Indian law.

Landlord: {landlord}
Tenant: {tenant}
Property: {property_address}
Monthly Rent: ₹{rent}
Security Deposit: ₹{deposit}
Duration: {duration} months

Include clauses:
- Rent payment terms
- Maintenance
- Termination
- Notice period
- Jurisdiction
- Signature block with witnesses
"""
        generated_doc = llm.invoke(prompt).content

# =====================================================
# BAIL APPLICATION
# =====================================================
elif doc_type == "Bail Application":
    accused = st.text_input("Accused Name")
    court = st.text_input("Court Name")
    section = st.text_input("IPC Sections Involved")
    facts = st.text_area("Brief Case Facts")

    if st.button("Generate Bail Application"):
        prompt = f"""
Draft a formal BAIL APPLICATION under Indian law.

Accused: {accused}
Court: {court}
Sections: {section}
Facts: {facts}

Include grounds for bail and prayer clause.
"""
        generated_doc = llm.invoke(prompt).content

# =====================================================
# GENERIC TYPES
# =====================================================
elif doc_type in [
    "Affidavit",
    "Power of Attorney",
    "Leave & License Agreement",
    "Consumer Court Complaint",
    "Employment Agreement",
    "Non-Disclosure Agreement (NDA)",
    "Partnership Deed",
    "FIR Draft"
]:
    party1 = st.text_input("Party 1 Name")
    party2 = st.text_input("Party 2 Name")
    details = st.text_area("Document Details")

    if st.button(f"Generate {doc_type}"):
        prompt = f"""
Draft a professional {doc_type} under Indian law.

Party 1: {party1}
Party 2: {party2}
Details: {details}
Date: {today_date}

Use structured clauses, jurisdiction clause and signature section.
"""
        generated_doc = llm.invoke(prompt).content

# =====================================================
# DISPLAY & PROFESSIONAL PDF
# =====================================================
if generated_doc:
    st.success("Document Generated Successfully")
    st.markdown(generated_doc)

    cleaned_text = clean_markdown(generated_doc)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
        doc = SimpleDocTemplate(tmpfile.name, pagesize=A4)
        styles = getSampleStyleSheet()

        # Custom Styles
        normal_style = styles["Normal"]
        heading_style = ParagraphStyle(
            name="HeadingCenter",
            parent=styles["Normal"],
            alignment=TA_CENTER,
            fontSize=14,
            spaceAfter=10
        )

        elements = []

        for para in cleaned_text.split("\n"):
            para = para.strip()
            if not para:
                continue

            # If line is ALL CAPS → treat as heading
            if para.isupper() and len(para) < 60:
                elements.append(Paragraph(para, heading_style))
            else:
                elements.append(Paragraph(para, normal_style))

            elements.append(Spacer(1, 0.2 * inch))

        doc.build(elements)

        with open(tmpfile.name, "rb") as f:
            st.download_button(
                "📥 Download Professional PDF",
                f,
                file_name=f"{doc_type.replace(' ','_')}.pdf",
                mime="application/pdf"

            )


