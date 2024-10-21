import streamlit as st
from openai import OpenAI
import os
from PyPDF2 import PdfReader
import random

open_ai_key = st.secrets["open_ai_key"]["key"]

client = OpenAI(api_key=os.environ['open_ai_key'])

# Function to extract text from specific pages in a PDF
def extract_text_from_pdf(pdf, start_page, end_page):
    try:
        reader = PdfReader(pdf)
        text = ""
        for page_num in range(start_page - 1, end_page):
            text += reader.pages[page_num].extract_text()
        return text
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"


# Function to generate a question using OpenAI API with gpt-4o-mini
def generate_question(course_content, question_type="mcq", difficulty="medium"):
    prompt = f"Generate a {difficulty} {question_type} question based on this course content: {course_content}. Do not provide the answer or any explanation for any of the questions."
    try:
        # Using the correct method for chat completion
        chat_completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return chat_completion
    except Exception as e:
        return f"Error generating question: {str(e)}"

# Function to generate the PDF with the required questions
def generate_question_paper(course_text):
    # Shuffle difficulties
    difficulties = ['easy', 'medium', 'hard']
    tokens_used = []
    # Generate 5 MCQs
    mcqs = []
    for _ in range(5):
        difficulty = random.choice(difficulties)
        mcq = generate_question(course_text, question_type="mcq", difficulty=difficulty)
        mcq_content = mcq.choices[0].message.content
        mcqs.append(mcq_content)
        tokens_used.append(mcq.usage.total_tokens)

    # Generate 2 six-mark questions
    six_mark_questions = []
    for _ in range(2):
        difficulty = random.choice(difficulties)
        six_mark_question = generate_question(course_text, question_type="long", difficulty=difficulty)
        six_mark_question_content = six_mark_question.choices[0].message.content
        six_mark_questions.append(six_mark_question_content)
        tokens_used.append(six_mark_question.usage.total_tokens)

    # Generate 2 eighteen-mark questions
    eighteen_mark_questions = []
    for _ in range(2):
        difficulty = random.choice(difficulties)
        eighteen_mark_question = generate_question(course_text, question_type="long", difficulty=difficulty)
        eighteen_mark_question_content = eighteen_mark_question.choices[0].message.content
        eighteen_mark_questions.append(eighteen_mark_question_content)
        tokens_used.append(eighteen_mark_question.usage.total_tokens)

    # Prepare the output
    return {
        "mcqs": mcqs,
        "six_mark_questions": six_mark_questions,
        "eighteen_mark_questions": eighteen_mark_questions,
        "tokens_used":tokens_used
    }

# Streamlit App UI

st.title("Question Paper Generator")

# File Upload for PDF
uploaded_pdf = st.file_uploader("Upload your course book PDF", type="pdf")

if uploaded_pdf:
    # Take input for start and end page numbers
    start_page = st.number_input("Enter the start page number:", min_value=1, step=1)
    end_page = st.number_input("Enter the end page number:", min_value=start_page, step=1)
    
    if st.button("Generate Question Paper"):
        # Extract text from PDF
        course_text = extract_text_from_pdf(uploaded_pdf, start_page, end_page)
        
        if "Error" in course_text:
            st.error(course_text)  # Show the error if there's an issue with the extraction
        else:
            # Generate question paper
            question_paper = generate_question_paper(course_text)
            
            # Display Tokens Used
            st.subheader("Total Tokens Used")
            st.write(sum(question_paper['tokens_used']))


            # Display MCQs
            st.subheader("Multiple Choice Questions (5):")
            for i, mcq in enumerate(question_paper['mcqs'], 1):
                st.write(f"{i}. {mcq}")
            
            # Display Six-Mark Questions
            st.subheader("Six-Mark Questions (2):")
            for i, question in enumerate(question_paper['six_mark_questions'], 1):
                st.write(f"{i}. {question}")
            
            # Display Ten-Mark Questions
            st.subheader("Ten-Mark Questions (2):")
            for i, question in enumerate(question_paper['eighteen_mark_questions'], 1):
                st.write(f"{i}. {question}")