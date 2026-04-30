import os
import tempfile
from pathlib import Path

from rasterio.crs import CRS

from functions import bbox_to_rd, find_asset_url, generate_tiles, get_basic_auth, reproject_to_rd

PLACE_NAME = "Rozendaal"
BBOX = [5.949912, 52.000471, 5.988407, 52.010748]  # [west, south, east, north] WGS84

TILE_SIZE_M = 100
OUTPUT_DIR = Path("data/tiles")
STAC_URL = "https://api.satellietdataportaal.nl/v2/stac"
CRS_RD = CRS.from_epsg(28992)


def main():
    auth = get_basic_auth()
    asset_url = find_asset_url(auth, BBOX, STAC_URL)
    print(f"Asset URL: {asset_url}")

    bounds_rd = bbox_to_rd(BBOX, TILE_SIZE_M)

    with tempfile.NamedTemporaryFile(suffix=".tif", delete=False) as tmp:
        rd_path = tmp.name

    try:
        reproject_to_rd(asset_url, rd_path, auth, BBOX, bounds_rd, CRS_RD)
        generate_tiles(rd_path, bounds_rd, TILE_SIZE_M, OUTPUT_DIR, CRS_RD)
    finally:
        os.unlink(rd_path)


if __name__ == "__main__":
    main()
