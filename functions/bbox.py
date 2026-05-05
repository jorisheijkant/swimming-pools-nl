from pyproj import Transformer


def bbox_to_rd(bbox: list[float]) -> tuple[float, float, float, float]:
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:28992", always_xy=True)
    w, s = transformer.transform(bbox[0], bbox[1])
    e, n = transformer.transform(bbox[2], bbox[3])
    return w, s, e, n
