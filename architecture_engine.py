from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class RuleResult:
    ok: bool
    messages: List[str]
    values: Dict
    source: str = "UP Model Building Construction and Development Byelaws 2025"

def _far_band(area):
    if area < 35: return None
    if area < 150: return 2.00,2.25
    if area < 300: return 1.80,2.50
    if area < 500: return 1.75,2.50
    if area < 1200: return 1.50,2.50
    return 1.25,2.50

def residential_rules(plot_area_sqm,use_type="single",built_up_area=True,road_width_m=None,frontage_m=None,depth_m=None):
    msgs=[]
    if plot_area_sqm<=0:return RuleResult(False,["Plot area must be greater than zero."],{})
    u=use_type.lower().replace("-","_").replace(" ","_")
    single=u in {"single","single_unit","singleunit"}; multi=u in {"multi","multi_unit","multiunit"}
    if not(single or multi):return RuleResult(False,["Only single-unit and multi-unit plotted residential rules are implemented."],{})
    band=_far_band(plot_area_sqm)
    if band is None:
        if built_up_area and plot_area_sqm<35: band=(2.0,2.25); msgs.append("Built-up-area plot below 35 sqm: base FAR 2.0 is permitted; coverage remains subject to setbacks.")
        else:return RuleResult(False,["Minimum single-unit plot size is 35 sqm in non-built-up area; multi-unit minimum is 150 sqm."],{})
    if multi and plot_area_sqm<150:return RuleResult(False,["Multi-unit residential development requires a minimum 150 sqm plot."],{})
    if single:max_height,max_floors,min_road,stilt=15.0,3,(4.0 if built_up_area else 9.0),"optional"
    else:max_height,max_floors,min_road,stilt=17.5,4,9.0,"mandatory"
    road_ok=road_width_m is None or road_width_m>=min_road
    if not road_ok:msgs.append(f"Road width {road_width_m:g} m is below the {min_road:g} m minimum.")
    if plot_area_sqm<150: sb={"front_m":1.0,"rear_m":0.0,"side1_m":0.0,"side2_m":0.0,"class":"row-housing"}
    elif plot_area_sqm<300: sb={"front_m":3.0,"rear_m":1.5,"side1_m":0.0,"side2_m":0.0,"class":"row-housing"}
    elif plot_area_sqm<500: sb={"front_m":3.0,"rear_m":3.0,"side1_m":0.0,"side2_m":0.0,"class":"row-housing"}
    elif plot_area_sqm<1200: sb={"front_m":4.5,"rear_m":4.5,"side1_m":1.5,"side2_m":0.0,"class":"semi-detached"}
    else: sb={"front_m":6.0,"rear_m":6.0,"side1_m":1.5,"side2_m":1.5,"class":"detached"}
    env=None
    if frontage_m and depth_m:
        if frontage_m*depth_m+1e-6<plot_area_sqm:msgs.append("Frontage × depth is smaller than stated plot area.")
        env={"width_m":round(max(0,frontage_m-sb["side1_m"]-sb["side2_m"]),3),"depth_m":round(max(0,depth_m-sb["front_m"]-sb["rear_m"]),3)}
        env["area_sqm"]=round(env["width_m"]*env["depth_m"],3)
        env["coverage_pct"]=round(100*env["area_sqm"]/plot_area_sqm,3)
    base_far,max_far=band
    return RuleResult(road_ok,msgs,{"plot_area_sqm":plot_area_sqm,"use_type":"single_unit" if single else "multi_unit","built_up_area":built_up_area,"road_width_m":road_width_m,"minimum_road_width_m":min_road,"road_width_ok":road_ok,"max_height_m":max_height,"max_storeys":max_floors,"stilt":stilt,"base_far":base_far,"max_permissible_far":max_far,"base_floor_area_sqm":round(plot_area_sqm*base_far,3),"max_floor_area_sqm":round(plot_area_sqm*max_far,3),"setbacks_m":sb,"envelope":env,"professional_review_flags":["Verify exact Master Plan/Zonal Plan land use.","Check protected monument/heritage, airport funnel and other statutory height controls.","Check approved layout, lease/title conditions and road widening.","Preliminary design/compliance aid only; not statutory approval."]})

def parking_for_dwelling_units(unit_areas_sqm):
    ecs=sum(1.5 if a>150 else 1.25 if a>100 else 1.0 if a>50 else 0 for a in unit_areas_sqm)
    return {"dwelling_units":len(unit_areas_sqm),"ecs":round(ecs,2),"parking_area_sqm_at_13_75_per_ecs":round(ecs*13.75,2),"source_clause":"UP 2025 §3.3.4.1 and §3.3.4.3(1)"}

def make_dxf_rectangles(frontage_m,depth_m,setbacks,building_width_m=None,building_depth_m=None):
    sw,se,sf,sr=[setbacks[k] for k in ("side1_m","side2_m","front_m","rear_m")]
    bw=building_width_m or max(.1,frontage_m-sw-se); bd=building_depth_m or max(.1,depth_m-sf-sr)
    x0,y0=sw,sf; x1,y1=x0+bw,y0+bd
    def p(layer,a,b,c,d):
        return f"0\nLWPOLYLINE\n8\n{layer}\n90\n4\n70\n1\n10\n{a}\n20\n{b}\n10\n{c}\n20\n{b}\n10\n{c}\n20\n{d}\n10\n{a}\n20\n{d}\n"
    return "0\nSECTION\n2\nHEADER\n0\nENDSEC\n0\nSECTION\n2\nENTITIES\n"+p("PLOT",0,0,frontage_m,depth_m)+p("BUILDING",x0,y0,x1,y1)+"0\nENDSEC\n0\nEOF\n"
