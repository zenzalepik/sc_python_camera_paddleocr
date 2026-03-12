"""
Script untuk download YOLOv3-Tiny weights
Jalankan script ini untuk download otomatis
"""

import os
import sys
import urllib.request

def download_yolov3_tiny():
    """Download YOLOv3-Tiny weights"""
    
    # URLs (mirror yang masih aktif)
    urls = [
        "https://pjreddie.com/media/files/yolov3-tiny.weights",
        "https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v3_pre/yolov3-tiny.weights",
    ]
    
    output_path = os.path.join(os.path.dirname(__file__), 'yolov3-tiny.weights')
    
    print("="*70)
    print("YOLOv3-Tiny Weights Downloader")
    print("="*70)
    print()
    
    # Check if already exists
    if os.path.exists(output_path) and os.path.getsize(output_path) > 1000000:
        print(f"✅ Weights already exists: {output_path}")
        print(f"   Size: {os.path.getsize(output_path) / 1024 / 1024:.2f} MB")
        return True
    
    # Try each URL
    for i, url in enumerate(urls, 1):
        print(f"Trying URL {i}: {url}")
        try:
            def reporthook(blocknum, blocksize, totalsize):
                readsofar = blocknum * blocksize
                if totalsize > 0:
                    percent = readsofar * 100 / totalsize
                    sys.stdout.write(f"\rProgress: {percent:.1f}% ({readsofar/1024/1024:.1f}/{totalsize/1024/1024:.1f} MB)")
                    sys.stdout.flush()
            
            urllib.request.urlretrieve(url, output_path, reporthook)
            print()
            
            # Verify size
            size = os.path.getsize(output_path)
            if size > 1000000:  # > 1 MB
                print(f"\n✅ Download successful!")
                print(f"   Size: {size / 1024 / 1024:.2f} MB")
                return True
            else:
                print(f"\n❌ Download failed: File too small ({size} bytes)")
                if os.path.exists(output_path):
                    os.remove(output_path)
        except Exception as e:
            print(f"\n❌ Download failed: {e}")
            if os.path.exists(output_path):
                os.remove(output_path)
    
    # If all failed
    print("\n" + "="*70)
    print("AUTOMATIC DOWNLOAD FAILED!")
    print("="*70)
    print()
    print("Please download manually:")
    print()
    print("1. Open browser")
    print("2. Visit: https://pjreddie.com/media/files/yolov3-tiny.weights")
    print("3. Save to: D:\\Github\\sc_python_camera_paddleocr\\V8_YOLO_OPENCV_DNN\\yolov3-tiny.weights")
    print()
    print("Or run this command in PowerShell:")
    print()
    print("curl -o yolov3-tiny.weights https://pjreddie.com/media/files/yolov3-tiny.weights")
    print()
    print("="*70)
    
    return False

if __name__ == "__main__":
    success = download_yolov3_tiny()
    sys.exit(0 if success else 1)
