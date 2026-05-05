def build_query(bbox: list[float], stac_url: str) -> str:
    bbox_str = ",".join(str(v) for v in bbox)
    return f"{stac_url}/search?bbox={bbox_str}&limit=10&sortby=-properties.created"
