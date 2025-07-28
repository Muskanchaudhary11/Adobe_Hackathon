import os
import re
from typing import List, Dict
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer


def split_soft_limit(paragraph: str, limit: int = 400) -> List[str]:
    if len(paragraph) <= limit:
        return [paragraph]

    result = []
    current_chunk = ""
    # Break using sentence boundaries
    sentences = re.split(r'(?<=[.!?])(?=\s+\S)', paragraph)

    for i, sentence in enumerate(sentences):
        sentence = sentence.strip()
        # Ensure sentence ends properly
        if i < len(sentences) - 1 and not sentence.endswith(('.', '!', '?')):
            sentence += '.'

        # Check chunk length before appending
        potential_chunk = (current_chunk + " " + sentence).strip() if current_chunk else sentence
        if len(potential_chunk) <= limit:
            current_chunk = potential_chunk
        else:
            if current_chunk:
                result.append(current_chunk)
            current_chunk = sentence

    if current_chunk:
        result.append(current_chunk)

    return result


def process_pdfs_content(filename: str, input_dir: str = "./input", para_limit: int = 400) -> Dict[str, List[Dict]]:
    paragraphs_data = []
    pdf_path = os.path.join(input_dir, filename)

    if not os.path.isfile(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return {"paragraphs": []}

    try:
        for page_num, layout in enumerate(extract_pages(pdf_path), start=1):
            for element in layout:
                if isinstance(element, LTTextContainer):
                    raw_text = element.get_text()
                    # Clean and normalize lines
                    cleaned_text = "\n".join(
                        [line.strip() for line in raw_text.splitlines() if line.strip()]
                    ).strip()

                    if cleaned_text:
                        split_paragraphs = split_soft_limit(cleaned_text, limit=para_limit)
                        for para in split_paragraphs:
                            if para:
                                paragraphs_data.append({
                                    "text": para,
                                    "page": page_num
                                })
    except Exception as e:
        print(f"❌ Error processing {filename}: {e}")
        return {"paragraphs": []}

    return {"paragraphs": paragraphs_data}
