import streamlit as st
import json
import os
from datetime import datetime, date

st.set_page_config(
    page_title="Smart Case Management",
    page_icon="📁",
    layout="wide"
)

CASES_FILE = "data/cases.json"

if not os.path.exists(CASES_FILE):
    with open(CASES_FILE, "w") as f:
        json.dump([], f)

# -------------------- JSON Load / Save --------------------
def load_cases():
    with open(CASES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_cases(cases):
    with open(CASES_FILE, "w", encoding="utf-8") as f:
        json.dump(cases, f, indent=4)

cases = load_cases()

st.title("📁 Smart Legal Case Management Dashboard")
st.markdown("---")

# -------------------- CREATE NEW CASE --------------------
with st.expander("➕ Create New Case", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        case_title = st.text_input("Case Title")
        client_name = st.text_input("Client Name")
        court_name = st.text_input("Court Name")
    with col2:
        status = st.selectbox("Case Status", ["Open", "In Progress", "Closed"])
        priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        next_hearing = st.date_input("Next Hearing Date", value=date.today())

    description = st.text_area("Case Description")
    success_prob = st.slider("Estimated Success Probability (%)", 0, 100, 50)
    attachments = st.file_uploader("Upload Attachments (PDF/Image)", accept_multiple_files=True)

    if st.button("Create Case"):
        if case_title and client_name:
            attach_list = []
            for file in attachments:
                filepath = f"data/case_files/{file.name}"
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, "wb") as f:
                    f.write(file.getbuffer())
                attach_list.append({
                    "filename": file.name,
                    "uploaded_at": str(datetime.now())
                })

            new_case = {
                "id": len(cases)+1,
                "title": case_title,
                "client": client_name,
                "court": court_name,
                "status": status,
                "priority": priority,
                "description": description,
                "next_hearing": str(next_hearing),
                "created_at": str(datetime.now()),
                "notes": [],
                "attachments": attach_list,
                "success_probability": success_prob
            }

            cases.append(new_case)
            save_cases(cases)
            st.success("Case Created Successfully")
            st.rerun()
        else:
            st.warning("Fill required fields")

st.markdown("---")

# -------------------- DISPLAY CASES --------------------
if not cases:
    st.info("No cases available.")
else:
    # Sort cases by priority & hearing date
    sorted_cases = sorted(cases, key=lambda x: (x["priority"], x["next_hearing"]), reverse=True)
    for case in sorted_cases:
        with st.container():
            st.subheader(case["title"])
            col1, col2, col3 = st.columns([3,2,1])

            with col1:
                st.write(f"👤 Client: {case['client']}")
                st.write(f"🏛 Court: {case['court']}")
                st.write(f"📄 Description: {case['description']}")
                # Edit case
                if st.button("Edit Case", key=f"edit_{case['id']}"):
                    st.session_state[f"edit_case_{case['id']}"] = True

            with col2:
                st.write(f"📌 Status: {case['status']}")
                st.write(f"🔥 Priority: {case['priority']}")
                st.progress(case["success_probability"]/100)

                hearing_date = datetime.strptime(case["next_hearing"], "%Y-%m-%d").date()
                days_left = (hearing_date - date.today()).days

                if days_left < 0:
                    st.markdown("⚠️ Hearing Passed")
                elif days_left <= 3:
                    st.markdown("🔴 Next Hearing Soon!")
                elif days_left <= 7:
                    st.markdown("🟠 Upcoming Hearing")
                else:
                    st.markdown("🟢 Hearing Scheduled")

            with col3:
                if st.button("Delete", key=f"delete_{case['id']}"):
                    cases = [c for c in cases if c["id"] != case["id"]]
                    save_cases(cases)
                    st.rerun()

            # -------------------- CASE NOTES --------------------
            st.markdown("### 📝 Notes / Timeline")
            new_note = st.text_input("Add Note", key=f"note_{case['id']}")
            if st.button("Add Note", key=f"addnote_{case['id']}"):
                if new_note:
                    case["notes"].append({
                        "text": new_note,
                        "time": str(datetime.now())
                    })
                    save_cases(cases)
                    st.rerun()

            if case["notes"]:
                for note in case["notes"]:
                    st.write(f"- {note['text']} ({note['time']})")

            # -------------------- ATTACHMENTS --------------------
            st.markdown("### 📎 Attachments")
            if case["attachments"]:
                for attach in case["attachments"]:
                    filepath = f"data/case_files/{attach['filename']}"
                    if os.path.exists(filepath):
                        st.download_button(attach['filename'], open(filepath, "rb").read())

            st.markdown("---")

# -------------------- EDIT CASE FORM --------------------
for case in cases:
    if st.session_state.get(f"edit_case_{case['id']}"):
        st.markdown(f"## ✏️ Edit Case: {case['title']}")
        new_title = st.text_input("Case Title", value=case["title"], key=f"title_{case['id']}")
        new_client = st.text_input("Client Name", value=case["client"], key=f"client_{case['id']}")
        new_court = st.text_input("Court Name", value=case["court"], key=f"court_{case['id']}")
        new_status = st.selectbox("Case Status", ["Open","In Progress","Closed"], index=["Open","In Progress","Closed"].index(case["status"]), key=f"status_{case['id']}")
        new_priority = st.selectbox("Priority", ["Low","Medium","High"], index=["Low","Medium","High"].index(case["priority"]), key=f"priority_{case['id']}")
        new_hearing = st.date_input("Next Hearing Date", value=datetime.strptime(case["next_hearing"], "%Y-%m-%d").date(), key=f"hearing_{case['id']}")
        new_description = st.text_area("Description", value=case["description"], key=f"desc_{case['id']}")
        new_prob = st.slider("Success Probability (%)", 0, 100, value=case["success_probability"], key=f"prob_{case['id']}")

        if st.button("Save Changes", key=f"save_{case['id']}"):
            case["title"] = new_title
            case["client"] = new_client
            case["court"] = new_court
            case["status"] = new_status
            case["priority"] = new_priority
            case["next_hearing"] = str(new_hearing)
            case["description"] = new_description
            case["success_probability"] = new_prob
            save_cases(cases)
            st.session_state[f"edit_case_{case['id']}"] = False
            st.success("Case Updated Successfully")
            st.rerun()