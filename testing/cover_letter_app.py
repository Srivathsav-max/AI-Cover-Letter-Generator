import os
from dotenv import load_dotenv
import streamlit as st
from openai import OpenAI
import PyPDF2
from fpdf import FPDF

# Load environment variables
load_dotenv()

# ---------------------------------------------------------------------
# 1. Initialize NVIDIA / OpenAI-Compatible Client
# ---------------------------------------------------------------------
client = OpenAI(
    base_url=os.getenv('NVIDIA_API_BASE_URL'),
    api_key=os.getenv('NVIDIA_API_KEY')
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
# 3. Build a Prompt Enforcing Line-by-Line Header + Multi-Paragraph Body
# ---------------------------------------------------------------------
def build_cover_letter_prompt(resume_text, job_description):
    prompt = f"""
                You are a professional cover letter writer with 20 years of experience. with lots of achievents in writing cover letter.
                memorize all the informations and use them to write the cover letter according to every rule it need to follow.

                Create a structured cover letter with these exact lines for the header:
                1) My Name (on its own line, first letter of each word capitalized and complete name need to be bold).
                2) My Email (on its own line in proper formate like Email: [Email Address]).
                3) My Phone Number (on its own line in proper formate like Phone: [Phone Number]).
                new line
                4) The Date (on its own line in proper formate like Date: [Date]).
                new line
                5) Company Name and Address (on its own line).
                new line
                6) A greeting line, e.g. "Dear Hiring Manager," or "Dear <Name>," on its own line.

                After the greeting, produce multiple paragraphs (separated by exactly one blank line)
                for the introduction, main body, and conclusion. Conclude with:
                - "Sincerely," on a line by itself
                - My typed name (on the next line)

                Total length: 150-250 words. don't over do it.
                Highlight relevant skills from my resume to address responsibilities from the job description.
                Do not lump everything into a single paragraph; separate them with line breaks and blank lines.

                JOB DESCRIPTION:
                --------------------
                {job_description}
                --------------------

                RESUME:
                --------------------
                {resume_text}
                --------------------

                Now produce the final cover letter text with each header piece on its own line
                and multi-paragraph body, no extra commentary:
            """
    return prompt.strip()

# ---------------------------------------------------------------------
# 4. Generate Cover Letter from NVIDIA LLM
# ---------------------------------------------------------------------
def generate_cover_letter_llm(prompt):
    try:
        response = client.chat.completions.create(
            model=os.getenv('MODEL_NAME'),
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

# ---------------------------------------------------------------------
# 5. Sanitize Text: Keep Paragraph Breaks, Limit Extra Blank Lines
# ---------------------------------------------------------------------
def sanitize_cover_letter_text(cover_letter: str) -> str:
    """
    1. Split on lines
    2. Trim trailing spaces
    3. Collapse consecutive blank lines to just one
    """
    lines = cover_letter.splitlines()
    cleaned_lines = []
    blank_count = 0

    for line in lines:
        if not line.strip():
            # It's a blank line
            blank_count += 1
            if blank_count <= 1:
                # Only keep one blank line in a row
                cleaned_lines.append("")
        else:
            blank_count = 0
            cleaned_lines.append(line.strip())

    return "\n".join(cleaned_lines)

# ---------------------------------------------------------------------
# 6. Convert Text to PDF - Handling "Not enough horizontal space..."
# ---------------------------------------------------------------------
def convert_text_to_pdf(cover_letter_text):
    """
    Fixed PDF generation with Sans Serif font and reduced spacing
    """
    try:
        pdf = FPDF(format='A4')
        pdf.add_page()
        pdf.set_margins(left=25.4, top=25.4, right=25.4)  #
        
        # Use Helvetica (Sans Serif) font
        pdf.set_font('Helvetica', '', 11)
        pdf.set_text_color(0, 0, 0)
        
        # Reduced line spacing settings
        line_height = 6  # Reduced from 8
        paragraph_spacing = 4  # Reduced from 8
        max_len = 80
        
        # Set initial Y position
        y_position = pdf.get_y()
        
        # Process each line with reduced spacing
        for line in cover_letter_text.splitlines():
            if line.strip():
                # Clean and encode the text
                encoded_line = line.encode('latin-1', errors='replace').decode('latin-1')
                pdf.set_y(y_position)
                pdf.multi_cell(0, line_height, encoded_line)
                y_position = pdf.get_y()
            else:
                # Reduced space for empty lines
                y_position += paragraph_spacing
        
        # Generate PDF output
        try:
            output = pdf.output(dest='S').encode('latin-1')
            if len(output) < 100:
                raise Exception("Generated PDF seems too small to be valid")
            return output
        except Exception as e:
            raise Exception(f"Failed to generate PDF output: {str(e)}")
    
    except Exception as e:
        st.error(f"PDF Generation Error: {str(e)}")
        raise e

# ---------------------------------------------------------------------
# 7. Streamlit UI
# ---------------------------------------------------------------------
def main():
    # Initialize session state
    if 'cover_letter_generated' not in st.session_state:
        st.session_state.cover_letter_generated = False
    if 'cover_letter_content' not in st.session_state:
        st.session_state.cover_letter_content = ""
    if 'pdf_generated' not in st.session_state:
        st.session_state.pdf_generated = False

    st.title("AI-Powered Cover Letter Generator")
    st.markdown("""
                Upload your **PDF resume** and paste the **Job Description**.  
                Then click **Generate Cover Letter** to receive a properly-structured PDF.
                """
                )

    # Resume Upload and Job Description sections remain the same
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    job_description = st.text_area("Paste Job Description Here", height=200)

    # Generate Button
    if st.button("Generate Cover Letter"):
        if not uploaded_file:
            st.warning("Please upload a PDF resume first.")
            return
        if not job_description.strip():
            st.warning("Please paste a job description.")
            return

        resume_text = extract_text_from_pdf(uploaded_file)
        prompt = build_cover_letter_prompt(resume_text, job_description)

        st.info("Generating cover letter. Please wait...")
        cover_letter_raw = generate_cover_letter_llm(prompt)
        if cover_letter_raw:
            cover_letter_clean = sanitize_cover_letter_text(cover_letter_raw)
            st.session_state.cover_letter_content = cover_letter_clean
            st.session_state.cover_letter_generated = True
            st.session_state.pdf_generated = False
        else:
            st.error("Failed to generate cover letter. Please try again.")

    # Show preview and edit section if cover letter was generated
    if st.session_state.cover_letter_generated:
        st.success("Cover letter generated successfully!")
        st.write("### Preview and Edit:")

        edited_cover_letter = st.text_area(
            "Edit your cover letter here:",
            value=st.session_state.cover_letter_content,
            height=400,
            key="cover_letter_edit"
        )

        # Finalize and Generate PDF
        if st.button("Finalize and Generate PDF"):
            if edited_cover_letter:
                try:
                    pdf_bytes = convert_text_to_pdf(edited_cover_letter)
                    if pdf_bytes:
                        st.session_state.pdf_bytes = pdf_bytes
                        st.session_state.pdf_generated = True
                        st.session_state.cover_letter_content = edited_cover_letter
                        st.success("PDF generated successfully! Click below download")
                    else:
                        st.error("Failed to generate PDF: Empty output")
                except Exception as e:
                    st.error(f"Failed to generate PDF: {str(e)}")

        # Show download button if PDF was generated
        if st.session_state.pdf_generated:
            st.download_button(
                label="Download Cover Letter as PDF",
                data=st.session_state.pdf_bytes,
                file_name="cover_letter.pdf",
                mime="application/pdf"
            )

        if st.button("Start Over"):
            st.session_state.cover_letter_generated = False
            st.session_state.cover_letter_content = ""
            st.session_state.pdf_generated = False
            st.experimental_rerun()

if __name__ == "__main__":
    main()