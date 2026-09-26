from flask import Blueprint,request,jsonify,Response
from architecture_engine import residential_rules,parking_for_dwelling_units,make_dxf_rectangles
from gis_masterplan import point_info
from cadastral_zoning import parcel_at, layer_status, CadastralLayerError
architecture_bp=Blueprint("architecture",__name__,url_prefix="/api/architecture")
@architecture_bp.post("/residential/check")
def residential_check():
 x=request.get_json(silent=True) or {}; r=residential_rules(float(x.get("plot_area_sqm",0)),x.get("use_type","single"),bool(x.get("built_up_area",True)),float(x["road_width_m"]) if x.get("road_width_m") not in (None,"") else None,float(x["frontage_m"]) if x.get("frontage_m") not in (None,"") else None,float(x["depth_m"]) if x.get("depth_m") not in (None,"") else None)
 return jsonify(ok=r.ok,messages=r.messages,values=r.values,source=r.source)
@architecture_bp.post("/residential/parking")
def residential_parking():
 x=request.get_json(silent=True) or {}; return jsonify(parking_for_dwelling_units([float(v) for v in x.get("unit_areas_sqm",[])]))
@architecture_bp.post("/dxf")
def dxf():
 x=request.get_json(silent=True) or {}; t=make_dxf_rectangles(float(x["frontage_m"]),float(x["depth_m"]),x["setbacks_m"],x.get("building_width_m"),x.get("building_depth_m"))
 return Response(t,mimetype="application/dxf",headers={"Content-Disposition":"attachment; filename=preliminary_plan.dxf"})
@architecture_bp.get("/masterplan/location")
def masterplan_location():
 try: lon=float(request.args["lon"]); lat=float(request.args["lat"])
 except: return jsonify(error="lon and lat are required"),400
 return jsonify(point_info(lon,lat))

@app.get("/cadastral/status")
def cadastral_status():
    return jsonify(layer_status())

@app.get("/cadastral/point")
def cadastral_point():
    try:
        lon=float(request.args["lon"]); lat=float(request.args["lat"])
        return jsonify(parcel_at(lon, lat))
    except KeyError:
        return jsonify(error="lon and lat are required"), 400
    except CadastralLayerError as exc:
        return jsonify(status="NOT_READY", authoritative=False, error=str(exc)), 503
    except ValueError:
        return jsonify(error="lon and lat must be numeric"), 400
