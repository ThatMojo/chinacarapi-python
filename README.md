# ChinaCarAPI: Python client for Chinese car data (Dongchedi API, Che168 API)

Official **Python client** for [ChinaCarAPI](https://chinacarapi.com/?utm_source=readme&utm_medium=chinacarapi-python), a REST
**China car API** for the Chinese used-car market. One API for **Dongchedi (懂车帝)** and
**Che168 (车168, Autohome)**: 400,000+ listings with price, mileage, first registration, seller,
photos, inspection reports (accident, flood, fire, EV battery), price history and export status.
Delivered in English, with the original Chinese kept alongside.

Built for car exporters, importers, dealers and marketplaces that need reliable **Chinese car data**
without scrapers, captchas, proxies or Chinese-language parsing.

> **A ChinaCarAPI key is required.** The API and its data are a paid service. This client only
> works with a key from [chinacarapi.com](https://chinacarapi.com/?utm_source=readme&utm_medium=chinacarapi-python) (5-day trial available).
> EnCarAPI keys with the China add-on work as well.

## Install

```bash
pip install chinacarapi
```

Requires Python 3.8+.

This package is the China entry point of [`encarapi`](https://pypi.org/project/encarapi/),
the official client for Korean **and** Chinese used car data. Need both markets? Use
`EnCarAPI(key)` with `client.korea` and `client.china` (exported here as well).

## Quick start

```python
from chinacarapi import ChinaCarAPI

# Get your key at https://chinacarapi.com
client = ChinaCarAPI("YOUR_API_KEY")  # or set CHINACARAPI_KEY

# Export-ready BYDs, cheapest first, from both marketplaces (duplicates merged)
page = client.catalog(make="BYD", export_ready=True, sort="price_asc", limit=25)

# Full record: price history, photos, seller, alsoListedOn (same car on the other marketplace)
car = client.vehicle(page["results"][0]["id"])

# Inspection report: accident, flood and fire checklist, battery data for EVs
report = client.inspection(page["results"][0]["id"])
```

Without a valid key every call raises a `ChinaCarAPIError` pointing to
[chinacarapi.com](https://chinacarapi.com/?utm_source=readme&utm_medium=chinacarapi-python). There is no free data in this package, only a clean
client for the paid API.

## API

| Method | Endpoint | Description |
|---|---|---|
| `client.catalog(**filters)` | `GET /api/catalog` | Search and filter listings (Dongchedi + Che168) |
| `client.vehicle(id)` | `GET /api/vehicle/:id` | Full record of one car |
| `client.vehicle_by_url(url)` | `GET /api/vehicle/by-url` | Same record by Che168/Dongchedi listing link (desktop, mobile or app) |
| `client.inspection(id)` | `GET /api/inspection/:id` | Inspection report |
| `client.specs(trim_id, **params)` | `GET /api/specs/:trimId` | Autohome trim sheet of a Che168 car (cc, kW, hp, torque, emission standard, weights, EV battery) |
| `client.spec_fields(**params)` | `GET /api/specs/fields` | Label, unit and group for every key of a record's `specs` object; `lang="ru"` or `"zh"` for Russian or Chinese |
| `client.bulk(ids)` | `POST /api/vehicle/bulk` | Up to 500 records per call |
| `client.changes(since=... \| cursor=...)` | `GET /api/catalog/changes` | Change feed: new cars, price changes, removals |
| `client.export_csv(**params)` | `GET /api/catalog/export` | Full catalog as CSV text |
| `client.export_to_file(path, **params)` | `GET /api/catalog/export` | Full catalog streamed to a file (not held in memory): `{"path", "bytes", "generated_at"}` |
| `client.enums(**params)` | `GET /api/enums` | Makes, fuels, cities, sources with counts |
| `client.models(make)` | `GET /api/models` | Models of one make |

**Catalog filters:** `source` (`dongchedi`, `che168`), `duplicates=include`, `make`, `model`,
`year_min`/`year_max`, `reg_year_min`/`reg_year_max`, `price_min`/`price_max` (CNY),
`mileage_max`, `power_min`/`power_max` (hp), `city`, `fuel`, `has_report`, `export_ready` (China's 180-day rule for used-car
exports), `updated_since`, `sort`, `page`, `limit`, `lang`.

**Languages:** `lang="zh"` returns the original Chinese values, `lang="ru"` Russian values for the fixed
fields (fuel, transmission, drivetrain, colours, seller type, condition, vehicle class), city names and
equipment names; make, model and trim names stay Latin. Works on `catalog`, `vehicle`, `vehicle_by_url`,
`bulk` and `specs`. `enums(lang="ru")` adds `nameRu` to fuels and cities, `export_csv(lang="ru")` and
`export_to_file(path, lang="ru")` return the label columns in Russian. With `lang="ru"` the text values of `specs` are Russian as well (energy type, transmission, drive, aspiration,
body type, emission standard, warranties, motor and battery type); a value without a Russian term stays English.
`spec_fields(lang=...)` returns the label, unit and group of every `specs` key in English, Russian or Chinese.

Full reference (OpenAPI 3.1, 13 languages): [chinacarapi.com/documentation](https://chinacarapi.com/documentation?utm_source=readme&utm_medium=chinacarapi-python)

## Keeping a local copy

Export to a file, start the change feed at the export's timestamp, then keep the cursor (Business/Scale):

```python
# 1) Baseline, streamed to disk; generated_at = the export's x-generated-at header
export = client.export_to_file("china-catalog.csv")   # {"path", "bytes", "generated_at"}
import_csv(export["path"])                             # your import: upsert by source + id

# 2) First sync from the export's timestamp (not the time of your download)
for change in client.iterate_changes(since=export["generated_at"]):
    # change["type"]: "new" | "price" | "removed" | "relisted"; apply idempotently
    ...
save_cursor(client.last_cursor)

# 3) Then every few minutes from the saved cursor
for change in client.iterate_changes(cursor=load_cursor()):
    ...
save_cursor(client.last_cursor)
```

`generated_at` lies a few minutes before the file's data snapshot, so the first feed page can repeat a few
events that are already in the file: apply them as upserts.

## Why ChinaCarAPI?

- **Dongchedi API and Che168 API in one**: the same car listed on both is merged and linked.
- **English output**: official English make and model names, translated trims and inspection findings.
- **Export status**: ready-made filter for China's 180-day rule on used-car exports.
- **Plans from €99/month**, 5-day trial for €9.99. EnCarAPI (Korea) customers add China from €39/month.

Korean car data: see [EnCarAPI](https://encarapi.com/?utm_source=readme&utm_medium=chinacarapi-python) and its [Python client](https://github.com/ThatMojo/encarapi-python).

## License

MIT for this client. The data is only available through a ChinaCarAPI subscription.
