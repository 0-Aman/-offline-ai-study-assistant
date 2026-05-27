from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.backend.rag import rag
from app.backend.schemas import AnswerResponse, AskRequest, GenerateRequest, QuizRequest
from app.backend.storage import save_upload


app = FastAPI(title="Offline AI Study Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check() -> dict:
    return {"status": "ok", "message": "Offline AI Study Assistant API is running"}


@app.post("/upload")
async def upload(file: UploadFile = File(...)) -> dict:
    try:
        content = await file.read()
        path = save_upload(file.filename or "study_material", content)
        return rag.index_file(path)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/documents")
def documents() -> list[dict]:
    return rag.list_documents()


@app.post("/ask", response_model=AnswerResponse)
def ask(request: AskRequest) -> dict:
    try:
        return rag.ask(request.question, request.language, request.document_id, request.top_k)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/summarize")
def summarize(request: GenerateRequest) -> dict:
    try:
        return {"summary": rag.summarize(request.language, request.document_id, request.topic, request.top_k)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/quiz")
def quiz(request: QuizRequest) -> dict:
    try:
        return {
            "quiz": rag.quiz(
                request.language,
                request.document_id,
                request.topic,
                request.top_k,
                request.number_of_questions,
            )
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/interview-questions")
def interview_questions(request: GenerateRequest) -> dict:
    try:
        return {
            "questions": rag.interview_questions(
                request.language,
                request.document_id,
                request.topic,
                request.top_k,
            )
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
