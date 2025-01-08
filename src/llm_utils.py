import streamlit as st
from datetime import datetime
from .config import client, MODEL_NAME

def build_cover_letter_prompt(resume_text, job_description, address=""):
    current_date = datetime.now().strftime("%B %d, %Y")
    
    prompt = f"""
            You are an experienced cover letter writer with 20 years of expertise, known for creating highly impactful and personalized cover letters. Your goal is to craft a compelling and professional cover letter that aligns with the candidate's resume, technical skills, and achievements while directly addressing the requirements and values outlined in the job description.

            Memorize all the information provided in the resume and job description to create a cohesive narrative that showcases the candidate's qualifications, enthusiasm, and fit for the role. Adhere to all standard cover letter rules, formatting requirements, and professional tone guidelines.

            **Header:**
            1) Candidate's Full Name (formatted as bold text, with each word capitalized, on its own line).
            2) Candidate's Email (formatted as: Email: [email_address],formatted as bold text, on its own line).
            3) Candidate's Phone Number (formatted as: Phone: [phone_number],formatted as bold text, on its own line).
            new line
            4) Date (formatted as: Date: {current_date}, on its own line).
            new line
            5) Company Name (extracted from the job description and written clearly on its own line).
            new line
            {f"6) Company Address (on its own line)." if address else ""}
            7) Greeting Line (choose the appropriate greeting based on the job description, e.g., "Dear Hiring Manager," or "Dear [Specific Name],").
            **Body:**
            1) Introduction (1 paragraph): A concise and engaging opening that highlights why the candidate is excited about the role and company. Mention the specific position and briefly touch on how their skills and experiences align with the job description.

            2) Main Body (1 paragraph): Expand on key achievements, skills, and experiences from the resume that are relevant to the job description. Emphasize how the candidate's background can address the company's needs or solve specific challenges. Use metrics or quantifiable results where possible.

            3) Conclusion (1 paragraph): Reiterate enthusiasm for the role, express interest in contributing to the company, and include a call to action (e.g., willingness to discuss further in an interview). 

            **Closing:**
            - "Sincerely," on its own line.
            - Candidate's Full Name (typed, on the next line).

            **Total Length:** 150–250 words.

            **Instructions:**
            - Tailor the language and content to reflect the tone and keywords of the job description.
            - Focus on relevance, clarity, and professionalism.
            - Ensure seamless integration of details from the resume into the narrative.

            **Job Description:**
            --------------------
            {job_description}
            --------------------

            **Resume:**
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
