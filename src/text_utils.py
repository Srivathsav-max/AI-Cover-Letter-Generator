def parse_bold_markers(text: str) -> list:
    parts = []
    current_text = ""
    is_bold = False
    i = 0
    
    while i < len(text):
        if i < len(text) - 1 and text[i:i+2] == "**":
            if current_text:
                parts.append((current_text, is_bold))
                current_text = ""
            is_bold = not is_bold
            i += 2
        else:
            current_text += text[i]
            i += 1
            
    if current_text:
        parts.append((current_text, is_bold))
    
    return parts

def sanitize_cover_letter_text(cover_letter: str) -> str:
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
