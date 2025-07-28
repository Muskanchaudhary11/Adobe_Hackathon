import os
import json
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer

def split_soft_limit(paragraph, limit=400):
    if len(paragraph) <= limit:
        return [paragraph]

    result = []
    current = ""
    for sentence in paragraph.split('. '): 
        if len(current) + len(sentence) + 2 <= limit:
            current += sentence + '. '
        else:
            if current:
                result.append(current.strip())
            current = sentence + '. '
    if current:
        result.append(current.strip())
    return result

def process_pdfs_content(filename, path="./../input", output_path="./../output", para_limit=400):
    result = []
    pdf_path = os.path.join(path, filename)

    for page_num, layout in enumerate(extract_pages(pdf_path), start=1):
        paragraphs = []

        for element in layout:
            if isinstance(element, LTTextContainer):
                raw_text = element.get_text()
                cleaned_text = "\n".join(
                    [line.strip() for line in raw_text.splitlines() if line.strip()]
                )
                if cleaned_text:
                    split_paras = split_soft_limit(cleaned_text, para_limit)
                    paragraphs.extend(split_paras)

        if paragraphs:
            full_text = "\n\n".join(paragraphs)
            result.append({
                "document": filename,
                "page_number": page_num,
                "refined_text": full_text
            })

    
    return result
