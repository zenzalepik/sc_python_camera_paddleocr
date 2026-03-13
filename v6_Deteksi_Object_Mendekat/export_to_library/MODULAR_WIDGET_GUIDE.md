# MODULAR WIDGET GUIDE  
  
## Cara Membuat Widget Modular  
  
File `main.py` (70KB) terlalu panjang untuk dikonversi otomatis.  
Berikut adalah langkah-langkah manual:  
  
### Option 1: Gunakan main.py sebagai Library  
  
```python  
import sys  
sys.path.insert(0, r'export_to_library')  
from main import RealTimeDistanceDetector  
  
detector = RealTimeDistanceDetector(camera_id=0)  
detector.run()  
```  
  
### Option 2: Copy Manual ke Project  
  
1. Copy semua file dari `export_to_library` ke project Anda  
2. Install dependencies: `pip install -r requirements.txt`  
3. Run: `python main.py`  
  
### Option 3: Extract Widget Class (RECOMMENDED)  
  
Untuk membuat widget yang bisa di-embed di tkinter app:  
  
1. Buka file `main.py`  
2. Extract class-class berikut:  
   - `ObjectDistanceTracker`  
   - `ParkingSession`  
   - `CaptureManager`  
   - `RealTimeDistanceDetector`  
3. Buat class baru `ObjectDistanceWidget(tk.Frame)`  
4. Embed di parent tkinter application 
