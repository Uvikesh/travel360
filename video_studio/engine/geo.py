"""Map geometry: India states (SVG) + neighbouring land (Natural Earth via world-atlas).

All geometry is returned in the SVG coordinate space of india_states.svg (viewBox 0 0 612 696).
Neighbouring land is projected with the same projection the SVG uses (fitted once, see fit_projection).
"""
import json
import math
import os
import re
from functools import lru_cache

from svgelements import SVG, Path

ASSETS = os.path.join(os.path.dirname(__file__), "..", "assets", "map")


def _path_to_rings(path, step=0.6):
    """Flatten an svgelements Path into lists of (x, y) points, one list per subpath."""
    rings = []
    for sub in path.as_subpaths():
        sp = Path(sub)
        length = sp.length(error=1e-3)
        if length < 0.05:
            continue
        n = max(8, int(length / step))
        pts = [sp.point(i / n) for i in range(n + 1)]
        rings.append([(p.x, p.y) for p in pts])
    return rings


GEOJSON36 = os.path.join(ASSETS, "india36_osm.geojson")   # 28 states + 8 UTs, GoI depiction, (c) OSM contributors
ID_FIX = {"od": "or"}   # keep the ids older episodes use


@lru_cache(maxsize=1)
def india_states():
    """{state_id: {"name": str, "rings": [[(x,y),...], ...]}} in SVG space.
    Uses the 36-region OSM-derived map (Ladakh separate, official J&K/Ladakh depiction) when present."""
    if os.path.exists(GEOJSON36):
        return _states_from_geojson()
    return _states_from_svg()


@lru_cache(maxsize=1)
def _states_from_geojson(min_area=0.02):
    fc = json.load(open(GEOJSON36))
    out = {}
    for f in fc["features"]:
        sid = f["properties"]["code"].split("-")[1].lower()
        sid = ID_FIX.get(sid, sid)
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        rings = []
        for poly in polys:
            r = [project(lon, lat) for lon, lat in poly[0]]
            if abs(_area(r)) >= min_area or sid in ("ld", "an", "py", "dh", "ch", "dl", "ga"):
                rings.append(r)
        out[sid] = {"name": f["properties"]["name"], "rings": rings}
    # the OSM Lakshadweep feature is the maritime area, not the islands -> use the island outlines instead
    old = _states_from_svg()
    if "ld" in old:
        out["ld"] = old["ld"]
    return out


@lru_cache(maxsize=1)
def _states_from_svg():
    """{state_id: {"name": str, "rings": [[(x,y),...], ...]}}"""
    svg = SVG.parse(os.path.join(ASSETS, "india_states.svg"))
    raw = open(os.path.join(ASSETS, "india_states.svg"), encoding="utf-8").read()
    names = dict(re.findall(r'id="(\w+)"\s+aria-label="([^"]+)"', raw))
    states = {}
    for el in svg.elements():
        if isinstance(el, Path) and el.id:
            states[el.id] = {"name": names.get(el.id, el.id), "rings": _path_to_rings(el)}
    return states


# ---------------------------------------------------------------- topojson

def _decode_topo(topo, obj_name):
    sc = topo["transform"]["scale"]
    tr = topo["transform"]["translate"]
    arcs = []
    for arc in topo["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in arc:
            x += dx
            y += dy
            pts.append((x * sc[0] + tr[0], y * sc[1] + tr[1]))
        arcs.append(pts)

    def ring(idx_list):
        out = []
        for i in idx_list:
            a = arcs[i] if i >= 0 else arcs[~i][::-1]
            out.extend(a if not out else a[1:])
        return out

    feats = []
    obj = topo["objects"][obj_name]
    geoms = obj["geometries"] if obj["type"] == "GeometryCollection" else [obj]
    for g in geoms:
        polys = []
        if g["type"] == "Polygon":
            polys = [[ring(r) for r in g["arcs"]]]
        elif g["type"] == "MultiPolygon":
            polys = [[ring(r) for r in p] for p in g["arcs"]]
        feats.append({"id": g.get("id"), "name": g.get("properties", {}).get("name"), "polys": polys})
    return feats


def _merc_y(lat):
    return math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))


# Projection lon/lat -> SVG coords. Fitted by fit_projection() against the SVG's west/east/south extremes
# (those coastlines are identical in both datasets). Stored here so rendering does not refit each time.
PROJ = None


def fit_projection():
    """Fit a Mercator projection (uniform scale) that maps Natural Earth India onto the SVG."""
    st = _states_from_svg()
    xs = [p[0] for s in st.values() for r in s["rings"] for p in r]
    ys = [p[1] for s in st.values() for r in s["rings"] for p in r]
    topo = json.load(open(os.path.join(ASSETS, "countries-50m.json")))
    india = [f for f in _decode_topo(topo, "countries") if f["name"] == "India"][0]
    pts = [p for poly in india["polys"] for r in poly for p in r]
    # ignore Andaman/Nicobar & Lakshadweep for extremes: use mainland via longitude limits
    lons = [p[0] for p in pts]
    lats = [p[1] for p in pts]
    # x: Gujarat west tip ↔ Arunachal east tip
    k = (max(xs) - min(xs)) / (max(lons) - min(lons))
    x0 = min(xs) - k * min(lons)
    # y: south tip (Indira Point, Nicobar) — both datasets include it
    ky = k * 180 / math.pi
    y0 = max(ys) + ky * _merc_y(min(lats))
    return {"k": k, "x0": x0, "ky": ky, "y0": y0}


def project(lon, lat):
    global PROJ
    if PROJ is None:
        PROJ = fit_projection()
    return (PROJ["x0"] + PROJ["k"] * lon, PROJ["y0"] - PROJ["ky"] * _merc_y(lat))


@lru_cache(maxsize=1)
def world_land(lon_range=(55, 110), lat_range=(-5, 45)):
    """Land polygons (outer rings + holes) near India, in SVG coords."""
    topo = json.load(open(os.path.join(ASSETS, "land-50m.json")))
    out = []
    for f in _decode_topo(topo, "land"):
        for poly in f["polys"]:
            outer = poly[0]
            if not any(lon_range[0] <= x <= lon_range[1] and lat_range[0] <= y <= lat_range[1] for x, y in outer):
                continue
            out.append([[project(x, max(-80, min(80, y))) for x, y in r] for r in poly])
    return out


def state_bbox(state_id):
    rings = india_states()[state_id]["rings"]
    xs = [p[0] for r in rings for p in r]
    ys = [p[1] for r in rings for p in r]
    return min(xs), min(ys), max(xs), max(ys)


def state_centroid(state_id):
    """Area-weighted centroid of the largest ring (good anchor for stickers)."""
    rings = india_states()[state_id]["rings"]
    best = max(rings, key=lambda r: abs(_area(r)))
    a = _area(best)
    cx = cy = 0.0
    for (x1, y1), (x2, y2) in zip(best, best[1:] + best[:1]):
        c = x1 * y2 - x2 * y1
        cx += (x1 + x2) * c
        cy += (y1 + y2) * c
    return cx / (6 * a), cy / (6 * a)


def _area(r):
    return 0.5 * sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(r, r[1:] + r[:1]))
