⚖️ AI-Law-Advisor

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-WebApp-red.svg)
![LLM](https://img.shields.io/badge/AI-LLM-green.svg)

**AI-Law-Advisor** is an AI-powered legal assistance platform built using **Python, Streamlit, and Large Language Models (LLMs)**.
The system helps users get legal guidance, generate legal documents, verify uploaded documents, and manage legal cases through an interactive web interface.

The platform uses **Retrieval Augmented Generation (RAG)** with **FAISS vector search and embeddings** to provide context-aware responses based on a legal document knowledge base.

---

📌 Features

 🤖 AI Legal Chatbot

* Ask legal questions in natural language
* Uses **RAG architecture** to retrieve relevant legal documents
* Generates structured legal guidance

 📄 Legal Document Generator

* Create legal documents such as:

  * Legal Notices
  * Rental Agreements
  * NDAs
* Automatically generates **formatted PDF documents**

🔎 Document Verification System

* Upload legal documents
* AI analyzes document structure
* Detects missing information and provides **confidence score**

 📂 Case Management Dashboard

* Track legal cases
* Add hearing dates and notes
* Manage client information
* Organize legal files

---

 🧠 Architecture

The project follows a **Retrieval Augmented Generation (RAG)** pipeline:

1. **Document Loader**

   * Loads legal PDFs from the knowledge base.

2. **Text Splitter**

   * Splits documents into smaller chunks for embedding.

3. **Embeddings**

   * Converts text into vector representations using embedding models.

4. **Vector Database**

   * Uses **FAISS** for fast semantic search.

5. **LLM**

   * Uses **Groq LLaMA models** for generating answers.

6. **Retriever + Memory**

   * Retrieves relevant context and maintains chat history.

---

🛠 Tech Stack

* **Python**
* **Streamlit**
* **LangChain**
* **FAISS Vector Database**
* **Groq LLaMA API**
* **HuggingFace Embeddings**
* **ReportLab (PDF Generation)**

---

# ⚙️ Setup and Installation

 1️⃣ Clone the Repository

```bash
git clone https://github.com/yourusername/AI-law-advisor.git
cd AI-law-advisor
```

2️⃣ Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Add Environment Variables

Create a `.env` file in the root directory:

```
GROQ_API_KEY=your_groq_api_key
```

---

 ▶️ Running the Application

Start the Streamlit app:

```bash
streamlit run app.py
```

The application will open in your browser.

---

 🌐 Deployment

The project can be deployed easily using **Streamlit Community Cloud**.

Once deployed, users can access the platform through a public link and interact with the AI legal assistant directly from the browser.

---

 🎯 Project Goal

The goal of **AI-Law-Advisor** is to make legal information more accessible by combining **AI, document retrieval, and automation tools** into a single platform that assists both **general users and legal professionals**.
