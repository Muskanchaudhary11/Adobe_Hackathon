# 📄 Adobe Hackathon Challenge 1A – PDF to JSON Structured Outline Extractor

## 🧩 Challenge Overview

As part of **Adobe Hackathon 2025 – Round 1**, this project solves **Challenge 1A** under the theme "Connecting the Dots".  
The challenge was to develop a tool that takes in any **PDF document (up to 50 pages)** and outputs a **clean JSON structure** that represents the **title**, **headings (H1, H2, H3)**, and the **page numbers** they appear on.

📌 Core Objectives:
- Work **offline** and on **CPU-only** environments
- Stay **under 1 GB** in model size
- Output structured **hierarchical JSON**
- Handle **real-world PDFs** with variable layouts

---

## 💡 Problem Motivation

We often consume long, text-heavy PDFs — from research papers to policy documents — but they're difficult to navigate without a clear outline.  
What if we could automate the extraction of this outline — title, section headings, and subsections — and turn it into a structured, machine-readable format?

This project addresses exactly that: **turning messy PDF formatting into clean JSON structures**, which can later be indexed, searched, or filtered (e.g., in Challenge 1B).

---

## ⚙️ Solution Summary

This is a **lightweight, layout-based PDF outline extractor** that:
- Reads PDFs using font metadata (size, weight, position)
- Automatically detects and classifies headings into **H1**, **H2**, and **H3**
- Outputs a structured, hierarchical JSON
- Works fully offline and **requires no ML model**

Unlike NLP-based solutions that rely on pretrained models or fine-tuned transformers, this project purely leverages **layout patterns**, which makes it:
- Much faster (sub-5 seconds)
- More memory-efficient (<100 MB RAM)
- Portable across any machine

---

## 🔍 How It Works (Internals)

### 📁 Input:
- A multi-page PDF document (digital, non-scanned)
  
### 🧠 Core Logic:
1. **Text Block Extraction**:
   - Uses `PyMuPDF` (`fitz`) to extract all text spans and their metadata:
     - Text content
     - Font size
     - Bold/italic flags
     - Bounding box position
     - Page number

2. **Font Size Analysis**:
   - Collects all font sizes across the document
   - Identifies the most frequent sizes and ranks them
     - Largest font = likely `Title` or `H1`
     - Medium = `H2`
     - Smaller = `H3` or body text

3. **Heading Classification**:
   - Uses size thresholds, boldness, and positioning to classify headings
   - Ignores lines with too many words (likely paragraphs)
   - Filters out headers/footers and non-content elements

4. **Section Ordering**:
   - Ensures that headings are listed in visual reading order (top to bottom, left to right)
   - Associates each heading with its page number

5. **Structured JSON Output**:
   - Stores the document’s outline with:
     - Heading Level (`H1`, `H2`, `H3`)
     - Text
     - Page Number
   - Also includes filename and detected title

---

## 🧪 Output Format

```json
{
  "file_name": "sample.pdf",
  "title": "Your Document Title",
  "headings": [
    {
      "heading_level": "H1",
      "text": "1. Introduction",
      "page_number": 1
    },
    {
      "heading_level": "H2",
      "text": "1.1 Background",
      "page_number": 2
    },
    {
      "heading_level": "H3",
      "text": "1.1.1 Problem Statement",
      "page_number": 3
    }
  ]
}
```

Machine Learning and Society

1. Introduction
1.1 Scope
1.2 Importance
2. Applications
2.1 Healthcare
2.2 Finance
```
{
  "file_name": "sample.pdf",
  "title": "Machine Learning and Society",
  "headings": [
    {"heading_level": "H1", "text": "1. Introduction", "page_number": 1},
    {"heading_level": "H2", "text": "1.1 Scope", "page_number": 1},
    {"heading_level": "H2", "text": "1.2 Importance", "page_number": 1},
    {"heading_level": "H1", "text": "2. Applications", "page_number": 2},
    {"heading_level": "H2", "text": "2.1 Healthcare", "page_number": 2},
    {"heading_level": "H2", "text": "2.2 Finance", "page_number": 2}
  ]
}
```





## 📈 Performance

- ✅ Runs completely offline  
- ✅ Processes ~50-page PDF in under 10 seconds  
- ✅ Lightweight — no large ML models or extra memory required  
- ✅ Output follows the required Adobe JSON schema

---

## ❗ Limitations

- Does not support scanned image PDFs (no OCR yet)
- Highly decorative or inconsistent formatting may reduce accuracy
- Roman numerals or unconventional heading styles may require extra rules

---

## 🚀 Future Improvements

- 🧠 Add OCR support (e.g., Tesseract) for scanned PDFs  
- 🎯 Improve heading detection using heuristic patterns + regex  
- 📦 Add command-line (CLI) support for batch processing multiple PDFs  
- 🌳 Visualize heading hierarchy using a collapsible tree structure  
- 🤖 Extend with persona-awareness for Challenge 1B (e.g., task-based filtering)

---

## 🤝 Team Contribution

This project was collaboratively developed by:

1. 👩‍💻 **Muskan Chaudhary** 
2. 👩‍💻 **Vaishnavi Rai** 

Together, we built this solution as a team for **Adobe Hackathon 2025 – Challenge 1A**, focusing on accuracy, simplicity, and offline performance.





