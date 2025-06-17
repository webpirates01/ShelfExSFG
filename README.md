# LLM Powered Flashcard Generator

A Streamlit web application that generates educational flashcards using Google's Gemini AI. Perfect for students, teachers, and lifelong learners to quickly create study materials from any text content.

## Features

- 🚀 AI-powered flashcard generation using Gemini 1.5 Flash
- 📝 Input content via text or file upload (TXT)
- ⚙️ Customizable options:
  - Difficulty level (Easy, Medium, Hard)
  - Number of flashcards (5-20)
  - Answer length (Short, Medium, Long)
  - Subject specification
- 📚 Organized flashcard display with expandable Q&A
- 💾 Multiple export formats:
  - JSON
  - CSV
  - Anki-compatible TSV
- 🎨 Clean, responsive interface with modern styling

## Prerequisites

Before you begin, ensure you have:

- Python 3.8+ installed
- A Google API key with access to Gemini AI
- Streamlit installed

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/flashcard-generator.git
   cd flashcard-generator
   ```

2. Create virtual environment:
  ```
 python -m venv venv
# Windows: venv\Scripts\activate
source venv/bin/activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```
4. Create .env file:
```
echo "GEM_API=your_api_key_here" > .env
```
# USAGE
```
streamlit run app.py
```
## File Structure
```
flashcard-generator/
├── app.py
├── README.md
├── requirements.txt
├── .env
└── .gitignore
```