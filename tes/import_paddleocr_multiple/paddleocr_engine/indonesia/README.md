# Indonesian License Plate Processor

Proses hasil deteksi OCR untuk validasi dan koreksi otomatis plat nomor kendaraan Indonesia.

## 🎯 Tujuan

Memperbaiki kesalahan umum OCR dalam membaca plat nomor, seperti:
- Huruf `O` terbaca sebagai angka `0` (dan sebaliknya)
- Huruf `B` terbaca sebagai angka `8` (dan sebaliknya)
- Huruf `I` terbaca sebagai angka `1` (dan sebaliknya)
- Huruf `S` terbaca sebagai angka `5` (dan sebaliknya)
- Dan lainnya

## 📋 Struktur Plat Nomor Indonesia

```
[Huruf Wilayah] [Nomor Registrasi] [Huruf Seri]
```

**Contoh:**
- `B 1234 CD` - Jakarta
- `BK 987 AB` - Medan
- `D 12 A` - Bandung

### Aturan Validasi

| Komponen | Format | Keterangan |
|----------|--------|------------|
| **Huruf Wilayah** | 1-2 huruf | Kode daerah registrasi |
| **Nomor Registrasi** | 1-4 angka | Nomor urut pendaftaran |
| **Huruf Seri** | 0-3 huruf | Pembeda kendaraan |

### Karakter yang Tidak Boleh Ada di Seri

Huruf `I` dan `Q` biasanya tidak digunakan di seri plat nomor Indonesia.

## ⚙️ Konfigurasi

Edit file `.env`:

```env
# Enable Indonesian Plate Processor
# True = Validate and correct detected text
# False = Return OCR results as-is
USE_INDONESIAN_PLATE_PROCESSOR=True

# Fallback behavior if validation fails
# True = Return original text if format doesn't match
# False = Return corrected text even if invalid
INDONESIAN_PLATE_FALLBACK_TO_ORIGINAL=True
```

## 🔧 Koreksi Otomatis

### Di Bagian Angka (Number Section)
| Input OCR | Output Corrected | Keterangan |
|-----------|------------------|------------|
| `O`, `o` | `0` | Huruf O (capital/lowercase) |
| `Ø` | `0` | O dengan garis miring **kanan** ↗ (U+00D8) |
| `ø` | `0` | o dengan garis miring **kanan** ↗ (U+00F8) |
| `∅` | `0` | Empty Set symbol (U+2205) |
| `⦸` | `0` | Circled Vertical Stroke (U+29B8) |
| `Q`, `q` | `0` | Huruf Q |
| `B`, `b` | `8` | Huruf B |
| `I`, `i`, `l`, `L` | `1` | Huruf I/i/L/l |
| `S`, `s` | `5` | Huruf S |
| `Z`, `z` | `2` | Huruf Z |
| `G`, `g` | `6` | Huruf G |
| `J`, `j` | `9` | Huruf J |

### Di Bagian Huruf (Series Section)
| Input OCR | Output Corrected | Keterangan |
|-----------|------------------|------------|
| `0`, `Ø`, `ø`, `∅`, `⦸` | `O` | Semua variasi O |
| `o` | `O` | Lowercase o → O |
| `8`, `b` | `B` | Angka 8 / huruf b |
| `1` | `I` → `L` | Angka 1 (invalid, jadi L) |
| `5`, `s` | `S` | Angka 5 / huruf s |
| `2`, `z` | `Z` | Angka 2 / huruf z |
| `6`, `g` | `G` | Angka 6 / huruf g |
| `9`, `q` | `Q` → `O` | Angka 9 / q (invalid, jadi O) |

## 📊 Contoh Penggunaan

### Contoh 1: OCR Error pada Angka
```
Input OCR:  "BO123CD"
Output:     "B 123 CD"
Penjelasan: "O" di posisi angka dikoreksi menjadi "0", 
            tapi karena "BO" bukan region valid, 
            diparsing sebagai "B" + "0123" → "123"
```

### Contoh 2: OCR Error pada Seri
```
Input OCR:  "B12340B"
Output:     "B 1234 OB"
Penjelasan: "0" di posisi seri dikoreksi menjadi "O"
```

### Contoh 3: Format Tanpa Spasi
```
Input OCR:  "B1964SSJ"
Output:     "B 1964 SSJ"
Penjelasan: Ditambahkan format spasi standar
```

### Contoh 4: Huruf Invalid di Seri
```
Input OCR:  "B 1234 I"
Output:     "B 1234 L"
Penjelasan: "I" di seri diganti dengan "L"
```

### Contoh 5: Karakter Khusus Ø (O dengan Garis Miring)
```
Input OCR:  "B 1234 Ø"
Output:     "B 1234 O"
Penjelasan: "Ø" (garis miring kanan ↗) di posisi seri → O

Input OCR:  "BØ123CD"
Output:     "B 123 CD"
Penjelasan: "Ø" di posisi angka → 0

Input OCR:  "B 1234 ø"
Output:     "B 1234 O"
Penjelasan: "ø" (lowercase dengan garis miring) di posisi seri → O

Input OCR:  "Bø123CD"
Output:     "B 123 CD"
Penjelasan: "ø" di posisi angka → 0

Input OCR:  "Bo123CD"
Output:     "B 123 CD"
Penjelasan: "o" (lowercase) di posisi angka → 0
```

**Catatan:** Saat ini support untuk garis miring ke **kanan** (↗). 
Format Unicode:
- `Ø` (U+00D8) - Latin Capital Letter O with Stroke
- `ø` (U+00F8) - Latin Small Letter O with Stroke

## 🧪 Testing

### Test Unit
```bash
cd D:\Github\sc_python_camera_paddleocr\V5_PaddleOCR_Mobile_Only
python indonesia\plat_processor.py
```

### Test Integrasi dengan OCR
```bash
python test_indonesian_plate_processor.py
```

## 📁 File Structure

```
V5_PaddleOCR_Mobile_Only/
├── .env                              # Konfigurasi
├── app_gui.py                        # GUI Application
├── main.py                           # Main Application
├── indonesia/
│   ├── plat_processor.py             # Plate Processor Module
│   └── struktur_plat_nomor.txt       # Dokumentasi Struktur
└── test_indonesian_plate_processor.py # Integration Test
```

## 🔍 Valid Region Codes

### Single Letter
`A, B, D, E, F, G, H, K, L, M, N, P, R, S, T, U, W, X, Z`

### Double Letters
`AA, AB, AD, AE, AG, BA, BB, BD, BE, BG, BH, BK, BL, BM, BN, BP, BR, BS, DA, DB, DC, DD, DE, DG, DH, DK, DL, DM, DN, DP, DR, DS, DT, DU, EA, EB, ED, EK, EL, EP, ES, ET, KB, KH, KT, KV, KY`

## ⚠️ Fallback Behavior

Jika `INDONESIAN_PLATE_FALLBACK_TO_ORIGINAL=True`:
- Input yang tidak sesuai format plat nomor Indonesia akan dikembalikan apa adanya
- Contoh: `"BLURRY TEXT"` → `"BLURRY TEXT"` (tidak diproses)

Jika `INDONESIAN_PLATE_FALLBACK_TO_ORIGINAL=False`:
- Input akan tetap dikoreksi meskipun tidak sesuai format
- Contoh: `"ABCDE"` → `"A 8 CDE"` (dipaksakan parse)

**Rekomendasi:** Gunakan `True` untuk hasil yang lebih akurat.

## 📝 Change Log

**Version 1.0.0** - 2026-03-07
- ✅ Initial release
- ✅ Parse plat nomor dengan/spasi tanpa spasi
- ✅ Koreksi otomatis huruf ↔ angka
- ✅ Validasi region codes
- ✅ Fallback ke original jika invalid
- ✅ Integrasi dengan GUI dan CLI

## 🙏 Credits

Based on:
- **Struktur Plat Nomor Indonesia** - Kementerian Perhubungan RI
- **PaddleOCR v5** - Baidu
- **Indonesian Vehicle Registration** - Wikipedia
