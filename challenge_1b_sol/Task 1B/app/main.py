import os
import json
from datetime import datetime, timezone
from sentence_transformers import SentenceTransformer, util

from PDF_text_extractor.process_pdfs_headings import process_pdfs_headings
from PDF_text_extractor.process_pdfs_content import process_pdfs_content

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
model = SentenceTransformer(MODEL_NAME)

def build_heading_chunks(json_data, doc_name):
    chunks = []
    outline = json_data.get("outline", [])
    full_text = json_data.get("full_text", [])

    for i, section in enumerate(outline):
        heading = section.get("text")
        page = section.get("page", 0)
        end_page = outline[i + 1]["page"] if i + 1 < len(outline) else page + 1

        section_text = [
            item["refined_text"]
            for item in full_text
            if page <= item["page_number"] < end_page
        ]
        text = " ".join(section_text).strip()

        if not text:
            text = " ".join(
                item["refined_text"]
                for item in full_text
                if item["page_number"] == page
            )

        chunks.append({
            "source_doc": doc_name,
            "page": page + 1,
            "heading": heading,
            "text": text
        })

    return chunks

def build_paragraph_chunks(paragraphs):
    chunks = []
    for para in paragraphs:
        chunks.append({
            "source_doc": para["document"],
            "page": para["page_number"],
            "heading": f"Page {para['page_number']}",
            "text": para["refined_text"]
        })
    return chunks

def process_pdfs(filename, input_dir):
    pdf_path = os.path.join(input_dir, filename)

    # Try extracting with headings
    try:
        heading_json = process_pdfs_headings(filename, input_dir)
        if heading_json and heading_json.get("outline"):
            full_text = process_pdfs_content(filename, input_dir)
            heading_json["full_text"] = full_text
            return "heading", heading_json
    except Exception as e:
        print(f"❌ Failed heading extraction for {filename}: {e}")

    # Fallback to paragraph-only
    try:
        content_json = process_pdfs_content(filename, input_dir)
        return "content", content_json
    except Exception as e:
        print(f"❌ Failed content extraction for {filename}: {e}")
        return None, None

def rank_chunks(chunks, persona, job, top_k=5):
    if not chunks:
        print("⚠️ No chunks to rank.")
        return [], []

    combined_texts = [f"{c['heading']}: {c['text']}" for c in chunks]

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
            "document": chunk["source_doc"],
            "page": chunk["page"] - 1,
            "section_title": chunk["heading"],
            "importance_rank": rank,
            "score": round(score, 4)
        })
        sub_section_analysis.append({
            "document": chunk["source_doc"],
            "page": chunk["page"] - 1,
            "refined_text": chunk["text"]
        })

    return extracted_sections, sub_section_analysis

def process_collection(documents_meta, persona, job):
    all_chunks = []
    documents = []

    for doc in documents_meta:
        filename = doc["filename"]
        input_dir = "input"

        strategy, data = process_pdfs(filename, input_dir)

        if not data:
            print(f"⚠️ Skipping {filename}, no extractable content.")
            continue

        documents.append(filename)

        if strategy == "heading":
            chunks = build_heading_chunks(data, filename)
        else:
            chunks = build_paragraph_chunks(data)

        all_chunks.extend(chunks)

    extracted_sections, sub_section_analysis = rank_chunks(all_chunks, persona, job)
    
    return {
        "metadata": {
            "documents": documents,
            "persona": persona,
            "job_to_be_done": job,
            "timestamp": datetime.now(timezone.utc).isoformat()
        },
        "extracted_sections": extracted_sections,
        "sub_section_analysis": sub_section_analysis
    }

def main():
    input_dir = "./input"
    output_dir = "./output"
    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(input_dir, "input_data.json"), "r", encoding="utf-8") as f:
        config = json.load(f)

    persona = config["persona"]["role"]
    job = config["job_to_be_done"]["task"]
    documents_meta = config["documents"]
    challenge_id = config["challenge_info"]["challenge_id"]
    test_case_name = config["challenge_info"]["test_case_name"]

    result = process_collection(documents_meta, persona, job)

    output_path = os.path.join(output_dir, f"{challenge_id}_{test_case_name}_output.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()

extract_font_info.py

