import requests


def find_asset_url(auth: str, bbox: list[float], stac_url: str) -> str:
    response = requests.get(
        f"{stac_url}/search",
        headers={"Authorization": f"Basic {auth}"},
        json={
            "bbox": bbox,
            "limit": 1,
            "sortby": [{"field": "properties.datetime", "direction": "desc"}],
        },
    )
    response.raise_for_status()
    features = response.json().get("features", [])
    if not features:
        raise RuntimeError("No imagery found for bounding box")
    item = features[0]
    print(f"Item: {item['id']}  |  {item['properties'].get('datetime')}")
    assets = item.get("assets", {})
    for key in ("visual", "TCI", "tci"):
        if key in assets:
            return assets[key]["href"]
    return next(iter(assets.values()))["href"]
