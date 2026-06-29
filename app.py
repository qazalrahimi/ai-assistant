import streamlit as st
from groq import Groq
from tavily import TavilyClient
from dotenv import load_dotenv
import os
import fitz
from docx import Document
import tempfile

# ── Configuration ──────────────────────────────────────────────────────────────
load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

# ── File Readers ───────────────────────────────────────────────────────────────
def read_pdf(file) -> str:
    """Extract text from a PDF file (max 3000 chars)."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file.read())
        tmp_path = tmp.name
    doc = fitz.open(tmp_path)
    return "".join(page.get_text() for page in doc)[:3000]

def read_docx(file) -> str:
    """Extract text from a Word document (max 3000 chars)."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(file.read())
        tmp_path = tmp.name
    doc = Document(tmp_path)
    return "\n".join(p.text for p in doc.paragraphs)[:3000]

# ── Web Search ─────────────────────────────────────────────────────────────────
def search_web(query: str) -> str:
    """Search the web and return top 3 results as a formatted string."""
    results = tavily_client.search(query=query, max_results=3)
    return "\n".join(
        f"- {r['title']}: {r['content'][:300]}"
        for r in results["results"]
    )

# ── AI Response ────────────────────────────────────────────────────────────────
def get_response(messages: list) -> str:
    """Send messages to the AI model and return the response."""
    response = groq_client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=1000
    )
    return response.choices[0].message.content

# ── Session State ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "file_content" not in st.session_state:
    st.session_state.file_content = None

# ── UI Styles ──────────────────────────────────────────────────────────────────
st.markdown("""
    <style>
        .stChatMessage p { direction: rtl; text-align: right; }
        .stChatInputContainer textarea { direction: rtl; text-align: right; }
    </style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("🤖 Personal AI Assistant")

# ── File Upload ────────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader("Upload a PDF or Word file", type=["pdf", "docx"])
if uploaded_file:
    if uploaded_file.name.endswith(".pdf"):
        st.session_state.file_content = read_pdf(uploaded_file)
    else:
        st.session_state.file_content = read_docx(uploaded_file)
    st.success("File loaded! Ask me anything about it 😊")

# ── Summarize Button ───────────────────────────────────────────────────────────
if st.session_state.file_content:
    if st.button("📝 Summarize"):
        with st.chat_message("assistant"):
            with st.spinner("Summarizing..."):
                answer = get_response([{
                    "role": "user",
                    "content": f"Summarize this text clearly:\n\n{st.session_state.file_content}"
                }])
                st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

# ── Chat History ───────────────────────────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── Chat Input ─────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Type your message..."):

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Build context with web search and file content
    user_content = prompt

    with st.spinner("Searching the web..."):
        user_content += f"\n\nWeb search results:\n{search_web(prompt)}"

    if st.session_state.file_content:
        user_content += f"\n\nFile content:\n{st.session_state.file_content}"

    # Build messages list for API call
    messages = st.session_state.messages + [{"role": "user", "content": user_content}]

    # Save original prompt (without search/file context) to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get and display AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = get_response(messages)
            st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
