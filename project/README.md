# Srimad Bhagavad Gita - Chapter 16 Multilingual RAG Chatbot

This project is a complete, production-ready, modular Retrieval-Augmented Generation (RAG) pipeline built from scratch. It allows users to ask questions in **English, Hindi, or Hinglish** about Bhagavad Gita Chapter 16 (*Daivasura Sampad Vibhaga Yoga*) and get context-backed answers sourced directly from a local PDF document.

---

## 🛠️ Project Structure
```
project/
├── data/
│      adhyay16.pdf       # Source text PDF (Sanskrit + Hindi + English)
├── vectorstore/
│      faiss.index        # FAISS vector database
│      metadata.pkl       # Chunks metadata pickle
├── config.py             # System configurations
├── generate_pdf.py       # PDF generator helper
├── ingest.py             # PDF text parser and chunker
├── build_index.py        # Vector embedding and index builder
├── retriever.py          # Similarity retriever and query router
├── chatbot.py            # Ollama client and CLI prompt chatbot
├── requirements.txt      # List of dependencies
└── README.md             # Guide documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites & Environment Setup
Verify you have python 3.10+ installed.

Run the pip installation command:
```bash
pip install -r requirements.txt
```

Ensure the **Ollama Desktop App** is installed and running on your local machine.
Pull the default model (Qwen 2.5 7B) or any model of your choice:
```bash
ollama pull qwen2.5:7b
```
*(Note: The chatbot automatically checks your local Ollama library on startup. If you do not have `qwen2.5:7b` pulled, it will fallback to the first available local model from your library).*

---

### 2. Generate the PDF
To build the test database containing Sanskrit shlokas, Hindi meanings, and English translations:
```bash
python generate_pdf.py
```
This generates the source PDF inside `project/data/adhyay16.pdf`.

---

### 3. Build the FAISS Vector Index
Parse the PDF, chunk the text, compute embeddings, and build the vector database store:
```bash
python build_index.py
```
This creates `faiss.index` and `metadata.pkl` inside the `project/vectorstore/` directory. If the index files are already present, the script loads them directly without rebuilding.

---

### 4. Run the Chatbot
Start the interactive Q&A command-line loop:
```bash
python chatbot.py
```

---

## 🔍 Features & Verification Queries
The chatbot displays retrieved source page blocks, similarity scores, and inference time for every query.

Try testing the following queries:
* **English**: `"What are the divine qualities?"`
* **Hindi**: `"दैवी गुण कौन-कौन से हैं?"`
* **Hinglish**: `"Krishna ne daivi gunon ke baare me kya kaha hai?"`
* **Direct Verse Lookup**: `"Verse 3"` (directly matches metadata without semantic retrieval)
* **Keyword Filter**: `"List all Asuri qualities."`
* **Sources**: Lists all unique page numbers utilized at the bottom of the response.

To exit the loop, type `exit`.
