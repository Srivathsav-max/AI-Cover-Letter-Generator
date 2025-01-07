import os
import subprocess
import tempfile

import streamlit as st
import PyPDF2

# If you're using Nvidia's endpoint (OpenAI-compatible):
from openai import OpenAI

# ---------------------------------------------------------------------
# 1. Initialize NVIDIA / OpenAI-Compatible Client
# ---------------------------------------------------------------------
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",  # or your chosen endpoint
    api_key="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"
)

# ---------------------------------------------------------------------
# 2. Extract PDF Text
# ---------------------------------------------------------------------
def extract_text_from_pdf(file_bytes):
    pdf_reader = PyPDF2.PdfReader(file_bytes)
    text_content = []
    for page in pdf_reader.pages:
        page_text = page.extract_text() or ""
        text_content.append(page_text)
    return "\n".join(text_content)

# ---------------------------------------------------------------------
# 3. Build the Prompt
# ---------------------------------------------------------------------
def build_cover_letter_prompt(resume_text, job_description):
    prompt = f"""
        You are a professional cover letter writer with 20 years of experience and many achievements.

        Create a structured cover letter with these exact lines for the header:
        1) My Name (on its own line, first letter of each word capitalized and complete name in **bold**).
        2) My Email (on its own line, like "Email: <address>").
        3) My Phone (on its own line, like "Phone: <number>").
        (blank line)
        4) The Date (like "Date: January 1, 2025").
        (blank line)
        5) Company Name and Address (on its own line).
        (blank line)
        6) A greeting line, e.g. "Dear Hiring Manager," or "Dear <Name>,"

        Then multiple paragraphs for introduction, main body, conclusion (150-250 words total).
        End with:
           Sincerely,
           My typed name

        JOB DESCRIPTION:
        {job_description}

        RESUME:
        {resume_text}

        Output the cover letter text with exactly those lines in the header, then paragraphs, etc.
        No extra commentary. 
    """
    return prompt.strip()

# ---------------------------------------------------------------------
# 4. Generate Cover Letter from the LLM
# ---------------------------------------------------------------------
def generate_cover_letter_llm(prompt):
    try:
        response = client.chat.completions.create(
            model="meta/llama-3.3-70b-instruct",  # or whichever model you have
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            top_p=0.9,
            max_tokens=1024,
            stream=False
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error generating cover letter: {e}")
        return ""

# ---------------------------------------------------------------------
# 5. Sanitize the Cover Letter
# ---------------------------------------------------------------------
def sanitize_cover_letter_text(cover_letter: str) -> str:
    # Remove extra blank lines, trim spaces
    lines = cover_letter.splitlines()
    cleaned_lines = []
    blank_count = 0
    for line in lines:
        if not line.strip():
            blank_count += 1
            if blank_count <= 1:
                cleaned_lines.append("")
        else:
            blank_count = 0
            cleaned_lines.append(line.strip())
    return "\n".join(cleaned_lines)

# ---------------------------------------------------------------------
# 6. Compile the LaTeX to PDF
# ---------------------------------------------------------------------
def compile_latex_to_pdf(cover_letter_body: str) -> bytes:
    """
    1. Reads the template from cover_letter_template.tex
    2. Replaces {{LETTER_BODY_PLACEHOLDER}} with the AI-generated text
    3. Calls pdflatex to compile
    4. Returns PDF bytes
    """
    # Load the Awesome CV cover letter template
    template_path = "/Users/jayarajsrivathsavadari/Desktop/job-application-automation/cover_letter_template.tex"
    if not os.path.exists(template_path):
        raise FileNotFoundError("cover_letter_template.tex not found. Please ensure it's in the same directory.")

    with open(template_path, "r", encoding="utf-8") as f:
        template_text = f.read()

    # Insert the AI-generated body
    populated_text = template_text.replace("{{LETTER_BODY_PLACEHOLDER}}", cover_letter_body)

    # Create a temp folder to compile the PDF
    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = os.path.join(tmpdir, "cover_letter.tex")
        pdf_path = os.path.join(tmpdir, "cover_letter.pdf")

        # Write the new .tex file
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(populated_text)

        # Run pdflatex (twice if you want to ensure references, but once may suffice)
        subprocess.run(
            ["xelatex", "-interaction=nonstopmode", tex_path],
            cwd=tmpdir,
            check=True
        )

        # Read the PDF
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

    return pdf_bytes

# ---------------------------------------------------------------------
# 7. Streamlit UI
# ---------------------------------------------------------------------
def main():
    st.title("AI-Powered Cover Letter Generator (Awesome CV Edition)")
    st.markdown("""
    **Instructions**:
    1. Upload your PDF resume below.
    2. Paste the job description.
    3. Click "Generate Cover Letter" to get an AI-drafted letter.
    4. Edit if needed, then "Finalize and Generate PDF" to compile the Awesome CV PDF.
    """)

    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    job_description = st.text_area("Paste Job Description Here", height=200)

    if 'cover_letter_generated' not in st.session_state:
        st.session_state.cover_letter_generated = False
    if 'cover_letter_content' not in st.session_state:
        st.session_state.cover_letter_content = ""
    if 'pdf_bytes' not in st.session_state:
        st.session_state.pdf_bytes = b""

    if st.button("Generate Cover Letter"):
        if not uploaded_file:
            st.warning("Please upload a PDF resume first.")
            return
        if not job_description.strip():
            st.warning("Please paste a job description.")
            return

        # Extract text from resume
        resume_text = extract_text_from_pdf(uploaded_file)

        # Build prompt & call LLM
        prompt = build_cover_letter_prompt(resume_text, job_description)
        st.info("Generating cover letter. Please wait...")
        cover_letter_raw = generate_cover_letter_llm(prompt)
        if cover_letter_raw:
            cover_letter_clean = sanitize_cover_letter_text(cover_letter_raw)
            st.session_state.cover_letter_content = cover_letter_clean
            st.session_state.cover_letter_generated = True
            st.success("Cover letter generated successfully!")
        else:
            st.error("Failed to generate cover letter. Please try again.")

    # If we have a generated cover letter
    if st.session_state.cover_letter_generated:
        st.write("### Preview / Edit Your Cover Letter")
        edited_cover_letter = st.text_area(
            "Make changes if needed:",
            value=st.session_state.cover_letter_content,
            height=400
        )

        if st.button("Finalize and Generate PDF"):
            try:
                pdf_bytes = compile_latex_to_pdf(edited_cover_letter)
                st.session_state.pdf_bytes = pdf_bytes
                st.success("PDF generated successfully! Download below.")
            except subprocess.CalledProcessError as e:
                st.error(f"LaTeX compilation failed: {e}")
            except Exception as e:
                st.error(f"PDF generation error: {e}")

        # If PDF bytes are available, show download button
        if st.session_state.pdf_bytes:
            st.download_button(
                "Download Cover Letter as PDF",
                data=st.session_state.pdf_bytes,
                file_name="cover_letter.pdf",
                mime="application/pdf"
            )

        if st.button("Start Over"):
            # Clear states
            st.session_state.cover_letter_generated = False
            st.session_state.cover_letter_content = ""
            st.session_state.pdf_bytes = b""
            st.experimental_rerun()

if __name__ == "__main__":
    main()