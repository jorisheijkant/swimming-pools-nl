from pathlib import Path

import rasterio
from rasterio.crs import CRS
from rasterio.transform import from_bounds as transform_from_bounds
from rasterio.windows import from_bounds as window_from_bounds


def generate_tiles(
    src_path: str,
    bbox_rd: tuple[float, float, float, float],
    tile_size_m: int,
    output_dir: Path,
    crs_rd: CRS,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    w, s, e, n = bbox_rd

    with rasterio.open(src_path) as src:
        xs = range(int(w), int(e), tile_size_m)
        ys = range(int(s), int(n), tile_size_m)
        total = len(xs) * len(ys)
        print(f"Writing up to {total} tiles ({len(xs)}×{len(ys)}) → {output_dir}/")

        written = 0
        for tx in xs:
            for ty in ys:
                window = window_from_bounds(
                    tx, ty, tx + tile_size_m, ty + tile_size_m, src.transform
                )
                data = src.read(window=window)

                if not data.any():
                    continue

                tile_transform = transform_from_bounds(
                    tx, ty, tx + tile_size_m, ty + tile_size_m,
                    data.shape[2], data.shape[1],
                )
                out_path = output_dir / f"tile_{tx}_{ty}.tif"
                with rasterio.open(
                    out_path, "w",
                    driver="GTiff",
                    height=data.shape[1],
                    width=data.shape[2],
                    count=src.count,
                    dtype=data.dtype,
                    crs=crs_rd,
                    transform=tile_transform,
                ) as dst:
                    dst.write(data)
                written += 1

        print(f"Done — {written} non-empty tiles written to {output_dir}/")
