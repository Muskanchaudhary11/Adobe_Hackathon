import fitz
import os
import json

def process_pdfs_headings(filename: str, path: str) -> dict:
    file_path = os.path.join(path, filename)
    headings = []

    try:
        doc = fitz.open(file_path)
    except Exception as e:
        return {"error": f"Failed to open PDF: {str(e)}"}

    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span.get("text", "").strip()
                    size = span.get("size", 0)
                    flags = span.get("flags", 0)

                    if (
                        len(text) > 2 and
                        not text.isnumeric() and
                        (size > 12 or (flags & 16))  
                    ):
                        headings.append({
                            "text": text,
                            "size": size,
                            "page": page_num
                        })

    doc.close()

    output = {
        "title": "",
        "outline": []
    }

    if headings:
        main_title = max(headings, key=lambda h: h["size"])
        output["title"] = main_title["text"]
        headings.remove(main_title)

        for h in headings:
            output["outline"].append({
                "level": "H2", 
                "text": h["text"],
                "page": h["page"]
            })

    return output
