// geofence.js — เช็คว่าพิกัดที่ส่ง report เข้ามาอยู่ในเขตไทยไหม + อยู่ในพื้นที่ชายแดนไหม
// ข้อมูล: thailand_provinces_simplified.geojson (บนบก 77 จังหวัด, GISTDA)
//         thailand_maritime_zones.geojson (เขตทางทะเล 13 polygon, GISTDA L13_MarineZone)
//         thailand_border_line.geojson (แนวชายแดนทางบก 31 จังหวัด — derive จากสองไฟล์บน)
// ทุกไฟล์ย่อไว้ ~150-200 ม. — คลาดเคลื่อนแถวเส้นเขตได้ระดับร้อยเมตร ซึ่งหยาบกว่า GPS
// ผู้ใช้อยู่แล้ว จึงตั้งใจให้ "ผ่อนผัน" ไว้ ดีกว่าปฏิเสธคนในหมู่บ้านชายแดนจริง ๆ

import { readFileSync } from "node:fs";

// เขตทะเลที่ยอมให้ส่ง report ได้ — เรือ/ชายฝั่งยังจับสัญญาณเสาบนบกได้ ส่วน EEZ/JDA ไกลเกินจะมีบริการ
export const MARINE_OK = ["Internal Water", "Territorial Sea", "Contiguous Zone"];

// รัศมีพื้นที่ชายแดนเริ่มต้น — ในไทย ห่างจากแนวชายแดนทางบกไม่เกิน 3.5 กม. (ส่งค่าอื่นตอนเรียกได้)
export const BORDER_KM = 3.5;

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

// ---------- ระยะจากจุดถึงแนวชายแดน ----------
// ใช้ระนาบท้องถิ่น (equirectangular) รอบจุดที่ถาม — ที่ระยะไม่กี่ กม. คลาดเคลื่อน < 0.1%
const M_PER_DEG_LAT = 110574;
const mPerDegLng = lat => 111320 * Math.cos((lat * Math.PI) / 180);

const segDist = (px, py, ax, ay, bx, by) => {
  const dx = bx - ax, dy = by - ay;
  const len2 = dx * dx + dy * dy;
  const t = len2 === 0 ? 0 : Math.max(0, Math.min(1, ((px - ax) * dx + (py - ay) * dy) / len2));
  return Math.hypot(px - ax - t * dx, py - ay - t * dy);
};

// แตก LineString/MultiLineString เป็นชุดเส้น + bbox ไว้กรองเร็ว ๆ ตอน query
const prepLines = features => features.map(f => {
  const g = f.geometry;
  const lines = g.type === "LineString" ? [g.coordinates] : g.coordinates;
  let minX = 180, minY = 90, maxX = -180, maxY = -90;
  for (const l of lines) for (const [x, y] of l) {
    if (x < minX) minX = x; if (x > maxX) maxX = x;
    if (y < minY) minY = y; if (y > maxY) maxY = y;
  }
  return { lines, bbox: [minX, minY, maxX, maxY], props: f.properties };
});

/** ระยะทางตรงจากพิกัดถึงแนวชายแดนทางบกที่ใกล้ที่สุด (กม.) — null ถ้าไม่ได้โหลดไฟล์ชายแดน */
export function borderDistanceKm(lat, lng, data) {
  if (!data.border || !data.border.length) return null;
  const kx = mPerDegLng(lat), ky = M_PER_DEG_LAT;
  const px = lng * kx, py = lat * ky;
  let best = Infinity;
  for (const { lines, bbox } of data.border) {
    // กรองด้วย bbox ก่อน: ถ้ากล่องยังไกลกว่าคำตอบที่ดีที่สุด ข้ามทั้งจังหวัด
    const gapX = Math.max(bbox[0] - lng, lng - bbox[2], 0) * kx;
    const gapY = Math.max(bbox[1] - lat, lat - bbox[3], 0) * ky;
    if (Math.hypot(gapX, gapY) >= best) continue;
    for (const line of lines) {
      for (let i = 1; i < line.length; i++) {
        const d = segDist(px, py, line[i - 1][0] * kx, line[i - 1][1] * ky,
                                  line[i][0] * kx, line[i][1] * ky);
        if (d < best) best = d;
      }
    }
  }
  return best === Infinity ? null : best / 1000;
}

export const load = (landPath = "thailand_provinces_simplified.geojson",
                     marinePath = "thailand_maritime_zones.geojson",
                     borderPath = "thailand_border_line.geojson") => ({
  land: JSON.parse(readFileSync(landPath, "utf8")).features,
  marine: JSON.parse(readFileSync(marinePath, "utf8")).features,
  border: prepLines(JSON.parse(readFileSync(borderPath, "utf8")).features),
});

/** lat/lng → { allowed, province, zone, borderKm, borderZone } ; allowed = ส่ง report ได้ */
export function locate(lat, lng, data, borderKm = BORDER_KM) {
  const pt = [lng, lat];
  const prov = data.land.find(f => f.geometry && inGeometry(pt, f.geometry));
  if (prov) {
    const km = borderDistanceKm(lat, lng, data);
    return {
      allowed: true,
      province: prov.properties.p_name_t,
      code: prov.properties.p_code,
      ...(km === null ? {} : { borderKm: Math.round(km * 100) / 100, borderZone: km <= borderKm }),
    };
  }
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

  // พื้นที่ชายแดน 3.5 กม.
  const border = [
    [20.4433, 99.8797, true, "แม่สาย เชียงราย (ติดท่าขี้เหล็ก)"],
    [16.7128, 98.5075, true, "แม่สอด ตาก (สะพานมิตรภาพ)"],
    [17.8782, 102.7418, true, "หนองคาย (ริมโขง)"],
    [6.0246, 101.9686, true, "สุไหงโก-ลก นราธิวาส"],
    [13.7563, 100.5018, false, "กรุงเทพ"],
    [18.7883, 98.9853, false, "เชียงใหม่เมือง"],
    [16.4322, 102.8236, false, "ขอนแก่น"],
  ];
  for (const [lat, lng, want, label] of border) {
    const r = locate(lat, lng, d);
    console.log(`${want === r.borderZone ? "ok  " : "FAIL"} ${label} → ${r.borderKm} กม. จากชายแดน`);
    assert.strictEqual(r.borderZone, want, label);
  }
  console.log("all ok");
}
