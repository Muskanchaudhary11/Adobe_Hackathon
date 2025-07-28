# 📄 Adobe Hackathon 2025 – Challenge 1B  
## 🤖 Persona-Aware PDF Section Extractor (Offline + CPU-Only)

---

## 📘 Introduction

In Round 2 of the Adobe Hackathon 2025, Challenge 1B asked participants to go beyond document structure and build a system that intelligently **extracts the most relevant sections from one or more PDF files**—depending on a **user’s persona** (job role) and a **specific task**.

The key goal:  
> “Given a persona and task, extract meaningful information from PDFs that helps the user accomplish that task — while working **completely offline**, on **CPU-only**, and with **model + logic size under 1GB**.”

---

## 🎯 Objectives

- ✅ Process multiple PDFs (up to 50 pages each)
- ✅ Use persona + job-to-be-done to rank important sections
- ✅ Output top-ranked sections and their content
- ✅ Work fully offline, CPU-only (no APIs, no GPU)
- ✅ Stay under 1GB total model + code size

---

## 🧠 How Our System Works

Our system is a hybrid of **layout-based extraction** and **semantic understanding**. It:

1. Parses the structure of PDFs using **font styles & sizes**
2. Extracts **headings** using KMeans-based clustering
3. If headings fail, falls back to **paragraph chunking**
4. Embeds all content chunks using a multilingual transformer
5. Embeds the **persona + task** into the same vector space
6. Scores all chunks using **cosine similarity**
7. Returns top N most relevant sections with refin

{
  "persona": { "role": "Data Analyst" },
  "job_to_be_done": { "task": "Summarize key insights from PDF" },
  "documents": [
    { "filename": "yourfile.pdf" }
  ],
  "challenge_info": {
    "challenge_id": "task1b",
    "test_case_name": "sample_case"
  }
}

{
  "metadata": {
    "documents": ["yourfile.pdf"],
    "persona": "Data Analyst",
    "job_to_be_done": "Summarize key insights from PDF",
    "timestamp": "2025-07-28T16:00:00Z"
  },
  "extracted_sections": [
    {
      "document": "yourfile.pdf",
      "page": 3,
      "section_title": "AI Applications in Finance",
      "importance_rank": 1,
      "score": 0.9015
    }
  ],
  "sub_section_analysis": [
    {
      "document": "yourfile.pdf",
      "page": 3,
      "refined_text": "AI helps in fraud detection, predictive analysis..."
    }
  ]
}
