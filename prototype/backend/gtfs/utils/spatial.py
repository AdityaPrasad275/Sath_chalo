from django.contrib.gis.geos import Point, LineString

def get_distance_on_shape(point: Point, shape_line: LineString) -> float:
    """
    Calculates the minimum distance in meters from the point to the shape.
    Assumes inputs are in SRID 4326.
    """
    # Project to Web Mercator (3857) for meter approximation.
    # Note: 3857 (Web Mercator) is not area-preserving but adequate for small distance checks
    # near the equator (Bangalore is ~13 degrees N).
    
    # We clone to avoid modifying the original objects if they are from ORM
    p_proj = point.transform(3857, clone=True)
    s_proj = shape_line.transform(3857, clone=True)
    return p_proj.distance(s_proj)

def is_off_route(point: Point, shape_line: LineString, threshold_meters=50.0) -> bool:
    dist = get_distance_on_shape(point, shape_line)
    return dist > threshold_meters
