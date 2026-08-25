# Thailand Boundary — ขอบเขตประเทศไทย GeoJSON (77 จังหวัด + เขตทางทะเล)

ไฟล์ GeoJSON ขอบเขตประเทศไทยพร้อมใช้ — **77 จังหวัด** และ **เขตทางทะเล** (น่านน้ำภายใน, ทะเลอาณาเขต 12 ไมล์ทะเล, เขตต่อเนื่อง 24 ไมล์ทะเล, เขตเศรษฐกิจจำเพาะ/EEZ 200 ไมล์ทะเล, พื้นที่พัฒนาร่วมไทย-มาเลเซีย) ข้อมูลจาก **GISTDA** ใช้ทำ **geofence / point-in-polygon** เช็คว่าพิกัด lat-lng อยู่ในประเทศไทยหรือจังหวัดใด สำหรับกันการส่ง report จากนอกประเทศ, ตรวจพื้นที่ให้บริการ, หรือวาดแผนที่ไทย

## ไฟล์

| ไฟล์ | ขนาด | คำอธิบาย |
|---|---|---|
| `thailand_provinces_simplified.geojson` | 584 KB | 77 จังหวัด ย่อ ~0.002° (≈200 ม.) — ใช้ตัวนี้เป็นค่าเริ่มต้น |
| `thailand_provinces_full.geojson` | 39 MB | 77 จังหวัด เต็มความละเอียด |
| `thailand_maritime_zones.geojson` | 54 KB | เขตทางทะเล 13 polygon (`name_th`, `name_eng`) |
| `geofence.js` | — | `locate(lat, lng)` → อยู่ในไทยไหม / จังหวัดอะไร / เขตทะเลไหน |
| `thailand_gistda_boundary_poc.html` | — | แผนที่ Leaflet คลิกทดสอบพิกัด + เทียบข้อมูลกับ GISTDA สด |

EPSG:4326 (WGS84, `[lng, lat]`) · properties จังหวัด: `p_code`, `p_name_t`, `p_name_e`

## ใช้งาน

```js
import { locate, load } from "./geofence.js";

const data = load();                     // โหลดครั้งเดียวตอน boot
locate(13.7563, 100.5018, data);         // { allowed: true, province: "กรุงเทพมหานคร", code: "10" }
locate(12.5, 100.5, data);               // { allowed: true, zone: "Territorial Sea" }
locate(1.3521, 103.8198, data);          // { allowed: false, zone: null }  ← สิงคโปร์
```

แก้เขตทะเลที่ยอมรับได้ที่ `MARINE_OK` ใน `geofence.js` · self-check: `node geofence.js`

เปิดแผนที่ทดสอบ: `python -m http.server` แล้วเข้า `thailand_gistda_boundary_poc.html` (เปิดตรง ๆ ด้วย `file://` จะโหลดไฟล์ข้าง ๆ ไม่ได้)

## ข้อควรรู้

- ไฟล์ที่ย่อแล้วคลาดเคลื่อนแถวเส้นเขตระดับ **ร้อยเมตร** — หยาบกว่าความแม่นของ GPS มือถือ ใช้เป็น geofence ได้ แต่ไม่ใช้ตัดสินกรรมสิทธิ์ที่ดินหรือข้อพิพาทเขตแดน
- geofence เช็คได้แค่ "พิกัดที่เครื่องส่งมา" **ปลอมได้** ถ้าต้องกันจริงให้เทียบ MCC/MNC หรือ IP ฝั่ง server ด้วย
- POC มีตัวเทียบ (count + ผลรวมเส้นรอบ/พื้นที่) เตือนเมื่อ GISTDA แก้ข้อมูลใหม่กว่าไฟล์ในรีโป — snapshot 25 ส.ค. 2026
- แหล่งข้อมูล: GISTDA ArcGIS `Hosted/Province_TH` และ `Hosted/L13_MarineZone` — อ้างอิงเครดิต GISTDA เมื่อนำไปใช้ต่อ

<sub>คำค้น: ขอบเขตประเทศไทย geojson, แผนที่จังหวัด 77 จังหวัด geojson, ทะเลอาณาเขตไทย, EEZ ไทย, thailand provinces geojson, thailand maritime boundary, thailand territorial sea shapefile, geofence ประเทศไทย, point in polygon lat lng ไทย, GISTDA</sub>
