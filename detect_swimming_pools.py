import json
from pathlib import Path

import numpy as np
import rasterio
from pyproj import Transformer
from ultralytics import YOLO

TILE_FILE = "data/og_tiles/duiven_26_03.tif"
CONFIDENCE_THRESHOLD = 0.4

source_stem = Path(TILE_FILE).stem
tiff_tiles_dir = Path("data/tiles") / source_stem / "tiff_tiles"
output_geojson_path = Path("data/tiles") / source_stem / "detected_pools.geojson"

tiff_tiles = sorted(tiff_tiles_dir.glob("*.tif"))
if not tiff_tiles:
    raise FileNotFoundError(f"No GeoTIFF tiles found in {tiff_tiles_dir} — run tile_satellite_file.py first")

print("Loading model: data/models/model.pt")
model = YOLO("data/models/model.pt")

print(f"Running detection on {len(tiff_tiles)} tiles…")

geojson_features = []

for tile_path in tiff_tiles:
    with rasterio.open(tile_path) as tile:
        tile_crs = tile.crs
        tile_transform = tile.transform
        pixel_data = tile.read()

    # Convert to uint8 RGB for the model
    rgb_bands = pixel_data[:3] if pixel_data.shape[0] >= 3 else np.repeat(pixel_data[:1], 3, axis=0)
    if rgb_bands.dtype != np.uint8:
        pixel_min, pixel_max = rgb_bands.min(), rgb_bands.max()
        if pixel_max > pixel_min:
            rgb_bands = ((rgb_bands - pixel_min) / (pixel_max - pixel_min) * 255).astype(np.uint8)
        else:
            rgb_bands = np.zeros_like(rgb_bands, dtype=np.uint8)
    rgb_image = np.moveaxis(rgb_bands, 0, -1)  # (H, W, 3)

    results = model.predict(source=rgb_image, conf=CONFIDENCE_THRESHOLD, verbose=False)
    detections = results[0].boxes

    if len(detections) == 0:
        continue

    # Transform pixel bbox coordinates → tile CRS → WGS84
    crs_to_wgs84 = Transformer.from_crs(tile_crs, "EPSG:4326", always_xy=True)

    for box in detections:
        pixel_x_min, pixel_y_min, pixel_x_max, pixel_y_max = box.xyxy[0].tolist()
        confidence = float(box.conf[0])

        # rasterio xy() converts pixel (row, col) to CRS coordinates
        geo_x_min, geo_y_max = rasterio.transform.xy(tile_transform, pixel_y_min, pixel_x_min)
        geo_x_max, geo_y_min = rasterio.transform.xy(tile_transform, pixel_y_max, pixel_x_max)

        # Convert to WGS84 for GeoJSON
        lon_min, lat_min = crs_to_wgs84.transform(geo_x_min, geo_y_min)
        lon_max, lat_max = crs_to_wgs84.transform(geo_x_max, geo_y_max)

        geojson_features.append({
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [lon_min, lat_min],
                    [lon_max, lat_min],
                    [lon_max, lat_max],
                    [lon_min, lat_max],
                    [lon_min, lat_min],
                ]],
            },
            "properties": {
                "confidence": round(confidence, 3),
                "source_tile": tile_path.name,
            },
        })

    print(f"  {tile_path.name}: {len(detections)} pool(s) detected")

geojson = {"type": "FeatureCollection", "features": geojson_features}
output_geojson_path.write_text(json.dumps(geojson, indent=2))
print(f"\nDone — {len(geojson_features)} pool(s) found → {output_geojson_path}")
