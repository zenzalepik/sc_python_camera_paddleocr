# 🔄 Changelog - Object Distance Widget

## [1.0.1] - 2026-03-13

### ✨ Added
- **Download Progress Overlay** - Menampilkan progress saat YOLO model sedang didownload
  - Large download icon (📥)
  - Clear message: "⏳ Sedang mendownload YOLO..."
  - Subtitle: "Please wait while the model is being downloaded"
  - Dynamic status text showing current progress
  - Full-screen overlay covering video area

### 🐛 Fixed
- **Widget Stretch Issue** - Widget sekarang stretch sempurna mengikuti frame
  - Added `video_container` frame untuk layout yang lebih baik
  - Video resize menggunakan `video_container.winfo_width()/Height()`
  - Overlay menggunakan `place(relx=0, rely=0, relwidth=1, relheight=1)` untuk fill sempurna
  - Fallback handling jika ukuran widget belum tersedia

### 🔧 Improved
- **Error Handling** - Better error handling saat YOLO model loading
  - Try-catch block dengan error message yang jelas
  - Loading time tracking
  - User-friendly error display

### 📝 Changed
- Enhanced download UI dengan icon dan text yang lebih besar
- Improved overlay visibility dengan full-screen coverage
- Better UI update forcing dengan `self.update()` calls

---

## [1.0.0] - 2026-03-13

### 🎉 Initial Release
- Complete reusable widget from `v6_Deteksi_Object_Mendekat`
- All original features preserved 100%
- 4-phase parking system (SIAGA → TETAP → LOOP → TAP)
- SIAGA alert system
- Real-time object detection with YOLOv8
- Object distance tracking (mendekat/menjauh/tetap)
- CLEAN_UI mode
- Configuration via `widget_variables.py`
- Thread-safe execution
- Auto-resize support
- Callback support for parking sessions

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0.1 | 2026-03-13 | Fixed widget stretch & added YOLO download overlay |
| 1.0.0 | 2026-03-13 | Initial release |

---

**Last Updated:** 2026-03-13  
**Current Version:** 1.0.1
