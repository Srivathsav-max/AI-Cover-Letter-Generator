import streamlit as st
from .pdf_utils import extract_text_from_pdf, convert_text_to_pdf
from .llm_utils import build_cover_letter_prompt, generate_cover_letter_llm
from .text_utils import sanitize_cover_letter_text

def init_session_state():
    if 'cover_letter_generated' not in st.session_state:
        st.session_state.cover_letter_generated = False
    if 'cover_letter_content' not in st.session_state:
        st.session_state.cover_letter_content = ""
    if 'pdf_generated' not in st.session_state:
        st.session_state.pdf_generated = False

def render_ui():
    st.markdown(
        """
        <style>
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: transparent;
            color: #808080;
            text-align: center;
            padding: 10px;
            border-top: 1px solid #e5e5e5;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    init_session_state()
    
    st.title("AI-Powered Cover Letter Generator")
    st.markdown("""
    Upload your **PDF resume** and paste the **Job Description**.  
    Then click **Generate Cover Letter** to receive a properly-structured PDF.
    """)

    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    job_description = st.text_area("Paste Job Description Here", height=200)
    address = st.text_input("Company Address (Optional)", "")

    if st.button("Generate Cover Letter"):
        if not uploaded_file:
            st.warning("Please upload a PDF resume first.")
            return
        if not job_description.strip():
            st.warning("Please paste a job description.")
            return

        resume_text = extract_text_from_pdf(uploaded_file)
        prompt = build_cover_letter_prompt(resume_text, job_description, address)

        st.info("Generating cover letter. Please wait...")
        cover_letter_raw = generate_cover_letter_llm(prompt)
        if cover_letter_raw:
            cover_letter_clean = sanitize_cover_letter_text(cover_letter_raw)
            st.session_state.cover_letter_content = cover_letter_clean
            st.session_state.cover_letter_generated = True
            st.session_state.pdf_generated = False
        else:
            st.error("Failed to generate cover letter. Please try again.")

    if st.session_state.cover_letter_generated:
        st.success("Cover letter generated successfully!")
        st.write("### Preview and Edit:")

        edited_cover_letter = st.text_area(
            "Edit your cover letter here:",
            value=st.session_state.cover_letter_content,
            height=400,
            key="cover_letter_edit"
        )

        if st.button("Finalize and Generate PDF"):
            if edited_cover_letter:
                try:
                    pdf_bytes = convert_text_to_pdf(edited_cover_letter)
                    if pdf_bytes:
                        st.session_state.pdf_bytes = pdf_bytes
                        st.session_state.pdf_generated = True
                        st.session_state.cover_letter_content = edited_cover_letter
                        st.success("PDF generated successfully! Click below to download")
                    else:
                        st.error("Failed to generate PDF: Empty output")
                except Exception as e:
                    st.error(f"Failed to generate PDF: {str(e)}")

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

    st.markdown(
        '<div class="footer">Made with ❤️ by Srivathsav</div>',
        unsafe_allow_html=True
    )
