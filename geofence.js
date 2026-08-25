// geofence.js — เช็คว่าพิกัดที่ส่ง report เข้ามาอยู่ในเขตไทยไหม (ใช้กับระบบ Network care)
// ข้อมูล: thailand_provinces_simplified.geojson (บนบก 77 จังหวัด, GISTDA)
//         thailand_maritime_zones.geojson (เขตทางทะเล 13 polygon, GISTDA L13_MarineZone)
// ทั้งสองไฟล์ย่อที่ ~0.002° (≈200 ม.) — คลาดเคลื่อนแถวเส้นเขตได้ระดับร้อยเมตร ซึ่งหยาบกว่า GPS
// ผู้ใช้อยู่แล้ว จึงตั้งใจให้ "ผ่อนผัน" ไว้ ดีกว่าปฏิเสธคนในหมู่บ้านชายแดนจริง ๆ

import { readFileSync } from "node:fs";

// เขตทะเลที่ยอมให้ส่ง report ได้ — เรือ/ชายฝั่งยังจับสัญญาณเสาบนบกได้ ส่วน EEZ/JDA ไกลเกินจะมีบริการ
export const MARINE_OK = ["Internal Water", "Territorial Sea", "Contiguous Zone"];

// ---------- point in polygon (ray casting; ring[0] = outer, ring[1..] = holes) ----------
const inRing = ([x, y], ring) => {
  let hit = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const [xi, yi] = ring[i], [xj, yj] = ring[j];
    if ((yi > y) !== (yj > y) && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) hit = !hit;
  }
  return hit;
};
const inPolygon = (pt, poly) => inRing(pt, poly[0]) && !poly.slice(1).some(h => inRing(pt, h));
const inGeometry = (pt, g) =>
  g.type === "Polygon" ? inPolygon(pt, g.coordinates)
                       : g.coordinates.some(p => inPolygon(pt, p));

export const load = (landPath = "thailand_provinces_simplified.geojson",
                     marinePath = "thailand_maritime_zones.geojson") => ({
  land: JSON.parse(readFileSync(landPath, "utf8")).features,
  marine: JSON.parse(readFileSync(marinePath, "utf8")).features,
});

/** lat/lng → { allowed, province, zone } ; allowed = ส่ง report ได้ */
export function locate(lat, lng, data) {
  const pt = [lng, lat];
  const prov = data.land.find(f => f.geometry && inGeometry(pt, f.geometry));
  if (prov) return { allowed: true, province: prov.properties.p_name_t, code: prov.properties.p_code };
  const sea = data.marine
    .filter(f => f.geometry && inGeometry(pt, f.geometry))
    .map(f => f.properties.name_eng);
  const zone = MARINE_OK.find(z => sea.includes(z)) || sea[0] || null;
  return { allowed: MARINE_OK.includes(zone), zone };
}

// ---------- self-check: node geofence.js ----------
if (import.meta.filename === process.argv[1]) {
  const assert = (await import("node:assert")).default;
  const d = load();
  const cases = [
    [13.7563, 100.5018, true, "กรุงเทพ"],
    [18.7883, 98.9853, true, "เชียงใหม่"],
    [7.8804, 98.3923, true, "ภูเก็ต"],
    [12.5, 100.5, true, "อ่าวไทย (ทะเลอาณาเขต)"],
    [1.3521, 103.8198, false, "สิงคโปร์"],
    [11.5564, 104.9282, false, "พนมเปญ"],
    [21.0278, 105.8342, false, "ฮานอย"],
    [5.0, 90.0, false, "อ่าวเบงกอลกลางทะเล"],
  ];
  for (const [lat, lng, want, label] of cases) {
    const r = locate(lat, lng, d);
    console.log(`${want === r.allowed ? "ok  " : "FAIL"} ${label} → ${JSON.stringify(r)}`);
    assert.strictEqual(r.allowed, want, label);
  }
  console.log("all ok");
}
