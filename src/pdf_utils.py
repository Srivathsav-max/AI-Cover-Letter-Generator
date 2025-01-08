import PyPDF2
from fpdf import FPDF
import streamlit as st
from .text_utils import parse_bold_markers

def extract_text_from_pdf(file_bytes):
    pdf_reader = PyPDF2.PdfReader(file_bytes)
    text_content = []
    for page in pdf_reader.pages:
        page_text = page.extract_text() or ""
        text_content.append(page_text)
    return "\n".join(text_content)

def convert_text_to_pdf(cover_letter_text):
    try:
        # Initialize PDF with A4 format (measurements in mm)
        pdf = FPDF(format='A4')
        pdf.add_page()
        
        # Standard A4 margins (25.4mm = 1 inch)
        margin = 25.4
        pdf.set_margins(left=margin, top=margin, right=margin)
        pdf.set_auto_page_break(auto=True, margin=margin)
        
        # Set effective width for text (A4 width = 210mm)
        effective_page_width = 210 - (2 * margin)
        
        # Add Times New Roman font
        pdf.add_font('Times', '', 'times.ttf', uni=True)
        pdf.add_font('Times', 'B', 'timesb.ttf', uni=True)
        
        pdf.set_font('Times', '', 11)
        pdf.set_text_color(0, 0, 0)
        
        line_height = 6
        paragraph_spacing = 4
        y_position = pdf.get_y()
        left_margin = pdf.l_margin
        
        for line in cover_letter_text.splitlines():
            if line.strip():
                formatted_parts = parse_bold_markers(line)
                
                x_position = left_margin
                pdf.set_y(y_position)
                
                # Check if we need to add a new page
                if y_position > 297 - margin:  # 297mm is A4 height
                    pdf.add_page()
                    y_position = pdf.get_y()
                
                for text, is_bold in formatted_parts:
                    pdf.set_x(x_position)
                    pdf.set_font('Times', 'B' if is_bold else '', 11)
                    encoded_text = text.encode('latin-1', errors='replace').decode('latin-1')
                    width = pdf.get_string_width(encoded_text)
                    
                    # Check if we need to wrap text
                    if x_position - left_margin + width > effective_page_width:
                        y_position += line_height
                        pdf.set_y(y_position)
                        x_position = left_margin
                        pdf.set_x(x_position)
                    
                    pdf.write(line_height, encoded_text)
                    x_position += width
                
                y_position = pdf.get_y() + line_height
            else:
                y_position += paragraph_spacing
            
            pdf.set_y(y_position)
        
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
