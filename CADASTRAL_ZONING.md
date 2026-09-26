# Cadastral-grade zoning

The app now has a fail-closed vector cadastral zoning path. It does not treat the supplied Master Plan 2031 raster as parcel geometry.

## Required authority dataset
Install the official parcel/zoning GeoJSON as `data/cadastral/mathura_zoning.geojson`, or set `CADASTRAL_GEOJSON_PATH` to a mounted file.

The GeoJSON must be a FeatureCollection with top-level metadata:
- `authoritative: true`
- `authority`
- `source`
- `effective_date`
- `crs_epsg: 4326`

Each parcel should carry fields such as `parcel_id`, `village`, `khasra`, `zoning_code`, `zoning_name`, `land_use`, and `area_sqm`.

## API
- `GET /api/architecture/cadastral/status`
- `GET /api/architecture/cadastral/point?lon=77.6736&lat=27.4925`

`MATCH` means exactly one authoritative polygon contains the point. `NO_MATCH` means the point is outside the loaded layer. `AMBIGUOUS` means overlapping authoritative polygons require topology/survey review.

## Why the supplied PDF is not enough
The supplied MVDA Master Plan 2031 PDF is a cartographic raster map. It can be used as a reference overlay, but it cannot establish cadastral parcel boundaries. The cadastral engine therefore refuses to infer parcel zoning from it.

UP Bhulekh currently reports verified and Bhunaksha-linked cadastral data for Mathura district, while also reporting some mapsheets that are not yet georeferenced. The official authority dataset/revision still has to be supplied to this application before a parcel can be returned as authoritative.

This is a technical GIS decision layer, not a substitute for title/lease records, survey demarcation, sanctioned plans, or the competent authority decision.
