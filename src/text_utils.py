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
