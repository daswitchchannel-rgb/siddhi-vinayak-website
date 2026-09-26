CONTROL_POINTS=[{"name":"Kosi Kalan","pixel_x":1300,"pixel_y":1450,"lon":77.4368,"lat":27.7932},{"name":"Mathura","pixel_x":2470,"pixel_y":3339,"lon":77.67361,"lat":27.49250},{"name":"Vrindavan","pixel_x":2700,"pixel_y":2750,"lon":77.70000,"lat":27.58330},{"name":"Govardhan","pixel_x":1100,"pixel_y":3200,"lon":77.46120,"lat":27.49730},{"name":"Farah","pixel_x":3450,"pixel_y":4700,"lon":77.76221,"lat":27.32061}]
AFFINE={"lon":[0.000140474219,0.0000158060023,77.2983061],"lat":[0.00000718737110,-0.000155599633,27.9830061],"confidence":"reference","source":"Initial control-point fit to official MVDA 2031 map"}
def pixel_to_lonlat(x,y):
    a,b,c=AFFINE["lon"]; d,e,f=AFFINE["lat"]; return a*x+b*y+c,d*x+e*y+f
def lonlat_to_pixel(lon,lat):
    a,b=AFFINE["lon"][0],AFFINE["lon"][1]
    d,e=AFFINE["lat"][0],AFFINE["lat"][1]
    vx,vy=lon-AFFINE["lon"][2],lat-AFFINE["lat"][2]
    det=a*e-b*d
    x=(vx*e-b*vy)/det
    y=(a*vy-vx*d)/det
    return float(x),float(y)
def point_info(lon,lat):
    x,y=lonlat_to_pixel(lon,lat)
    return {"longitude":lon,"latitude":lat,"source_pixel":{"x":round(x,2),"y":round(y,2)},"overlay":"MVDA Master Plan 2031","confidence":"reference","warning":"Raster position is a planning-map reference, not a legally verified zoning/cadastral determination."}
