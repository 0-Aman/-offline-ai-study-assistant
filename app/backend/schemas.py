from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=2)
    language: str = "English"
    document_id: str | None = None
    top_k: int = Field(default=4, ge=1, le=10)


class GenerateRequest(BaseModel):
    document_id: str | None = None
    language: str = "English"
    topic: str | None = None
    top_k: int = Field(default=8, ge=1, le=20)


class QuizRequest(GenerateRequest):
    number_of_questions: int = Field(default=5, ge=1, le=15)


class SourceChunk(BaseModel):
    document_id: str
    source: str
    page: int | None = None
    chunk: str


class AnswerResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
