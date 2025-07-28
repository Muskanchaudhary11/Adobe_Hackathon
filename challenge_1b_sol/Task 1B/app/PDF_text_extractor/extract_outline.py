def extract_outline(elements):
    outline = []
    title = ""

    for e in elements:
        if not all(k in e for k in ("text", "level", "page")):
            continue

        text = e["text"].strip()
        level = e["level"]

        if level == "TITLE" and not title:
            title = text
        elif level in {"H1", "H2", "H3"}:
            if len(text) <= 2 and not any(c.isalnum() for c in text):
                continue
            outline.append({
                "level": level,
                "text": text,
                "page": e["page"] - 1
            })

    return {
        "title": title,
        "outline": outline
    }
