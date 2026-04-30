import math
import os

import rasterio
from rasterio.crs import CRS
from rasterio.enums import Resampling
from rasterio.transform import from_origin
from rasterio.warp import reproject


def reproject_to_rd(
    src_url: str,
    dst_path: str,
    auth: str,
    bbox: list[float],
    bbox_rd: tuple[float, float, float, float],
    crs_rd: CRS,
) -> None:
    # GDAL uses this env var for HTTP auth on /vsicurl/ reads
    os.environ["GDAL_HTTP_HEADERS"] = f"Authorization: Basic {auth}"
    w, s, e, n = bbox_rd

    with rasterio.open(src_url) as src:
        if src.crs.is_geographic:
            lat_centre = (bbox[1] + bbox[3]) / 2
            res_m = abs(src.transform.a) * 111_320 * math.cos(math.radians(lat_centre))
        else:
            res_m = abs(src.transform.a)
        res_m = max(res_m, 0.1)

        width = round((e - w) / res_m)
        height = round((n - s) / res_m)
        dst_transform = from_origin(w, n, res_m, res_m)

        meta = {
            "driver": "GTiff",
            "crs": crs_rd,
            "transform": dst_transform,
            "width": width,
            "height": height,
            "count": src.count,
            "dtype": src.dtypes[0],
        }

        print(f"Reprojecting to RD New at {res_m:.2f}m resolution ({width}×{height}px)…")
        with rasterio.open(dst_path, "w", **meta) as dst:
            for band_idx in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, band_idx),
                    destination=rasterio.band(dst, band_idx),
                    src_crs=src.crs,
                    src_transform=src.transform,
                    dst_crs=crs_rd,
                    dst_transform=dst_transform,
                    resampling=Resampling.bilinear,
                )
