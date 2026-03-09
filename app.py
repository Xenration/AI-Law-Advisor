import streamlit as st
import os
import feedparser
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_community.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain
from dotenv import load_dotenv
import json

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Smart Legal Advisor",
    page_icon="⚖️",
    layout="wide"
)

# ---------------- LOAD LAWYER DIRECTORY ----------------
with open("data/mumbai_lawyers.json", "r", encoding="utf-8") as file:
    lawyer_directory = json.load(file)

# ---------------- CASE FILE ----------------
CASES_FILE = "data/cases.json"

if not os.path.exists(CASES_FILE):
    with open(CASES_FILE, "w") as f:
        json.dump([], f)

def load_cases():
    with open(CASES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_cases(cases):
    with open(CASES_FILE, "w", encoding="utf-8") as f:
        json.dump(cases, f, indent=4)

# ---------------- CUSTOM LEGAL UI ----------------
st.markdown("""
<style>
    body { background-color: #eef1f7; }
    .main { background-color: #eef1f7; }
    h1 { color: #0d1b4c; text-align: center; font-weight: 700; }
    .stChatMessage { border-radius: 10px; padding: 12px; }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

st.title("⚖️ Smart Legal Advisor")
st.markdown("##### AI-Powered Indian Legal Guidance System")

# Load API key (Streamlit Cloud or local)
groq_api_key = os.getenv("GROQ_API_KEY")
# ---------------- CASE MANAGER SIDEBAR ----------------
st.sidebar.title("📁 Smart Case Manager")

cases = load_cases()

with st.sidebar.expander("➕ Create New Case"):
    case_title = st.text_input("Case Title")
    case_desc = st.text_area("Case Description")
    case_status = st.selectbox("Status", ["Open", "In Progress", "Closed"])

    if st.button("Create Case"):
        if case_title and case_desc:
            new_case = {
                "id": len(cases) + 1,
                "title": case_title,
                "description": case_desc,
                "status": case_status,
                "ai_summary": ""
            }
            cases.append(new_case)
            save_cases(cases)
            st.success("Case Created Successfully")
        else:
            st.warning("Fill all fields")

with st.sidebar.expander("📂 View Cases"):
    if cases:
        for case in cases:
            st.markdown(f"### {case['title']}")
            st.write(f"Status: {case['status']}")
            st.divider()
    else:
        st.write("No cases yet")

# ---------------- LEGAL UPDATES PANEL ----------------
@st.cache_data(ttl=600)
def get_legal_updates():
    feeds = {
        "PRS India": "https://prsindia.org/theprsblog/rss.xml",
        "LiveLaw": "https://www.livelaw.in/rss/main.xml"
    }

    updates = []
    for source, url in feeds.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:2]:
                summary = entry.summary if "summary" in entry else ""
                updates.append({
                    "source": source,
                    "title": entry.title,
                    "summary": summary[:180] + "...",
                    "link": entry.link
                })
        except:
            continue
    return updates[:4]

with st.expander("🔔 Latest Legal Updates", expanded=False):
    updates = get_legal_updates()
    if updates:
        for item in updates:
            st.markdown(f"### {item['title']}")
            st.markdown(f"**Source:** {item['source']}")
            st.write(item["summary"])
            st.markdown(f"[Read Full Article]({item['link']})")
            st.divider()

st.divider()

# ---------------- DOMAIN DETECTION ----------------
def extract_domain(answer):
    if "📌 Legal Domain:" in answer:
        return answer.split("📌 Legal Domain:")[1].split("\n")[0].strip()
    return None

def professional_advice_needed(answer):
    if "📌 Professional Legal Advice Required:" in answer:
        section = answer.split("📌 Professional Legal Advice Required:")[1]
        return "Yes" in section
    return False

# ---------------- SAFE LAWYER DISPLAY ----------------
def show_lawyers(domain):
    if domain in lawyer_directory:
        st.markdown("## 👨‍⚖️ Recommended Legal Professionals in Mumbai")
        for lawyer in lawyer_directory[domain][:10]:
            with st.container():
                st.markdown(f"""
### {lawyer.get('name','N/A')}

**Specialization:** {lawyer.get('specialization','N/A')}  
**Experience:** {lawyer.get('experience','N/A')}  
**Court:** {lawyer.get('court','N/A')}  
**Location:** {lawyer.get('location','N/A')}  
📞 **Phone:** {lawyer.get('contact_phone','N/A')}
                """)
                if lawyer.get("website"):
                    st.markdown(f"🌐 [Visit Website]({lawyer['website']})")
                st.divider()

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- LOAD MODELS ----------------
@st.cache_resource
def load_chain():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    db = FAISS.load_local(
        "my_vector_store",
        embeddings,
        allow_dangerous_deserialization=True
    )

    retriever = db.as_retriever(search_kwargs={"k": 4})

    prompt_template = """
You are a professional AI Legal Advisor specialized in Indian Law.

Use STRICT format:

📌 Legal Domain:
📌 Applicable Law:
📌 Section:
📌 Explanation:
📌 Legally Recognized Exceptions:
📌 Procedure:
📌 Professional Legal Advice Required:
📌 Source:

Context:
{context}

Chat History:
{chat_history}

Question:
{question}

Answer:
"""

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "chat_history", "question"]
    )

    llm = ChatGroq(
        groq_api_key=groq_api_key,
        model_name="llama-3.1-8b-instant",
        temperature=0.2
    )

    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=ConversationBufferWindowMemory(
            k=2, memory_key="chat_history", return_messages=True
        ),
        combine_docs_chain_kwargs={"prompt": prompt}
    )

qa = load_chain()

# ---------------- CHAT INTERFACE ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

query = st.chat_input("Ask your legal question here...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("assistant"):
        with st.spinner("Analyzing Indian law..."):
            result = qa.invoke({"question": query})
            answer = result["answer"]
            st.markdown(answer)

            # Attach AI answer to a case
            if cases:
                case_titles = [case["title"] for case in cases]
                selected_case = st.selectbox("Attach to case:", case_titles)

                if st.button("Save to Case"):
                    for case in cases:
                        if case["title"] == selected_case:
                            case["ai_summary"] = answer
                    save_cases(cases)
                    st.success("Saved to case")

            domain = extract_domain(answer)

            if professional_advice_needed(answer) and domain:
                show_lawyers(domain)

    st.session_state.messages.append({"role": "assistant", "content": answer})

# ---------------- RESET ----------------
st.divider()
if st.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.rerun()
