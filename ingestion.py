import os
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

def embed_and_save_documents():
    print("Loading PDFs...")
    loader = PyPDFDirectoryLoader("./LEGAL-DATA")
    docs = loader.load()

    print("Splitting documents...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    final_docs = splitter.split_documents(docs)

    print("Loading FREE embeddings (HuggingFace)...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    print("Creating FAISS vector store...")
    vectors = FAISS.from_documents(final_docs, embeddings)

    print("Saving vector store...")
    vectors.save_local("my_vector_store")

    print("✅ Vector store created successfully")

if __name__ == "__main__":
    embed_and_save_documents()