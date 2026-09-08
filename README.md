# Thailand Boundary — ขอบเขตประเทศไทย GeoJSON (77 จังหวัด + ขอบประเทศ + พื้นที่ชายแดน + เขตทางทะเล)

ไฟล์ GeoJSON ขอบเขตประเทศไทยพร้อมใช้ — **77 จังหวัด**, **เส้นขอบนอกประเทศ** (polygon ก้อนเดียว ไม่แบ่งจังหวัด — มีทั้งแบบเฉพาะแผ่นดิน และแบบรวมทะเลถึง EEZ), **แนวชายแดนทางบก + พื้นที่ชายแดน 3.5 กม.** และ **เขตทางทะเล** (น่านน้ำภายใน, ทะเลอาณาเขต 12 ไมล์ทะเล, เขตต่อเนื่อง 24 ไมล์ทะเล, เขตเศรษฐกิจจำเพาะ/EEZ 200 ไมล์ทะเล, พื้นที่พัฒนาร่วมไทย-มาเลเซีย) ข้อมูลจาก **GISTDA** ใช้ทำ **geofence / point-in-polygon** เช็คว่าพิกัด lat-lng อยู่ในประเทศไทยหรือจังหวัดใด **หรืออยู่ในพื้นที่ชายแดนหรือไม่** สำหรับกันการส่ง report จากนอกประเทศ, ตรวจพื้นที่ให้บริการ, คัดกรองพิกัดในพื้นที่ชายแดน หรือวาดแผนที่ไทย

## ลิงก์

- **ดู POC (แผนที่คลิกทดสอบพิกัด):** https://hydrogenb.github.io/Thailand-Boundary/thailand_gistda_boundary_poc.html
- **โหลด JSON ตรง ๆ** (ใส่ใน `fetch`/`curl` ได้เลย):
  - จังหวัด ย่อ 584 KB — https://raw.githubusercontent.com/HydrogenB/Thailand-Boundary/main/thailand_provinces_simplified.geojson
  - จังหวัด เต็ม 39 MB — https://raw.githubusercontent.com/HydrogenB/Thailand-Boundary/main/thailand_provinces_full.geojson
  - เขตทางทะเล 54 KB — https://raw.githubusercontent.com/HydrogenB/Thailand-Boundary/main/thailand_maritime_zones.geojson
  - **ขอบนอกประเทศ (แผ่นดิน)** 197 KB — https://raw.githubusercontent.com/HydrogenB/Thailand-Boundary/main/thailand_outline.geojson
  - **ขอบนอกประเทศ (รวมทะเลถึง EEZ)** 99 KB — https://raw.githubusercontent.com/HydrogenB/Thailand-Boundary/main/thailand_outline_with_sea.geojson
  - **แนวชายแดนทางบก** 106 KB — https://raw.githubusercontent.com/HydrogenB/Thailand-Boundary/main/thailand_border_line.geojson
  - **พื้นที่ชายแดน** 1 / 3.5 / 5 / 10 กม. ~155-175 KB — https://raw.githubusercontent.com/HydrogenB/Thailand-Boundary/main/thailand_border_zone_3_5km.geojson (เปลี่ยน `3_5` เป็น `1`, `5`, `10` ได้)
  - แนวชายฝั่ง 108 KB — https://raw.githubusercontent.com/HydrogenB/Thailand-Boundary/main/thailand_coastline.geojson
- **ดึงจาก GISTDA เองแบบสด** (ปรับ field/ความละเอียดเองได้ ไม่ต้องผ่านรีโปนี้):
  - จังหวัด — [Province_TH/FeatureServer/0](https://gistdaportal.gistda.or.th/arcgis/rest/services/Hosted/Province_TH/FeatureServer/0)
  - เขตทางทะเล — [L13_MarineZone/FeatureServer/0](https://gistdaportal.gistda.or.th/arcgis/rest/services/Hosted/L13_MarineZone_GISTDA_xxk_Yxxx/FeatureServer/0)
  - ชั้นข้อมูลทั้งหมด 2,000+ ชั้น — [ArcGIS services directory ของ GISTDA](https://gistdaportal.gistda.or.th/arcgis/rest/services/Hosted)
  - วิธีเขียน query (`where`, `outFields`, `maxAllowableOffset`, `f=geojson`) — [ArcGIS REST API: Query (Feature Service)](https://developers.arcgis.com/rest/services-reference/enterprise/query-feature-service-layer/)

ตัวอย่างดึงสดเป็น GeoJSON ย่อ 0.002°:

```bash
curl "https://gistdaportal.gistda.or.th/arcgis/rest/services/Hosted/Province_TH/FeatureServer/0/query?where=1%3D1&outFields=p_code,p_name_t,p_name_e&returnGeometry=true&outSR=4326&maxAllowableOffset=0.002&f=geojson" -o provinces.geojson
```

## ไฟล์

| ไฟล์ | ขนาด | คำอธิบาย |
|---|---|---|
| `thailand_provinces_simplified.geojson` | 584 KB | 77 จังหวัด ย่อ ~0.002° (≈200 ม.) — ใช้ตัวนี้เป็นค่าเริ่มต้น |
| `thailand_provinces_full.geojson` | 39 MB | 77 จังหวัด เต็มความละเอียด |
| `thailand_maritime_zones.geojson` | 54 KB | เขตทางทะเล 13 polygon (`name_th`, `name_eng`) |
| `thailand_outline.geojson` | 197 KB | **เส้นขอบนอกประเทศ (แผ่นดิน)** — 1 feature MultiPolygon 361 ก้อน (แผ่นดินใหญ่ + เกาะ) ไม่มีเส้นจังหวัด |
| `thailand_outline_with_sea.geojson` | 99 KB | **เส้นขอบนอกประเทศ (รวมทะเล)** — 1 feature Polygon ก้อนเดียว แผ่นดิน + น่านน้ำภายใน + ทะเลอาณาเขต + เขตต่อเนื่อง + EEZ **ไม่รวมพื้นที่พัฒนาร่วมไทย-มาเลเซีย** · 823,668 ตร.กม. |
| `thailand_border_line.geojson` | 106 KB | **แนวชายแดนทางบก** 5,697 กม. แยกเป็น 31 จังหวัดชายแดน (LineString) |
| `thailand_border_zone_3_5km.geojson` | 157 KB | **พื้นที่ชายแดน** — ในไทยห่างแนวชายแดน ≤ 3.5 กม. 17,088 ตร.กม. 31 จังหวัด |
| `thailand_border_zone_1km.geojson` | 175 KB | พื้นที่ชายแดน 1 กม. — 5,339 ตร.กม. 31 จังหวัด |
| `thailand_border_zone_5km.geojson` | 154 KB | พื้นที่ชายแดน 5 กม. — 23,711 ตร.กม. 31 จังหวัด |
| `thailand_border_zone_10km.geojson` | 156 KB | พื้นที่ชายแดน 10 กม. — 44,667 ตร.กม. 32 จังหวัด |
| `thailand_coastline.geojson` | 108 KB | แนวชายฝั่ง 5,107 กม. 23 จังหวัดติดทะเล (ส่วนที่เหลือของขอบนอก) |
| `build_border_geojson.py` | — | สคริปต์ที่ derive 4 ไฟล์บนจากไฟล์จังหวัด+ทะเลในรีโป (`--km` เปลี่ยนรัศมีได้) |
| `geofence.js` | — | `locate(lat, lng)` → อยู่ในไทยไหม / จังหวัดอะไร / เขตทะเลไหน / ห่างชายแดนกี่ กม. |
| `thailand_gistda_boundary_poc.html` | — | แผนที่ Leaflet: คลิกทดสอบพิกัด, ตรวจพิกัดเป็นชุด, เปิด-ปิดชั้นขอบประเทศ/ชายแดน, เทียบข้อมูลกับ GISTDA สด |

EPSG:4326 (WGS84, `[lng, lat]`) · properties จังหวัด: `p_code`, `p_name_t`, `p_name_e`

## ใช้งาน

```js
import { locate, load, BORDER_KM } from "./geofence.js";

const data = load();                     // โหลดครั้งเดียวตอน boot (จังหวัด + ทะเล + แนวชายแดน)

locate(13.7563, 100.5018, data);         // กรุงเทพ  { allowed: true, province: "กรุงเทพมหานคร", code: "10",
                                         //            borderKm: 143.58, borderZone: false }
locate(20.4433, 99.8797, data);          // แม่สาย   { allowed: true, province: "จังหวัดเชียงราย", code: "57",
                                         //            borderKm: 0.13, borderZone: true }   ← พื้นที่ชายแดน
locate(12.5, 100.5, data);               // { allowed: true, zone: "Territorial Sea" }
locate(1.3521, 103.8198, data);          // { allowed: false, zone: null }  ← สิงคโปร์

locate(20.4433, 99.8797, data, 10);      // เปลี่ยนรัศมีพื้นที่ชายแดนเป็น 10 กม. (ค่าเริ่มต้น BORDER_KM = 3.5)
```

แก้เขตทะเลที่ยอมรับได้ที่ `MARINE_OK` ใน `geofence.js` · self-check: `node geofence.js`

`borderZone` คิดจาก **ระยะถึงแนวชายแดน** (`thailand_border_line.geojson`) ไม่ได้ทำ point-in-polygon กับไฟล์ zone
จึงเปลี่ยนรัศมีตอน runtime ได้เลยไม่ต้อง build ใหม่ — ไฟล์ `thailand_border_zone_3_5km.geojson` ไว้สำหรับ **วาดแผนที่**

### POC บนแผนที่

`python -m http.server` แล้วเข้า `thailand_gistda_boundary_poc.html` (เปิดตรง ๆ ด้วย `file://` จะโหลดไฟล์ข้าง ๆ ไม่ได้) ทำอะไรได้บ้าง:

- เปิด-ปิดชั้น **ขอบนอกประเทศ (แผ่นดิน / รวมทะเล) / แนวชายแดน / พื้นที่ชายแดน** ทับกับ 77 จังหวัด และเขตทางทะเล
- **คลิกบนแผนที่** → บอกจังหวัด, เขตทางทะเล, ระยะถึงแนวชายแดน และเตือนเมื่ออยู่ในรัศมีที่ตั้งไว้
- **ตรวจพิกัดเป็นชุด** → วางลิสต์ `lat, lng, ชื่อ` ทีละหลายบรรทัด กด "ตรวจทั้งหมด" ได้ตารางผล
  (พื้นที่ชายแดน / ในประเทศ / นอกประเทศ) + หมุดสีบนแผนที่ + สรุปจำนวน
- สลับ **รัศมีพื้นที่ชายแดน** ระหว่าง 1 / 3.5 / 5 / 10 กม. → polygon บนแผนที่ ผลของจุดที่คลิกไว้
  และตารางที่ตรวจไว้แล้ว อัปเดตพร้อมกันทันที (ถ้าอยากได้รัศมีอื่นให้ build ไฟล์เพิ่มด้วย `--km`)

## ขอบประเทศ + พื้นที่ชายแดน มาจากไหน

สร้างจาก **ไฟล์ในรีโปนี้เท่านั้น** (`thailand_provinces_full.geojson` + `thailand_maritime_zones.geojson` ต้นทาง GISTDA)
ไม่ได้ใช้ข้อมูลขอบเขตจากแหล่งอื่นเลย รวมถึงไม่ใช้ polygon ประเทศเพื่อนบ้าน — รันซ้ำได้ด้วย:

```bash
pip install shapely pyproj
python3 build_border_geojson.py            # ค่าเริ่มต้น 3.5 กม.
python3 build_border_geojson.py --km 7.5   # รัศมีอื่น → thailand_border_zone_7_5km.geojson
```

ขั้นตอน:

1. **dissolve 77 จังหวัด** เป็น polygon ประเทศไทยก้อนเดียว → `thailand_outline.geojson` (แผ่นดินใหญ่ + เกาะ 360 เกาะ)
   แล้ว union กับเขตทางทะเลทุกเขต **ยกเว้นพื้นที่พัฒนาร่วมไทย-มาเลเซีย** → `thailand_outline_with_sea.geojson`
   (เกาะทั้งหมดถูกกลืนเข้าไปในทะเล เหลือ polygon เดียว ไม่มีรูและไม่มีเส้นแบ่งย่อยใด ๆ)
2. เอา **วงนอก (exterior ring)** ของทุกก้อนมาแบ่งเป็นช่วง แล้วยิง probe ออกนอกประเทศที่ระยะ 0.5 / 1 / 2 / 4 กม.
   ถ้า probe ตกใน polygon เขตทางทะเล = ช่วงนั้นเป็น **ชายฝั่ง** ถ้าไม่ตกเลย = **ชายแดนทางบก**
3. ชายแดนทางบกจริงของไทยเป็นเส้นต่อเนื่อง 2 เส้น (พม่า-ลาว-กัมพูชา และมาเลเซีย) จึงเก็บเฉพาะ component ที่ยาว ≥ 20 กม.
   เศษที่หลุด classify (ชายฝั่งอ่าวที่ไฟล์ทะเลไม่ครอบ, เกาะเล็ก) ถูกตัดออก
4. **พื้นที่ชายแดน** = buffer จากแนวชายแดนเข้ามา 3.5 กม. แล้ว intersect กับ polygon ประเทศ (ไม่ล้นออกนอกประเทศ)
   ตัดตามจังหวัดเป็น 1 feature ต่อจังหวัด · คำนวณบน Lambert Conformal Conic ของไทย (คลาดเคลื่อนสเกล < 0.1%)

ตัวเลขที่ได้ ใช้เช็คความถูกต้องคร่าว ๆ ได้:

| ผลลัพธ์ | ได้ | เทียบกับตัวเลขทางการ |
|---|---|---|
| จังหวัดที่มีชายแดนทางบก | **31** | 31 จังหวัดชายแดน ✓ |
| ความยาวชายแดนทางบก | **5,697 กม.** | ~5,656 กม. (พม่า 2,401 / ลาว 1,810 / กัมพูชา 798 / มาเลเซีย 647) |
| จังหวัดติดทะเล | **23** | 23 จังหวัดชายทะเล ✓ |
| พื้นที่แผ่นดิน | **514,354 ตร.กม.** | ~513,120 ตร.กม. |
| พื้นที่แผ่นดิน + ทะเล (ไม่รวมพื้นที่พัฒนาร่วม) | **823,668 ตร.กม.** | — (ทะเลจาก GISTDA 309,314 ตร.กม.) |
| พื้นที่ชายแดน 3.5 กม. | **17,088 ตร.กม.** | — (≈ 3.3% ของพื้นที่ประเทศ) |

properties ที่ใส่มาให้: `kind`, `p_code`, `p_name_t`, `p_name_e`, `length_km` (เส้น) / `area_km2` + `buffer_km` (พื้นที่)

## ข้อควรรู้

- ไฟล์ที่ย่อแล้วคลาดเคลื่อนแถวเส้นเขตระดับ **ร้อยเมตร** — หยาบกว่าความแม่นของ GPS มือถือ ใช้เป็น geofence ได้ แต่ไม่ใช้ตัดสินกรรมสิทธิ์ที่ดินหรือข้อพิพาทเขตแดน
- geofence เช็คได้แค่ "พิกัดที่เครื่องส่งมา" **ปลอมได้** ถ้าต้องกันจริงให้เทียบ MCC/MNC หรือ IP ฝั่ง server ด้วย
- POC มีตัวเทียบ (count + ผลรวมเส้นรอบ/พื้นที่) เตือนเมื่อ GISTDA แก้ข้อมูลใหม่กว่าไฟล์ในรีโป — snapshot 25 ส.ค. 2026
- แหล่งข้อมูล: GISTDA ArcGIS `Hosted/Province_TH` และ `Hosted/L13_MarineZone` — อ้างอิงเครดิต GISTDA เมื่อนำไปใช้ต่อ

### เฉพาะพื้นที่ชายแดน

- **ไม่ใช่ขอบเขตทางกฎหมาย** — เป็นแค่พื้นที่ 3.5 กม. เชิงเรขาคณิตจากเส้นเขตของ GISTDA ถ้าต้องใช้กับกฎเกณฑ์ที่มีผลผูกพัน ให้ยึดพื้นที่ที่หน่วยงานเจ้าของเรื่องประกาศเป็นตัวตัดสิน แล้วใช้ไฟล์นี้เป็นตัวเทียบ/วาดแผนที่เท่านั้น
- รีโปนี้มีถึงระดับ **จังหวัด** เท่านั้น ถ้าต้องการระดับอำเภอ/ตำบล เอา zone ไป intersect กับชั้นอำเภอของ GISTDA เอง (`Hosted/L05_Amphoe_2559`)
- แนวชายแดนไม่มี attribute บอกว่าฝั่งตรงข้ามเป็นประเทศใด เพราะรีโปนี้ไม่มีข้อมูลประเทศเพื่อนบ้าน — ระบุเป็นจังหวัดฝั่งไทย (`p_name_t`) แทน
- `thailand_outline_with_sea.geojson` ถมรูเล็ก ๆ ที่เกิดจากขอบ polygon ต้นทางไม่สนิท (รวม ~206 ตร.กม. รูใหญ่สุด ~10 ตร.กม.) เพื่อให้ได้ขอบนอกก้อนเดียวไม่พรุน · เขตทางทะเลย่อไว้ ~200 ม. อยู่แล้วตั้งแต่ต้นทาง
- เขตแดนบางช่วง (เช่น กลางลำน้ำโขง/สาละวิน, พื้นที่ยังไม่ปักปันสมบูรณ์) เป็นเส้นตามข้อมูล GISTDA ไม่ใช่ข้อยุติทางการทูต
- ปากน้ำ/เกาะในลำน้ำชายแดน (เช่น ปากน้ำกระบุรี) บางส่วนถูกตัดออกจากแนวชายแดนตามเกณฑ์ข้อ 3 — ตรงนั้น zone จะมาจากแนวบนฝั่งที่ใกล้ที่สุด

<sub>คำค้น: ขอบเขตประเทศไทย geojson, เส้นขอบประเทศไทย polygon, พื้นที่ชายแดน 3.5 กม., แนวชายแดนไทย geojson, จังหวัดชายแดน 31 จังหวัด, แผนที่จังหวัด 77 จังหวัด geojson, ทะเลอาณาเขตไทย, EEZ ไทย, thailand outline geojson, thailand border line geojson, thailand border zone buffer, thailand provinces geojson, thailand maritime boundary, geofence ประเทศไทย, point in polygon lat lng ไทย, GISTDA</sub>
