from functions import build_query

bounding_box = [5.949912, 52.000471, 5.988407, 52.010748]  # [west, south, east, north] WGS84
STAC_URL = "https://api.satellietdataportaal.nl/v2/stac"


def main():
    url = build_query(bounding_box, STAC_URL)
    print(f"Click to view results:\n{url}")


if __name__ == "__main__":
    main()
