"""
Download YOLOv8n ONNX model
Script ini akan download model YOLOv8n.onnx untuk OpenCV DNN
"""

import os
import sys

def download_model():
    """Download YOLOv8n ONNX model."""
    
    # Use correct URL from Ultralytics GitHub releases
    model_url = "https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8n.onnx"
    model_path = os.path.join(os.path.dirname(__file__), 'yolov8n.onnx')
    
    print("="*70)
    print("YOLOv8n ONNX Model Downloader")
    print("="*70)
    print()
    
    # Check if model already exists
    if os.path.exists(model_path):
        print(f"✅ Model already exists at: {model_path}")
        print(f"   Size: {os.path.getsize(model_path) / 1024 / 1024:.2f} MB")
        return True
    
    print(f"Downloading YOLOv8n ONNX model...")
    print(f"URL: {model_url}")
    print(f"Save to: {model_path}")
    print()
    
    try:
        import urllib.request
        
        # Download with progress
        def reporthook(blocknum, blocksize, totalsize):
            readsofar = blocknum * blocksize
            if totalsize > 0:
                percent = readsofar * 100 / totalsize
                sys.stdout.write(f"\rProgress: {percent:.1f}%")
                sys.stdout.flush()
        
        urllib.request.urlretrieve(model_url, model_path, reporthook)
        
        print("\n")
        print(f"✅ Download successful!")
        print(f"   Model saved to: {model_path}")
        print(f"   Size: {os.path.getsize(model_path) / 1024 / 1024:.2f} MB")
        print()
        print("Now you can run: python main.py")
        print("="*70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Download failed: {e}")
        print()
        print("Manual download instructions:")
        print(f"1. Open browser and go to: {model_url}")
        print(f"2. Download yolov8n.onnx")
        print(f"3. Move file to: {model_path}")
        print("="*70)
        return False


if __name__ == "__main__":
    success = download_model()
    sys.exit(0 if success else 1)
