# Offline AI Study Assistant for College Students

A beginner-friendly AI engineering project that lets students upload college PDFs or notes, ask questions from their material, generate summaries, create quizzes, and prepare interview questions in Hindi or English.

## Features

- Upload PDF, TXT, or Markdown notes
- Ask questions using RAG with source chunks
- Generate concise study summaries
- Generate MCQ quizzes
- Generate interview/viva questions
- Hindi and English response modes
- Local/offline LLM support with Ollama
- Persistent vector database with ChromaDB
- FastAPI backend and Streamlit frontend

## Tech Stack

- Python
- FastAPI
- Streamlit
- LangChain text splitting
- ChromaDB vector database
- Ollama for offline embeddings and chat
- PyPDF for PDF parsing

## Folder Structure

```text
.
├── app/
│   ├── backend/
│   │   ├── main.py
│   │   ├── rag.py
│   │   ├── schemas.py
│   │   └── storage.py
│   └── frontend/
│       └── streamlit_app.py
├── data/
│   ├── chroma/
│   └── uploads/
├── requirements.txt
└── README.md
```

## Setup

1. Create and activate a virtual environment.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies.

```powershell
pip install -r requirements.txt
```

3. Install Ollama from https://ollama.com and pull local models.

```powershell
ollama pull llama3.1
ollama pull nomic-embed-text
```

4. Start the backend.

```powershell
uvicorn app.backend.main:app --reload --port 8000
```

5. Start the frontend in another terminal.

```powershell
streamlit run app/frontend/streamlit_app.py
```

On Windows, you can also start both services with:

```powershell
.\run_app.ps1
```

## API Endpoints

- `POST /upload` uploads and indexes a study file
- `POST /ask` answers questions with source chunks
- `POST /summarize` summarizes selected material
- `POST /quiz` creates MCQs
- `POST /interview-questions` creates interview/viva questions
- `GET /documents` lists indexed documents

## Project Extensions

- Add voice input with Whisper
- Add login and semester-wise memory
- Add Gemini API as an online model option
- Add flashcard spaced repetition
- Add Docker deployment
- Add evaluation scripts for answer quality
