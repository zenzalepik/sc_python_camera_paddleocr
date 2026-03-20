# 🐛 Bug Fix - Queue Access Logic

## Issue

Setelah klik "Open" dan select image, klik "Detect All" menampilkan error:
```
[WARNING] No images in queue!
[WARNING] Please click 'Open' first to add images
```

Padahal image sudah berhasil ditambahkan ke queue.

---

## Root Cause

**Inconsistent queue access** - ada 2 cara akses queue:

1. **`widget.images`** - Queue yang benar (digunakan di `open_image()`)
2. **`widget.gui.images`** - Queue yang salah (digunakan di fungsi lain)

### Code yang Bermasalah:

```python
# DI open_image() - BENAR ✅
self.widget.add_images(list(filepaths))  # Add ke widget.images

# DI detect_text() - SALAH ❌
if not self.widget.gui or not self.widget.gui.images:
    return

# DI _ocr_worker() - SALAH ❌
for i, img_data in enumerate(self.widget.gui.images):
    ...

# DI export_result() - SALAH ❌
results = [img for img in self.widget.gui.images if img.get('result')]

# DI clear_all() - SALAH ❌
queue_size = len(self.widget.gui.images)
```

---

## Solution

**Ganti semua akses `widget.gui.images` menjadi `widget.images`**

### Files Modified:
- `app.py`

### Changes:

#### 1. `detect_text()`
```python
# BEFORE ❌
if not self.widget.gui or not self.widget.gui.images:

# AFTER ✅
if not self.widget or not self.widget.images:
```

#### 2. `_ocr_worker()`
```python
# BEFORE ❌
for i, img_data in enumerate(self.widget.gui.images):
    ...

# AFTER ✅
for i, img_data in enumerate(self.widget.images):
    ...
```

#### 3. `export_result()`
```python
# BEFORE ❌
results = [img for img in self.widget.gui.images if img.get('result')]

# AFTER ✅
results = [img for img in self.widget.images if img.get('result')]
```

#### 4. `clear_all()`
```python
# BEFORE ❌
queue_size = len(self.widget.gui.images)

# AFTER ✅
queue_size = len(self.widget.images)
```

#### 5. `show_preview_image()`
```python
# BEFORE ❌
if self.widget.gui and 0 <= self.current_index < len(self.widget.gui.images):

# AFTER ✅
if self.widget and 0 <= self.current_index < len(self.widget.images):
```

---

## Why This Happened

Widget initialization:
```python
self.widget = PaddleOCRMultipleWidget(root=self.tk_root)
```

Constructor widget:
```python
def __init__(self, root=None, config=None):
    self.root = root
    self.gui = None  # ← TIDAK PERNAH DI-INIT!
    self.images = []  # ← INI YANG DIPAKAI
    
    if self.root:
        self._init_gui()  # ← Set self.gui = PaddleOCRMultipleInputGUI
```

Jadi:
- `widget.images` = `[]` (digunakan untuk queue)
- `widget.gui` = `PaddleOCRMultipleInputGUI instance` (tidak digunakan)
- `widget.gui.images` = `[]` (queue berbeda yang tidak pernah di-init)

---

## Testing

### Before Fix:
```
[OPEN] Added 1 images to queue
[OK] New queue size: 1

[DETECT] Queue information:
  - Total images: 0  ← SALAH!
[WARNING] No images in queue!
```

### After Fix:
```
[OPEN] Added 1 images to queue
[OK] New queue size: 1

[DETECT] Queue information:
  - Total images: 1  ← BENAR!
  - Pending: 1
[OK] OCR thread started
```

---

## Verification

Test flow:
1. ✅ Click "Open" → Select image
2. ✅ Click "Detect All" → Processing starts
3. ✅ Wait for OCR → Results shown
4. ✅ Click "Export" → Export works
5. ✅ Click "Clear" → Queue cleared

All buttons now working correctly!

---

## Impact

- ✅ **Open** button: Works (no change)
- ✅ **Detect All** button: Fixed (now detects images)
- ✅ **Export** button: Fixed (now exports results)
- ✅ **Clear** button: Fixed (now clears correct queue)

---

## Lesson Learned

**Consistent data access is critical!**

Always use:
- `widget.images` for queue access
- NOT `widget.gui.images` (unless gui is explicitly used)

Check widget structure before accessing properties.

---

**Fixed:** 2026-03-19  
**Version:** 2.1.1 (bug fix)  
**Status:** ✅ Resolved
