import math
from pathlib import Path

import numpy as np
import rasterio
from pyproj import Transformer
from rasterio.transform import from_bounds as transform_from_bounds
from rasterio.windows import from_bounds as window_from_bounds
from PIL import Image


def create_tiles(tile_file: str, bounding_box: list[float] | None = None, tile_size_in_meters: int = 100, tile_overlap: int = 20) -> None:
    source_stem = Path(tile_file).stem
    output_tiff_dir = Path("data/tiles") / source_stem / "tiff_tiles"
    output_jpg_dir = Path("data/tiles") / source_stem / "jpg_files"
    output_tiff_dir.mkdir(parents=True, exist_ok=True)
    output_jpg_dir.mkdir(parents=True, exist_ok=True)

    with rasterio.open(tile_file) as source_file:
        if bounding_box is not None:
            # Reproject the WGS84 bounding box into the file's native CRS
            wgs84_to_file_crs = Transformer.from_crs("EPSG:4326", source_file.crs, always_xy=True)
            bbox_west, bbox_south = wgs84_to_file_crs.transform(bounding_box[0], bounding_box[1])
            bbox_east, bbox_north = wgs84_to_file_crs.transform(bounding_box[2], bounding_box[3])
            # Clip to the actual file extent so we don't request data outside the file
            file_bounds = source_file.bounds
            area_west  = max(bbox_west,  file_bounds.left)
            area_south = max(bbox_south, file_bounds.bottom)
            area_east  = min(bbox_east,  file_bounds.right)
            area_north = min(bbox_north, file_bounds.top)
        else:
            file_bounds = source_file.bounds
            area_west, area_south, area_east, area_north = (
                file_bounds.left, file_bounds.bottom, file_bounds.right, file_bounds.top
            )

        # Snap the area outward to the nearest tile boundary
        grid_west  = math.floor(area_west  / tile_size_in_meters) * tile_size_in_meters
        grid_south = math.floor(area_south / tile_size_in_meters) * tile_size_in_meters
        grid_east  = math.ceil(area_east   / tile_size_in_meters) * tile_size_in_meters
        grid_north = math.ceil(area_north  / tile_size_in_meters) * tile_size_in_meters

        tile_step = tile_size_in_meters - tile_overlap
        tile_origins_x = range(int(grid_west),  int(grid_east),  tile_step)
        tile_origins_y = range(int(grid_south), int(grid_north), tile_step)
        total_tiles = len(tile_origins_x) * len(tile_origins_y)
        print(f"Writing up to {total_tiles} tiles ({len(tile_origins_x)}×{len(tile_origins_y)}) → {output_tiff_dir.parent}/")

        tiles_written = 0
        for tile_origin_x in tile_origins_x:
            for tile_origin_y in tile_origins_y:
                tile_left   = tile_origin_x
                tile_bottom = tile_origin_y
                tile_right  = tile_origin_x + tile_size_in_meters
                tile_top    = tile_origin_y + tile_size_in_meters

                read_window = window_from_bounds(tile_left, tile_bottom, tile_right, tile_top, source_file.transform)
                pixel_data = source_file.read(window=read_window)

                if not pixel_data.any():
                    continue

                tile_geo_transform = transform_from_bounds(
                    tile_left, tile_bottom, tile_right, tile_top,
                    pixel_data.shape[2], pixel_data.shape[1],
                )
                tile_filename = f"tile_{tile_origin_x}_{tile_origin_y}"

                # Write GeoTIFF with full geodata intact
                with rasterio.open(
                    output_tiff_dir / f"{tile_filename}.tif", "w",
                    driver="GTiff",
                    height=pixel_data.shape[1],
                    width=pixel_data.shape[2],
                    count=source_file.count,
                    dtype=pixel_data.dtype,
                    crs=source_file.crs,
                    transform=tile_geo_transform,
                ) as output_tiff:
                    output_tiff.write(pixel_data)

                # Write JPEG: use first 3 bands as RGB, scale to uint8
                rgb_bands = pixel_data[:3] if pixel_data.shape[0] >= 3 else np.repeat(pixel_data[:1], 3, axis=0)
                if rgb_bands.dtype != np.uint8:
                    pixel_min, pixel_max = rgb_bands.min(), rgb_bands.max()
                    if pixel_max > pixel_min:
                        rgb_bands = ((rgb_bands - pixel_min) / (pixel_max - pixel_min) * 255).astype(np.uint8)
                    else:
                        rgb_bands = np.zeros_like(rgb_bands, dtype=np.uint8)
                rgb_image = Image.fromarray(np.moveaxis(rgb_bands, 0, -1)).resize((500, 500), Image.NEAREST)
                rgb_image.save(output_jpg_dir / f"{tile_filename}.jpg")

                tiles_written += 1

        print(f"Done — {tiles_written} tiles written to {output_tiff_dir.parent}/")
