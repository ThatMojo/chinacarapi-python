# CHINACARAPI_KEY=your_key python examples/quickstart.py
from chinacarapi import ChinaCarAPI

client = ChinaCarAPI()  # reads CHINACARAPI_KEY; get a key at https://chinacarapi.com
page = client.catalog(make="BYD", export_ready=True, sort="price_asc", limit=5)
print(f"{page['total']} export-ready BYD cars, cheapest:")
for car in page["results"]:
    print(f"{car['title']} | {car['mileageKm']} km | {car['price']['eur']} EUR | {car['source']}")
