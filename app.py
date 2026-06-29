import streamlit as st
from groq import Groq
from tavily import TavilyClient
from dotenv import load_dotenv
import os
import fitz
from docx import Document
import tempfile

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search_web(query):
    results = tavily_client.search(query=query, max_results=3)
    output = ""
    for r in results["results"]:
        output += f"- {r['title']}: {r['content'][:300]}\n"
    return output

def read_pdf(file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file.read())
        tmp_path = tmp.name
    doc = fitz.open(tmp_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text[:3000]

def read_docx(file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(file.read())
        tmp_path = tmp.name
    doc = Document(tmp_path)
    text = "\n".join([p.text for p in doc.paragraphs])
    return text[:3000]

if "messages" not in st.session_state:
    st.session_state.messages = []
if "file_content" not in st.session_state:
    st.session_state.file_content = None

st.markdown("""
    <style>
        .stChatMessage p { direction: rtl; text-align: right; }
        .stChatInputContainer textarea { direction: rtl; text-align: right; }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 دستیار هوشمند من")
# دکمه خلاصه‌سازی
if st.session_state.file_content:
    if st.button("📝 خلاصه کن"):
        with st.chat_message("assistant"):
            with st.spinner("در حال خلاصه کردن..."):
                response = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{
                        "role": "user",
                        "content": f"این متن رو به فارسی خلاصه کن:\n\n{st.session_state.file_content}"
                    }],
                    max_tokens=1000
                )
                answer = response.choices[0].message.content
                st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
# آپلود فایل
uploaded_file = st.file_uploader("فایل PDF یا Word آپلود کن", type=["pdf", "docx"])
if uploaded_file:
    if uploaded_file.name.endswith(".pdf"):
        st.session_state.file_content = read_pdf(uploaded_file)
    else:
        st.session_state.file_content = read_docx(uploaded_file)
    st.success("فایل خونده شد! حالا ازش سوال بپرس 😊")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("پیامت رو بنویس..."):

    with st.chat_message("user"):
        st.markdown(prompt)

    messages = list(st.session_state.messages)

    # اگه فایل آپلود شده، محتواش رو به پرامپت اضافه کن
    user_content = prompt
    if st.session_state.file_content:
        user_content = f"{prompt}\n\nمحتوای فایل:\n{st.session_state.file_content}"

    # جستجوی وب
    with st.spinner("در حال جستجو در وب..."):
        search_result = search_web(prompt)
    user_content += f"\n\nاطلاعات از وب:\n{search_result}"

    messages.append({"role": "user", "content": user_content})
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("در حال فکر کردن..."):
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                max_tokens=1000
            )
            answer = response.choices[0].message.content
            st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
