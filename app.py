import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import os
import json
import csv
from io import StringIO

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEM_API"))

# Initialize the model
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_flashcards(content, subject=None, difficulty="Medium", answer_size="Medium", count=10):
    """Generate flashcards using Gemini API"""
    prompt = f"""
    Generate {count} question-answer flashcards based on the following content.
    The subject is: {subject if subject else 'general knowledge'}.
    Difficulty level: {difficulty}.
    Answer size: {answer_size} (keep answers concise if 'Short', more detailed if 'Long').

    For each flashcard:
    - Question should be clear and test understanding
    - Answer should be accurate and self-contained
    - Format as "Q: [question]\nA: [answer]"

    Content:
    {content}
    """

    try:
        response = model.generate_content(prompt)
        return parse_flashcards(response.text)
    except Exception as e:
        st.error(f"Error generating flashcards: {e}")
        return []

def parse_flashcards(text):
    """Parse the generated text into flashcards"""
    flashcards = []
    current_q = None
    
    for line in text.split('\n'):
        line = line.strip()
        if line.startswith(('Q:', 'Question:')):
            if current_q:
                flashcards.append(current_q)
            current_q = {'question': line[2:].strip(), 'answer': ''}
        elif line.startswith(('A:', 'Answer:')):
            if current_q:
                current_q['answer'] = line[2:].strip()
                flashcards.append(current_q)
                current_q = None
        elif current_q:
            if current_q.get('answer', '') == '':
                current_q['question'] += ' ' + line
            else:
                current_q['answer'] += ' ' + line
    
    if current_q:
        flashcards.append(current_q)
    
    return flashcards

def export_flashcards(flashcards, format='json'):
    """Export flashcards in different formats"""
    if format == 'json':
        return json.dumps(flashcards, indent=2)
    elif format == 'csv':
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Question', 'Answer'])
        for card in flashcards:
            writer.writerow([card['question'], card['answer']])
        return output.getvalue()
    elif format == 'anki':
        output = StringIO()
        for card in flashcards:
            output.write(f"{card['question']}\t{card['answer']}\n")
        return output.getvalue()
    return ""

def main():
    st.set_page_config(
        page_title="Flashcard Generator",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    # Custom CSS for styling
    st.markdown("""
    <style>
        .main {
            max-width: 800px;
            padding: 2rem;
            background-color: #10E7DC;
            border-radius: 15px;
        }
        
        body {
            background-color: #f0f2f6;
        }
        
        .stApp {
            background-color: #f0f2f6;
        }

        .stTextArea textarea {
            background-color: white !important;
            border: 1px solid #ddd !important;
            border-radius: 8px !important;
            padding: 10px !important;
        }
        
        .stTextArea label {
            font-weight: bold !important;
            color: #333 !important;
            margin-bottom: 8px !important;
            display: block !important;
        }

        .stButton>button {
            width: 100%;
            background-color: #4CAF50;
            color: white;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: bold;
        }
        .stButton>button:hover {
            background-color: #45a049;
        }
        .stTextArea>div>div>textarea {
            min-height: 200px;
        }
        .flashcard {
            background: white;
            border-radius: 10px;
            padding: 1rem;
            margin: 0.5rem 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .flashcard-question {
            font-weight: bold;
            font-size: 1.1rem;
            margin-bottom: 0.5rem;
        }
        .success-message {
            color: #4CAF50;
            font-weight: bold;
            text-align: center;
            margin: 1rem 0;
        }
        /* Prevent layout shifts */
        .stSelectbox, .stDownloadButton {
            margin-top: 0.5rem;
        }
        /* Hide the selectbox label properly */
        [data-testid="stSelectbox"] label {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("<h1 style='text-align: center; color: white; background-color: #45a049; border-radius: 10px;'> LLM Powered Flashcard Generator</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Initialize session state for flashcards if not exists
    if 'flashcards' not in st.session_state:
        st.session_state.flashcards = []
    
    # Input section
    st.markdown("###  Enter Your Content")
    input_method = st.radio("", ["Text Input", "File Upload"], horizontal=True, key="input_method")
    
    content = ""
    if input_method == "Text Input":
        content = st.text_area(
            "Paste your book excerpt, chapter, or any educational content here...",
            height=250,
            placeholder="Type or paste your content here...",
            key="text_content"
        )
    else:
        uploaded_file = st.file_uploader("Upload a file", type=['txt', 'pdf'], key="file_uploader")
        if uploaded_file:
            if uploaded_file.type == 'text/plain':
                content = uploaded_file.read().decode('utf-8')
            else:
                st.warning("PDF parsing would require additional libraries like PyPDF2")
    
    # Customization options
    st.markdown("### ⚙️ Customization Options")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        difficulty = st.selectbox(
            "Difficulty Level",
            ["Easy", "Medium", "Hard"],
            index=1,
            key="difficulty"
        )
    
    with col2:
        flashcard_count = st.slider(
            "Number of Flashcards",
            10, 30, 15,
            key="flashcard_count"
        )
    
    with col3:
        subject = st.text_input(
            "Related Subject",
            placeholder="General",
            key="subject"
        )
    
    answer_size = st.selectbox(
        "Answer Size",
        ["Short (1 sentence)", "Medium", "Long (detailed)"],
        index=1,
        key="answer_size"
    )
    
    # Generate button
    if st.button("✨ Generate Flashcards", type="primary", key="generate_button"):
        if not content.strip():
            st.error("Please provide some content to generate flashcards")
        else:
            with st.spinner("Generating flashcards... This may take a moment"):
                st.session_state.flashcards = generate_flashcards(
                    content=content,
                    subject=subject,
                    difficulty=difficulty,
                    answer_size=answer_size,
                    count=flashcard_count
                )
    
    # Display flashcards if they exist
    if st.session_state.flashcards:
        st.markdown(f"<div class='success-message'>✅ Successfully generated {len(st.session_state.flashcards)} flashcards!</div>", unsafe_allow_html=True)
        
        st.markdown("### 📚 Generated Flashcards")
        for i, card in enumerate(st.session_state.flashcards, 1):
            with st.expander(f"Card {i}: {card['question']}", expanded=False):
                st.markdown(f"<div class='flashcard'><div class='flashcard-question'>Question:</div>{card['question']}<br><br><div class='flashcard-question'>Answer:</div>{card['answer']}</div>", unsafe_allow_html=True)
        
        # Export section with persistent format selection
        st.markdown("### 💾 Export Options")
        
        # Use columns to layout the format selector and download button
        col1, col2 = st.columns([1, 2])
        
        with col1:
            export_format = st.selectbox(
                "Select format",
                ["JSON", "CSV", "Anki"],
                key="export_format",
                label_visibility="collapsed"
            )
        
        with col2:
            # Generate the export data
            export_data = export_flashcards(st.session_state.flashcards, export_format.lower())
            
            # Create a unique key for the download button based on the format
            st.download_button(
                label=f"Download as {export_format}",
                data=export_data,
                file_name=f"flashcards.{export_format.lower()}",
                mime="text/plain" if export_format != 'json' else 'application/json',
                key=f"download_{export_format.lower()}"
            )

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #666; font-size: 0.9rem;">
            <p>LLM Powered FlashCard Generator by ABUBAKAR | Built with ❤️ using Gemini 2.0 Flash Lite</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()