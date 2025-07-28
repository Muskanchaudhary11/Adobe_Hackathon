from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar
from sklearn.cluster import KMeans
import numpy as np

def extract_outline(elements):
    outline = []
    title = ""
    for e in elements:
        if e["level"] == "TITLE" and not title:
            title = e["text"]
        elif e["level"] in ["H1", "H2", "H3"]:
            outline.append({
                "level": e["level"],
                "text": e["text"],
                "page": e["page"]-1
            })
    return {
        "title": title,
        "outline": outline
    }

def determine_heading_levels(elements):
    font_sizes = np.array([e["font_size"] for e in elements]).reshape(-1, 1)
    n_clusters = 4 
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    kmeans.fit(font_sizes)

    clusters = sorted([(i, center[0]) for i, center in enumerate(kmeans.cluster_centers_)], key=lambda x: -x[1])
    level_map = {cluster_id: f"H{i}" if i > 0 else "TITLE" for i, (cluster_id, _) in enumerate(clusters)}
    
    for e in elements:
        e["level"] = level_map[kmeans.predict([[e["font_size"]]])[0]]
    
    return elements

def extract_font_info(file_path):
    text_elements = []
    for page_num, page_layout in enumerate(extract_pages(file_path), start=1):
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    font_sizes = []
                    try:
                        for char in text_line:
                            if isinstance(char, LTChar):
                                font_sizes.append(char.size)
                    except TypeError:
                        if isinstance(text_line, LTChar):
                            font_sizes.append(text_line.size)

                    if not font_sizes:
                        continue
                    
                    avg_font_size = sum(font_sizes) / len(font_sizes)
                    text = text_line.get_text().strip()
                    if text:
                        text_elements.append({
                            "text": text,
                            "font_size": avg_font_size,
                            "page": page_num
                        })
    return text_elements