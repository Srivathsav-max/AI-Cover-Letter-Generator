import PyPDF2
from fpdf import FPDF
import streamlit as st

def extract_text_from_pdf(file_bytes):
    pdf_reader = PyPDF2.PdfReader(file_bytes)
    text_content = []
    for page in pdf_reader.pages:
        page_text = page.extract_text() or ""
        text_content.append(page_text)
    return "\n".join(text_content)

def convert_text_to_pdf(cover_letter_text):
    try:
        pdf = FPDF(format='A4')
        pdf.add_page()
        pdf.set_margins(left=25.4, top=25.4, right=25.4)
        
        pdf.set_font('Helvetica', '', 11)
        pdf.set_text_color(0, 0, 0)
        
        line_height = 6
        paragraph_spacing = 4
        y_position = pdf.get_y()
        
        for line in cover_letter_text.splitlines():
            if line.strip():
                encoded_line = line.encode('latin-1', errors='replace').decode('latin-1')
                pdf.set_y(y_position)
                pdf.multi_cell(0, line_height, encoded_line)
                y_position = pdf.get_y()
            else:
                y_position += paragraph_spacing
        
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
