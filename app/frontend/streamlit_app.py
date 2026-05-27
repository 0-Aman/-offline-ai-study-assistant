import requests
import streamlit as st


API_URL = "http://localhost:8000"


st.set_page_config(page_title="Offline AI Study Assistant", page_icon=":books:", layout="wide")

st.title("Offline AI Study Assistant")
st.caption("Upload college material, ask questions, generate summaries, quizzes, and interview prep.")


def api_get(path: str):
    response = requests.get(f"{API_URL}{path}", timeout=30)
    response.raise_for_status()
    return response.json()


def api_post(path: str, payload: dict):
    response = requests.post(f"{API_URL}{path}", json=payload, timeout=180)
    response.raise_for_status()
    return response.json()


with st.sidebar:
    st.header("Study Material")
    uploaded_file = st.file_uploader("Upload PDF, TXT, or Markdown", type=["pdf", "txt", "md"])
    if uploaded_file and st.button("Index File", type="primary", use_container_width=True):
        with st.spinner("Reading and indexing material..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            response = requests.post(f"{API_URL}/upload", files=files, timeout=300)
            if response.ok:
                result = response.json()
                st.success(f"Indexed {result['chunks']} chunks")
            else:
                st.error(response.json().get("detail", "Upload failed"))

    try:
        documents = api_get("/documents")
    except Exception:
        documents = []
        st.warning("Start the FastAPI backend on port 8000.")

    document_options = {"All documents": None}
    document_options.update({f"{doc['source']} ({doc['chunks']} chunks)": doc["document_id"] for doc in documents})
    selected_document = st.selectbox("Use document", list(document_options.keys()))
    document_id = document_options[selected_document]
    language = st.radio("Language", ["English", "Hindi"], horizontal=True)
    top_k = st.slider("Source chunks", min_value=2, max_value=10, value=4)


ask_tab, summary_tab, quiz_tab, interview_tab = st.tabs(
    ["Ask Questions", "Summary", "MCQ Quiz", "Interview Prep"]
)


with ask_tab:
    question = st.text_area("Question", placeholder="Example: Explain DBMS normalization with examples.")
    if st.button("Ask AI", type="primary", use_container_width=True):
        if not question.strip():
            st.warning("Enter a question first.")
        else:
            with st.spinner("Thinking from your notes..."):
                try:
                    result = api_post(
                        "/ask",
                        {
                            "question": question,
                            "language": language,
                            "document_id": document_id,
                            "top_k": top_k,
                        },
                    )
                    st.subheader("Answer")
                    st.write(result["answer"])
                    st.subheader("Sources")
                    for source in result["sources"]:
                        page = f" - page {source['page']}" if source.get("page") else ""
                        with st.expander(f"{source['source']}{page}"):
                            st.write(source["chunk"])
                except Exception as exc:
                    st.error(str(exc))


with summary_tab:
    topic = st.text_input("Focus topic", placeholder="Optional: operating system deadlocks")
    if st.button("Generate Summary", type="primary", use_container_width=True):
        with st.spinner("Creating study summary..."):
            try:
                result = api_post(
                    "/summarize",
                    {"language": language, "document_id": document_id, "topic": topic or None, "top_k": 8},
                )
                st.write(result["summary"])
            except Exception as exc:
                st.error(str(exc))


with quiz_tab:
    quiz_topic = st.text_input("Quiz topic", placeholder="Optional: machine learning basics")
    count = st.number_input("Questions", min_value=1, max_value=15, value=5)
    if st.button("Generate Quiz", type="primary", use_container_width=True):
        with st.spinner("Preparing MCQs..."):
            try:
                result = api_post(
                    "/quiz",
                    {
                        "language": language,
                        "document_id": document_id,
                        "topic": quiz_topic or None,
                        "number_of_questions": count,
                        "top_k": 8,
                    },
                )
                st.write(result["quiz"])
            except Exception as exc:
                st.error(str(exc))


with interview_tab:
    interview_topic = st.text_input("Interview topic", placeholder="Optional: OOP concepts")
    if st.button("Generate Interview Questions", type="primary", use_container_width=True):
        with st.spinner("Building viva/interview prep..."):
            try:
                result = api_post(
                    "/interview-questions",
                    {
                        "language": language,
                        "document_id": document_id,
                        "topic": interview_topic or None,
                        "top_k": 8,
                    },
                )
                st.write(result["questions"])
            except Exception as exc:
                st.error(str(exc))
