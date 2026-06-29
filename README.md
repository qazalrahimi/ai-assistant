# 🤖 Personal AI Assistant

A smart chatbot built with Python that can:
- Answer your questions intelligently
- Search the web for real-time information
- Read and summarize PDF and Word files

## Built With
- **Python** — Core programming language
- **Streamlit** — Web user interface
- **Groq API** — LLaMA 3.3 AI model
- **Tavily** — Real-time web search

## Features
- 💬 Natural conversation in any language
- 🔍 Real-time web search
- 📄 PDF and Word file reading
- 📝 One-click summarization
- 🧠 Conversation memory

## Installation

1. Clone the repository:
git clone https://github.com/yourusername/ai-assistant.git
cd ai-assistant

2. Create a virtual environment:
python3 -m venv venv
source venv/bin/activate

3. Install dependencies:
pip install -r requirements.txt

4. Create a .env file:
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key

5. Run the app:
streamlit run app.py

## How to Get API Keys
- Groq API Key: https://console.groq.com
- Tavily API Key: https://app.tavily.com

## Project Structure
- app.py — Main application code
- requirements.txt — Python dependencies
- .env — API keys (not included in repo)
- .gitignore — Files excluded from Git
