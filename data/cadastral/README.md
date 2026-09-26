# Cadastral layer data contract

Create the authority-derived file at `data/cadastral/mathura_zoning.geojson`.

Example:
{
  "type": "FeatureCollection",
  "metadata": {
    "authoritative": true,
    "authority": "Issuing authority",
    "source": "Official dataset identifier/revision",
    "effective_date": "YYYY-MM-DD",
    "crs_epsg": 4326
  },
  "features": [
    {
      "type": "Feature",
      "properties": {
        "parcel_id": "…", "village": "…", "khasra": "…",
        "zoning_code": "…", "zoning_name": "…",
        "land_use": "…", "area_sqm": 0
      },
      "geometry": { "type": "Polygon", "coordinates": [[[77.0,27.0],[77.0,27.1],[77.1,27.1],[77.0,27.0]]] }
    }
  ]
}

Do not generate this dataset from a screenshot or raster map. Obtain the parcel polygons from the competent cadastral/GIS authority and record the exact source and effective date.
