"""Authoritative-vector cadastral zoning engine.

Fail-closed: it never converts a raster master-plan image into a parcel/legal
zoning decision. A result is cadastral-grade only when an authoritative parcel/
zoning GeoJSON layer is supplied with explicit CRS and provenance metadata.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Any

DEFAULT_PATH = os.environ.get("CADASTRAL_GEOJSON_PATH", str(Path(__file__).resolve().parent / "data" / "cadastral" / "mathura_zoning.geojson"))

class CadastralLayerError(RuntimeError):
    pass

def _point_on_segment(px, py, ax, ay, bx, by, eps=1e-12):
    cross = (px-ax)*(by-ay) - (py-ay)*(bx-ax)
    if abs(cross) > eps: return False
    return min(ax,bx)-eps <= px <= max(ax,bx)+eps and min(ay,by)-eps <= py <= max(ay,by)+eps

def _ring_contains(x, y, ring):
    inside = False
    if not ring: return False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        if _point_on_segment(x, y, xi, yi, xj, yj): return True
        if ((yi > y) != (yj > y)):
            xin = (xj-xi)*(y-yi)/(yj-yi) + xi
            if x < xin: inside = not inside
        j = i
    return inside

def _polygon_contains(x, y, coordinates):
    return bool(coordinates) and _ring_contains(x, y, coordinates[0]) and not any(_ring_contains(x, y, h) for h in coordinates[1:])

def _geometry_contains(lon, lat, geometry):
    if not geometry: return False
    kind, coords = geometry.get("type"), geometry.get("coordinates")
    if kind == "Polygon": return _polygon_contains(lon, lat, coords)
    if kind == "MultiPolygon": return any(_polygon_contains(lon, lat, p) for p in coords)
    return False

def _bbox_contains(lon, lat, bbox):
    return not bbox or (bbox[0] <= lon <= bbox[2] and bbox[1] <= lat <= bbox[3])

def load_layer(path: str = DEFAULT_PATH) -> dict[str, Any]:
    p = Path(path)
    if not p.exists(): raise CadastralLayerError("Authoritative cadastral zoning layer is not installed. Provide a GeoJSON FeatureCollection via CADASTRAL_GEOJSON_PATH.")
    try: data = json.loads(p.read_text(encoding="utf-8"))
    except Exception as exc: raise CadastralLayerError(f"Cannot read cadastral layer: {exc}") from exc
    if data.get("type") != "FeatureCollection": raise CadastralLayerError("Cadastral layer must be a GeoJSON FeatureCollection.")
    meta = data.get("metadata") or {}
    if meta.get("crs_epsg") != 4326: raise CadastralLayerError("Cadastral layer must declare metadata.crs_epsg=4326.")
    if meta.get("authoritative") is not True: raise CadastralLayerError("Layer must explicitly declare metadata.authoritative=true.")
    if not meta.get("source"): raise CadastralLayerError("Layer metadata.source is required.")
    if not meta.get("effective_date"): raise CadastralLayerError("Layer metadata.effective_date is required.")
    return data

def layer_status(path: str = DEFAULT_PATH):
    try:
        data = load_layer(path); meta = data["metadata"]
        return {"ready": True, "authoritative": True, "source": meta["source"], "effective_date": meta["effective_date"], "crs_epsg": meta["crs_epsg"], "feature_count": len(data.get("features", [])), "path": str(Path(path))}
    except CadastralLayerError as exc:
        return {"ready": False, "authoritative": False, "error": str(exc), "path": str(Path(path))}

def parcel_at(lon: float, lat: float, path: str = DEFAULT_PATH):
    if not (-180 <= lon <= 180 and -90 <= lat <= 90): raise CadastralLayerError("Invalid longitude/latitude.")
    data = load_layer(path); matches = []
    for feature in data.get("features", []):
        if feature.get("type") != "Feature": continue
        if not _bbox_contains(lon, lat, feature.get("bbox")): continue
        if _geometry_contains(lon, lat, feature.get("geometry")):
            props = feature.get("properties") or {}
            matches.append({"parcel_id": props.get("parcel_id") or props.get("khasra") or props.get("plot_no"), "village": props.get("village"), "khasra": props.get("khasra"), "zoning_code": props.get("zoning_code"), "zoning_name": props.get("zoning_name"), "land_use": props.get("land_use"), "area_sqm": props.get("area_sqm"), "properties": props})
    meta = data["metadata"]
    if len(matches) == 0: return {"status":"NO_MATCH","message":"Point is outside the supplied authoritative cadastral layer.","lon":lon,"lat":lat,"source":meta["source"],"effective_date":meta["effective_date"]}
    if len(matches) > 1: return {"status":"AMBIGUOUS","message":"More than one authoritative polygon contains the point; survey/topology review required.","lon":lon,"lat":lat,"matches":matches,"source":meta["source"],"effective_date":meta["effective_date"]}
    return {"status":"MATCH","lon":lon,"lat":lat,"parcel":matches[0],"source":meta["source"],"effective_date":meta["effective_date"],"crs_epsg":meta["crs_epsg"],"authority":meta.get("authority"),"basis":"authoritative vector parcel/zoning layer; point-in-polygon"}
