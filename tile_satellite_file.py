from functions import create_tiles

tile_file = "data/og_tiles/duiven_26_03.tif"
tile_size_in_meters = 30 
bounding_box = [5.949912, 52.000471, 5.988407, 52.010748]  # [west, south, east, north] WGS84

create_tiles(tile_file, bounding_box=bounding_box, tile_size_in_meters=tile_size_in_meters)
