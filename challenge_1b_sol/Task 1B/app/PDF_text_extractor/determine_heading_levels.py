from sklearn.cluster import KMeans
import numpy as np

def determine_heading_levels(elements, n_clusters=4):
    font_sizes = np.array([e["font_size"] for e in elements]).reshape(-1, 1)
    kmeans = KMeans(n_clusters=min(n_clusters, len(set(font_sizes.flatten()))), random_state=42)
    kmeans.fit(font_sizes)

    clusters = sorted(
        [(i, center[0]) for i, center in enumerate(kmeans.cluster_centers_)],
        key=lambda x: -x[1]
    )
    level_map = {cluster_id: f"H{i}" if i > 0 else "TITLE" for i, (cluster_id, _) in enumerate(clusters)}

    for e in elements:
        cluster_id = kmeans.predict([[e["font_size"]]])[0]
        e["level"] = level_map[cluster_id]

    for e in elements:
        text = e["text"]
        is_heading_like = text.isupper() and len(text.split()) <= 10
        if is_heading_like:
            if e["level"] == "H2":
                e["level"] = "H1"
            elif e["level"] == "H3":
                e["level"] = "H2"
            elif e["level"] is None:
                e["level"] = "H3"
    return elements
