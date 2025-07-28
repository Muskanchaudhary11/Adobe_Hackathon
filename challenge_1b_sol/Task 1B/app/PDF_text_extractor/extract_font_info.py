from pdfminer.layout import LTTextContainer, LTChar
from pdfminer.high_level import extract_pages

def extract_font_info(pdf_path):
    elements = []
    for page_num, layout in enumerate(extract_pages(pdf_path), start=1):
        for element in layout:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    if not hasattr(text_line, '__iter__'):
                        continue

                    font_sizes = [obj.size for obj in text_line if isinstance(obj, LTChar)]
                    if not font_sizes:
                        continue

                    avg_font_size = sum(font_sizes) / len(font_sizes)
                    text = text_line.get_text().strip()

                    if len(text) <= 2 and not any(c.isalnum() for c in text):
                        continue

                    if text:
                        elements.append({
                            "text": text,
                            "font_size": avg_font_size,
                            "page": page_num
                        })
    return elements
