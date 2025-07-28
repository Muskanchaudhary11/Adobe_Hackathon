import os
import json
from heading_parser import extract_font_info, determine_heading_levels, extract_outline

INPUT_DIR = "./input"
OUTPUT_DIR = "./output"

for filename in os.listdir(INPUT_DIR):
    if filename.endswith(".pdf"):
        filepath = os.path.join(INPUT_DIR, filename)
        elements = extract_font_info(filepath)
        clustered = determine_heading_levels(elements)
        json_data = extract_outline(clustered)
        out_path = os.path.join(OUTPUT_DIR, filename.replace(".pdf", ".json"))
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2)
