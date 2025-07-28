import os
import json
import re
from typing import List, Dict
from datetime import datetime, timezone
from sentence_transformers import SentenceTransformer, util

from PDF_text_extractor.process_pdfs_headings import process_pdfs_headings
from PDF_text_extractor.process_pdfs_content import process_pdfs_content

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
model = SentenceTransformer(MODEL_NAME)

def process_pdfs(filename, input_dir):
    pdf_path = os.path.normpath(os.path.join(input_dir, filename))

    try:
        heading_json = process_pdfs_headings(filename, input_dir)
        if heading_json and heading_json.get("outline"):
            full_text_content = process_pdfs_content(filename, input_dir)
            heading_json["full_text_paragraphs"] = full_text_content.get("paragraphs", [])
            return "heading_and_content", heading_json
    except Exception as e:
        print(f"❌ Failed heading extraction for {filename}: {e}")

    try:
        content_json = process_pdfs_content(filename, input_dir)
        return "content_only", content_json
    except Exception as e:
        print(f"❌ Failed content extraction for {filename}: {e}")
        return None, None

def rank_chunks(chunks, persona, job, top_k=5):
    
    if not chunks:
        print("⚠️ No chunks to rank.")
        return [], []

    combined_texts = []
    for c in chunks:
        if c.get("type") == "heading":
            combined_texts.append(f"{c.get('text', '')}") 
        else:
            combined_texts.append(f"{c.get('text', '')}")

    if not combined_texts:
        print("⚠️ No valid texts to embed from chunks.")
        return [], []

    chunk_embeddings = model.encode(
        combined_texts,
        normalize_embeddings=True,
        batch_size=16,
        show_progress_bar=False
    )

    query = f"As a {persona}, {job}"
    query_embedding = model.encode(query, normalize_embeddings=True)

    scores = util.dot_score(query_embedding, chunk_embeddings)[0].cpu().tolist()
    ranked = sorted(zip(chunks, scores), key=lambda x: -x[1])[:top_k]

    extracted_sections = []
    sub_section_analysis = []

    for rank, (chunk, score) in enumerate(ranked, 1):
        extracted_sections.append({
            "document": chunk["source"], 
            "page": chunk["page"],       
            "section_title": chunk.get("text", "N/A"), 
            "importance_rank": rank,
            "score": round(score, 4)
        })
        sub_section_analysis.append({
            "document": chunk["source"], 
            "page": chunk["page"],       
            "refined_text": chunk["text"]
        })

    return extracted_sections, sub_section_analysis

def build_heading_chunks(heading_data: Dict, filename: str) -> List[Dict]:
    outline = heading_data.get("outline", [])
    chunks = []

    for item in outline:
        chunk = {
            "type": "heading",
            "source": filename,
            "text": item.get("text", "").strip(),
            "level": item.get("level", "H2"),
            "page": item.get("page", -1),
            "metadata": {
                "filename": filename,
                "page": item.get("page", -1),
                "level": item.get("level", "H2")
            }
        }
        chunks.append(chunk)

    return chunks

def build_paragraph_chunks(paragraph_data: Dict[str, List[Dict]], filename: str) -> List[Dict]:
    
    paragraphs_list = paragraph_data.get("paragraphs", [])
    chunks = []

    for item in paragraphs_list:
        text = item.get("text", "").strip()
        page = item.get("page", -1)
        words = text.split()

        if len(words) < 15:
            continue
        list_or_heading_pattern = r'^\s*((\d+\.?\d*\.?)|([A-Za-z]\.?)|([IVXLCDM]+\.?))\s+.*'
        if re.match(list_or_heading_pattern, text) and len(words) < 25: 
            continue

        if len(words) < 20: 
            if text.isupper() and any(c.isalpha() for c in text):
                continue
            if text.istitle() and len(words) < 10:
                continue
            if len(text) < 50:
                continue
        if re.match(r'^\s*\d+\s*$', text) or re.match(r'^\s*[A-Za-z]\s*$', text): 
            continue

        if not any(c.isalpha() for c in text) and len(text) > 5: 
            continue

        chunk = {
            "type": "paragraph",
            "source": filename,
            "text": text,
            "page": page,
            "metadata": {
                "filename": filename,
                "page": page
            }
        }
        chunks.append(chunk)
    return chunks


def process_collection(documents_meta, persona, job, input_dir):
    all_heading_chunks = []
    all_paragraph_chunks = []
    processed_documents = []

    for doc_meta in documents_meta:
        filename = doc_meta["filename"]
        processed_documents.append(filename)

        doc_type, doc_data = process_pdfs(filename, input_dir)

        if doc_type == "heading_and_content":
            if doc_data.get("outline"):
                all_heading_chunks.extend(build_heading_chunks(doc_data, filename))
            if doc_data.get("full_text_paragraphs"):
                all_paragraph_chunks.extend(build_paragraph_chunks({"paragraphs": doc_data["full_text_paragraphs"]}, filename))
        elif doc_type == "content_only":
            if doc_data.get("paragraphs"):
                all_paragraph_chunks.extend(build_paragraph_chunks(doc_data, filename))
        else:
            print(f"Skipping document {filename} due to processing failure.")

    top_headings, _ = rank_chunks(all_heading_chunks, persona, job)
    top_paragraphs, _ = rank_chunks(all_paragraph_chunks, persona, job)

    return {
        "metadata": {
            "input_documents": processed_documents,
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": datetime.now(timezone.utc).isoformat()
        },
        "extracted_sections": top_headings,
        "subsection_analysis": top_paragraphs
    }

def main():
    input_dir = "./input"
    output_dir = "./output"
    os.makedirs(output_dir, exist_ok=True)

    input_data_path = os.path.join(input_dir, "input_data.json")
    if not os.path.exists(input_data_path):
        print(f"Creating dummy {input_data_path}")
        dummy_config = {
            "persona": {"role": "researcher"},
            "job_to_be_done": {"task": "find key insights on climate change"},
            "documents": [{"filename": "example1.pdf"}],
            "challenge_info": {"challenge_id": "test_challenge", "test_case_name": "basic_test"}
        }
        with open(input_data_path, "w", encoding="utf-8") as f:
            json.dump(dummy_config, f, indent=2)

    with open(input_data_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    persona = config["persona"]["role"]
    job = config["job_to_be_done"]["task"]
    documents_meta = config["documents"]
    challenge_id = config["challenge_info"]["challenge_id"]
    test_case_name = config["challenge_info"]["test_case_name"]

    result = process_collection(documents_meta, persona, job, input_dir)

    output_path = os.path.join(output_dir, f"{challenge_id}_{test_case_name}_output.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Output saved to {output_path}")

if __name__ == "__main__":
    main()
