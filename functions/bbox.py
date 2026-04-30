import math

from pyproj import Transformer


def bbox_to_rd(
    bbox: list[float], tile_size_m: int
) -> tuple[float, float, float, float]:
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:28992", always_xy=True)
    w, s = transformer.transform(bbox[0], bbox[1])
    e, n = transformer.transform(bbox[2], bbox[3])
    # snap outward to tile-grid boundary so tiles align perfectly
    w = math.floor(w / tile_size_m) * tile_size_m
    s = math.floor(s / tile_size_m) * tile_size_m
    e = math.ceil(e / tile_size_m) * tile_size_m
    n = math.ceil(n / tile_size_m) * tile_size_m
    return w, s, e, n
