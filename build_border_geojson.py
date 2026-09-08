#!/usr/bin/env python3
"""สร้าง polygon เส้นขอบนอกประเทศไทย + แนวชายแดน + พื้นที่ชายแดน (border zone)

ที่มาข้อมูล: ใช้เฉพาะไฟล์ที่อยู่ในรีโปนี้ (ต้นทาง GISTDA) ไม่ดึงข้อมูลจากแหล่งอื่น
  - thailand_provinces_full.geojson  (77 จังหวัด เต็มความละเอียด)
  - thailand_maritime_zones.geojson  (เขตทางทะเล — ใช้แยกว่าเส้นไหนคือชายฝั่ง)

ผลลัพธ์
  - thailand_outline.geojson          เส้นขอบนอกประเทศ (รวมจังหวัดเป็นก้อนเดียว)
  - thailand_coastline.geojson        แนวชายฝั่งทะเล (แยกจังหวัด)
  - thailand_border_line.geojson      แนวชายแดนทางบก (แยกจังหวัด)
  - thailand_border_zone_3_5km.geojson  พื้นที่ในไทยห่างจากแนวชายแดน <= 3.5 กม. (ปรับด้วย --km) (แยกจังหวัด)

วิธีคิด "ชายแดนทางบก" (ใช้ข้อมูลในรีโปล้วน ๆ ไม่แตะข้อมูลประเทศเพื่อนบ้านจากที่อื่น)
  1. dissolve 77 จังหวัด -> polygon ประเทศไทย  แล้วเอาเฉพาะวงนอก (exterior ring) ของทุกก้อน
  2. แต่ละช่วงของเส้นขอบ ยิง probe ออกนอกประเทศที่ระยะ 0.5/1/2/4 กม.
     ถ้า probe ตกใน polygon เขตทางทะเล = ช่วงนั้น "ชายฝั่ง" ถ้าไม่ตกเลย = "ชายแดนทางบก"
  3. ชายแดนทางบกจริงของไทยเป็นเส้นต่อเนื่องยาว 2 เส้น (พม่า-ลาว-กัมพูชา และ มาเลเซีย)
     จึงเก็บเฉพาะ component ที่ยาว >= MIN_COMPONENT แล้วโยนเศษเกาะ/อ่าวที่หลุด classify ทิ้ง
ผลที่ได้ ~5,700 กม. เทียบกับตัวเลขทางการ ~5,656 กม. (พม่า 2,401 / ลาว 1,810 / กัมพูชา 798 / มาเลเซีย 647)
ไม่มี attribute บอกว่าฝั่งตรงข้ามเป็นประเทศใด เพราะรีโปนี้ไม่มีข้อมูลประเทศเพื่อนบ้าน — ระบุจังหวัดฝั่งไทยแทน

รัน: python3 build_border_geojson.py [--km 3.5]
"""
import argparse, json, os
import numpy as np
import shapely
from shapely.geometry import shape, mapping, MultiLineString, LineString
from shapely.ops import unary_union, transform, linemerge
from shapely.strtree import STRtree
from pyproj import Transformer

# LCC สำหรับประเทศไทย — ใช้คำนวณระยะ/บัฟเฟอร์เป็นเมตร (คลาดเคลื่อนสเกล < 0.1%)
LCC = "+proj=lcc +lat_1=8 +lat_2=19 +lat_0=13.5 +lon_0=101 +datum=WGS84 +units=m +no_defs"
FWD = Transformer.from_crs("EPSG:4326", LCC, always_xy=True).transform
INV = Transformer.from_crs(LCC, "EPSG:4326", always_xy=True).transform

PROBES = (500.0, 1000.0, 2000.0, 4000.0)   # ม. — ระยะยิง probe ออกนอกประเทศเพื่อเช็คว่าเจอทะเลไหม
MIN_COMPONENT = 20_000.0                   # ม. — ความยาวขั้นต่ำของเส้นชายแดนต่อเนื่อง 1 เส้น
SIMPLIFY = 150.0                           # ม. — ย่อรูปก่อนเขียนไฟล์
MIN_SEG = 200.0                            # ม. — ตัดเศษเส้นสั้นกว่านี้ทิ้ง


def fc(features):
    return {"type": "FeatureCollection",
            "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
            "features": features}


def round_geom(geom, nd=5):
    """ปัดพิกัดให้เหลือ 5 ตำแหน่ง (~1 ม.) เพื่อลดขนาดไฟล์"""
    def r(x, y, z=None):
        return (round(x, nd), round(y, nd))
    return transform(r, geom)


def write(path, features):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(fc(features), f, ensure_ascii=False, separators=(",", ":"))
    print(f"  {path}  ({len(features)} features, {round(os.path.getsize(path)/1024)} KB)")


def to_out(geom_m, simplify=SIMPLIFY):
    """simplify -> WGS84 -> ปัดพิกัด -> ซ่อม (simplify+ปัดพิกัดทำให้ ring เกยกันได้)"""
    g = round_geom(transform(INV, geom_m.simplify(simplify)))
    if g.geom_type in ("Polygon", "MultiPolygon") and not g.is_valid:
        g = shapely.make_valid(g)
        keep = [x for x in getattr(g, "geoms", [g]) if x.geom_type in ("Polygon", "MultiPolygon")]
        g = unary_union(keep)
    return mapping(g)


def clean_lines(geom, min_len=MIN_SEG):
    """เก็บเฉพาะเส้น ตัดเศษสั้น ๆ ทิ้ง แล้ว merge"""
    if geom.is_empty:
        return None
    parts = [g for g in getattr(geom, "geoms", [geom])
             if g.geom_type in ("LineString", "LinearRing") and g.length >= min_len]
    if not parts:
        return None
    merged = linemerge(MultiLineString([LineString(p.coords) for p in parts]))
    return merged


def split_coast_border(land, sea):
    """แยกเส้นขอบนอกประเทศเป็น (ชายฝั่ง, ชายแดนทางบก) ด้วยการยิง probe ออกนอกประเทศ"""
    shapely.prepare(land)
    shapely.prepare(sea)
    coast, border = [], []
    for poly in sorted(getattr(land, "geoms", [land]), key=lambda p: -p.area):
        c = np.asarray(poly.exterior.coords)
        if len(c) < 3:
            continue
        a, b = c[:-1], c[1:]
        mid = (a + b) / 2.0
        d = b - a
        ln = np.hypot(d[:, 0], d[:, 1])
        ln[ln == 0] = 1.0
        n = np.column_stack([d[:, 1], -d[:, 0]]) / ln[:, None]     # normal ของแต่ละช่วง
        # เลือกด้านที่ชี้ออกนอกประเทศ: ขยับ 50 ม. แล้วดูว่ายังอยู่ในแผ่นดินไหม
        inside = shapely.contains_xy(land, mid[:, 0] + n[:, 0] * 50.0, mid[:, 1] + n[:, 1] * 50.0)
        nn = n * np.where(inside, -1.0, 1.0)[:, None]
        is_coast = np.zeros(len(mid), bool)
        for probe in PROBES:
            is_coast |= shapely.contains_xy(sea, mid[:, 0] + nn[:, 0] * probe,
                                                 mid[:, 1] + nn[:, 1] * probe)
        i = 0
        while i < len(mid):                                        # จับช่วงที่ผลเหมือนกันติดกัน
            j = i
            while j < len(mid) and is_coast[j] == is_coast[i]:
                j += 1
            (coast if is_coast[i] else border).append(LineString(c[i:j + 1]))
            i = j
    border_line = linemerge(unary_union(border))
    keep = [g for g in getattr(border_line, "geoms", [border_line]) if g.length >= MIN_COMPONENT]
    print(f"  ชายแดนทางบก: เก็บ {len(keep)} เส้นต่อเนื่อง"
          f" ({', '.join(f'{g.length/1000:,.0f} กม.' for g in keep)})")
    border_line = unary_union(keep)
    ext = MultiLineString([p.exterior for p in getattr(land, "geoms", [land])])
    return ext.difference(border_line.buffer(1.0)), border_line


def main(km):
    print("โหลดข้อมูลจากรีโป …")
    prov = json.load(open("thailand_provinces_full.geojson", encoding="utf-8"))["features"]
    sea = json.load(open("thailand_maritime_zones.geojson", encoding="utf-8"))["features"]

    prov_m = []
    for f in prov:
        if not f.get("geometry"):
            continue
        prov_m.append((f["properties"], transform(FWD, shape(f["geometry"])).buffer(0)))
    land = unary_union([g for _, g in prov_m])
    sea_m = unary_union([transform(FWD, shape(f["geometry"])).buffer(0) for f in sea])

    # ---- 1) เส้นขอบนอกประเทศ (dissolve 77 จังหวัด) ----
    print("รวมจังหวัดเป็นขอบประเทศ …")
    parts = sorted(getattr(land, "geoms", [land]), key=lambda p: -p.area)
    write("thailand_outline.geojson", [{
        "type": "Feature",
        "properties": {
            "name_th": "ประเทศไทย", "name_en": "Thailand", "iso": "TH",
            "source": "GISTDA Province_TH (dissolved 77 provinces)",
            "parts": len(parts),
            "area_km2": round(land.area / 1e6, 1),
            "perimeter_km": round(land.length / 1000, 1),
            "simplify_m": SIMPLIFY,
        },
        "geometry": to_out(land)}])

    # ---- 2) แยกขอบนอกเป็น ชายฝั่ง / ชายแดนทางบก ----
    print("แยกชายฝั่งกับชายแดนทางบก …")
    coast_all, border_all = split_coast_border(land, sea_m)
    print(f"  ขอบนอกรวม {land.length/1000:,.0f} กม."
          f" | ชายฝั่ง {coast_all.length/1000:,.0f} กม."
          f" | ชายแดนทางบก {border_all.length/1000:,.0f} กม.")

    # ---- 3) ตัดตามจังหวัด ----
    geoms = [g for _, g in prov_m]
    tree = STRtree(geoms)

    def by_province(line_geom, kind):
        feats = []
        for idx in tree.query(line_geom):
            props, pg = prov_m[idx]
            seg = clean_lines(line_geom.intersection(pg.buffer(1.0)))
            if seg is None or seg.length < MIN_SEG:
                continue
            feats.append({
                "type": "Feature",
                "properties": {
                    "kind": kind,
                    "p_code": props.get("p_code"),
                    "p_name_t": props.get("p_name_t"),
                    "p_name_e": props.get("p_name_e"),
                    "length_km": round(seg.length / 1000, 2),
                },
                "geometry": to_out(seg),
            })
        return sorted(feats, key=lambda f: -f["properties"]["length_km"])

    write("thailand_coastline.geojson", by_province(coast_all, "coastline"))
    border_feats = by_province(border_all, "land_border")
    write("thailand_border_line.geojson", border_feats)
    print("  จังหวัดที่มีชายแดนทางบก:", len(border_feats))

    # ---- 4) พื้นที่ชายแดน = บัฟเฟอร์จากแนวชายแดนเข้ามาในประเทศ km กม. ----
    print(f"สร้างพื้นที่ชายแดน {km} กม. …")
    zone = border_all.buffer(km * 1000.0).intersection(land)
    print(f"  พื้นที่รวม {zone.area/1e6:,.0f} ตร.กม.")
    zfeats = []
    for idx in tree.query(zone):
        props, pg = prov_m[idx]
        piece = zone.intersection(pg)
        if piece.is_empty or piece.area < 1e5:      # < 0.1 ตร.กม. ตัดทิ้ง
            continue
        zfeats.append({
            "type": "Feature",
            "properties": {
                "kind": "border_zone",
                "buffer_km": km,
                "p_code": props.get("p_code"),
                "p_name_t": props.get("p_name_t"),
                "p_name_e": props.get("p_name_e"),
                "area_km2": round(piece.area / 1e6, 1),
            },
            "geometry": to_out(piece.buffer(0)),
        })
    zfeats.sort(key=lambda f: -f["properties"]["area_km2"])
    write(f"thailand_border_zone_{str(km).replace('.', '_')}km.geojson", zfeats)
    print("  จังหวัดที่โดนพื้นที่ชายแดน:", len(zfeats))
    print("เสร็จ")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--km", type=float, default=3.5, help="ความกว้างพื้นที่ชายแดน (กม.) ค่าเริ่มต้น 3.5")
    main(ap.parse_args().km)
