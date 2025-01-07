import streamlit as st
from datetime import datetime
from .config import client, MODEL_NAME

def build_cover_letter_prompt(resume_text, job_description, address=""):
    current_date = datetime.now().strftime("%B %d, %Y")
    address_instruction = "Company Address (on its own line)." if address else ""
    
    prompt = f"""
    You are a professional cover letter writer with 20 years of experience. with lots of achievents in writing cover letter.
    memorize all the informations and use them to write the cover letter according to every rule it need to follow.

    Create a structured cover letter with these exact lines for the header:
    1) My Name (on its own line, first letter of each word capitalized and complete name need to be bold).
    2) My Email (on its own line in proper formate like Email: [Email Address]).
    3) My Phone Number (on its own line in proper formate like Phone: [Phone Number]).
    new line
    4) Date: {current_date}
    new line
    5) Company Name (on its own line).
    {f"6) Company Address (on its own line)." if address else ""}
    new line
    7) A greeting line, e.g. "Dear Hiring Manager," or "Dear <Name>," on its own line.

    After the greeting, produce multiple paragraphs (separated by exactly one blank line)
    for the introduction, main body, and conclusion. Conclude with:
    - "Sincerely," on a line by itself
    - My typed name (on the next line)

    Total length: 150-250 words.

    JOB DESCRIPTION:
    --------------------
    {job_description}
    --------------------

    RESUME:
    --------------------
    {resume_text}
    --------------------
    """
    return prompt.strip()

def generate_cover_letter_llm(prompt):
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            top_p=0.9,
            max_tokens=1024,
            stream=False
        )
        cover_letter = response.choices[0].message.content
        return cover_letter.strip()
    except Exception as e:
        st.error(f"Error generating cover letter: {e}")
        return ""
