from pathlib import Path
from uuid import uuid4

import chromadb
import ollama
from chromadb.api.models.Collection import Collection
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.backend.storage import CHROMA_DIR, ensure_data_dirs, load_text


COLLECTION_NAME = "study_material"
EMBED_MODEL = "nomic-embed-text"
CHAT_MODEL = "llama3.1"


class StudyRAG:
    def __init__(self) -> None:
        ensure_data_dirs()
        self.client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=900,
            chunk_overlap=180,
            separators=["\n\n", "\n", ".", "?", "!", " ", ""],
        )

    def index_file(self, path: Path) -> dict:
        document_id = uuid4().hex
        pages = load_text(path)
        ids: list[str] = []
        chunks: list[str] = []
        metadatas: list[dict] = []

        for page in pages:
            for chunk in self.splitter.split_text(page["text"]):
                clean_chunk = chunk.strip()
                if not clean_chunk:
                    continue
                ids.append(uuid4().hex)
                chunks.append(clean_chunk)
                metadatas.append(
                    {
                        "document_id": document_id,
                        "source": path.name,
                        "page": page["page"] or "",
                    }
                )

        if not chunks:
            raise ValueError("No readable text found in the uploaded file.")

        embeddings = [self._embed(chunk) for chunk in chunks]
        self.collection.add(
            ids=ids,
            documents=chunks,
            metadatas=metadatas,
            embeddings=embeddings,
        )
        return {"document_id": document_id, "filename": path.name, "chunks": len(chunks)}

    def ask(self, question: str, language: str, document_id: str | None, top_k: int) -> dict:
        chunks = self.search(question, document_id, top_k)
        context = self._format_context(chunks)
        prompt = f"""
You are an offline AI study assistant for college students.
Answer in {language}.
Use only the provided study material. If the answer is not present, say that the material does not contain enough information.
Give a clear, exam-friendly answer.

Study material:
{context}

Question: {question}
"""
        return {"answer": self._chat(prompt), "sources": chunks}

    def summarize(self, language: str, document_id: str | None, topic: str | None, top_k: int) -> str:
        query = topic or "important concepts summary"
        chunks = self.search(query, document_id, top_k)
        prompt = f"""
Summarize the following college study material in {language}.
Use headings and short bullet points.
Include key definitions, formulas, and exam-important points when present.

Material:
{self._format_context(chunks)}
"""
        return self._chat(prompt)

    def quiz(self, language: str, document_id: str | None, topic: str | None, top_k: int, count: int) -> str:
        query = topic or "important exam questions"
        chunks = self.search(query, document_id, top_k)
        prompt = f"""
Create {count} multiple-choice questions in {language} from the material.
Each question must have four options, mark the correct answer, and add a one-line explanation.

Material:
{self._format_context(chunks)}
"""
        return self._chat(prompt)

    def interview_questions(self, language: str, document_id: str | None, topic: str | None, top_k: int) -> str:
        query = topic or "important viva and interview concepts"
        chunks = self.search(query, document_id, top_k)
        prompt = f"""
Generate interview or viva questions in {language} from this study material.
Group them into basic, intermediate, and advanced levels.
Include short model answers.

Material:
{self._format_context(chunks)}
"""
        return self._chat(prompt)

    def list_documents(self) -> list[dict]:
        data = self.collection.get(include=["metadatas"])
        documents: dict[str, dict] = {}
        for metadata in data.get("metadatas", []):
            document_id = metadata.get("document_id")
            if not document_id:
                continue
            documents.setdefault(
                document_id,
                {"document_id": document_id, "source": metadata.get("source"), "chunks": 0},
            )
            documents[document_id]["chunks"] += 1
        return sorted(documents.values(), key=lambda item: item["source"] or "")

    def search(self, query: str, document_id: str | None, top_k: int) -> list[dict]:
        where = {"document_id": document_id} if document_id else None
        result = self.collection.query(
            query_embeddings=[self._embed(query)],
            n_results=top_k,
            where=where,
            include=["documents", "metadatas"],
        )
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        chunks = []
        for document, metadata in zip(documents, metadatas):
            page = metadata.get("page") or None
            chunks.append(
                {
                    "document_id": metadata.get("document_id", ""),
                    "source": metadata.get("source", ""),
                    "page": int(page) if str(page).isdigit() else None,
                    "chunk": document,
                }
            )
        return chunks

    def _embed(self, text: str) -> list[float]:
        try:
            response = ollama.embeddings(model=EMBED_MODEL, prompt=text)
            return response["embedding"]
        except Exception as exc:
            raise RuntimeError(
                "Ollama embedding failed. Start Ollama and run: ollama pull nomic-embed-text"
            ) from exc

    def _chat(self, prompt: str) -> str:
        try:
            response = ollama.chat(
                model=CHAT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.2},
            )
            return response["message"]["content"]
        except Exception as exc:
            raise RuntimeError("Ollama chat failed. Start Ollama and run: ollama pull llama3.1") from exc

    @staticmethod
    def _format_context(chunks: list[dict]) -> str:
        if not chunks:
            return "No matching study material found."
        formatted = []
        for index, chunk in enumerate(chunks, start=1):
            page = f", page {chunk['page']}" if chunk.get("page") else ""
            formatted.append(f"[Source {index}: {chunk['source']}{page}]\n{chunk['chunk']}")
        return "\n\n".join(formatted)


rag = StudyRAG()
