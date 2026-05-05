import json
from pathlib import Path

from pyproj import Transformer


def bbox_to_geojson(
    bbox_wgs84: list[float],
    bbox_rd: tuple[float, float, float, float],
    out_path: Path,
) -> None:
    w84, s84, e84, n84 = bbox_wgs84
    transformer = Transformer.from_crs("EPSG:28992", "EPSG:4326", always_xy=True)
    w_rd, s_rd, e_rd, n_rd = bbox_rd
    w84_rd, s84_rd = transformer.transform(w_rd, s_rd)
    e84_rd, n84_rd = transformer.transform(e_rd, n_rd)

    def rect(w, s, e, n):
        return [[w, s], [e, s], [e, n], [w, n], [w, s]]

    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"label": "input bbox (WGS84)"},
                "geometry": {"type": "Polygon", "coordinates": [rect(w84, s84, e84, n84)]},
            },
            {
                "type": "Feature",
                "properties": {"label": "RD bounds (reprojected to WGS84)"},
                "geometry": {"type": "Polygon", "coordinates": [rect(w84_rd, s84_rd, e84_rd, n84_rd)]},
            },
        ],
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(geojson, indent=2))
    print(f"GeoJSON written → {out_path}")
