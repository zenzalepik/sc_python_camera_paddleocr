"""
Download YOLOv3-Tiny weights dengan requests
"""
import requests
import os
import sys

def download_file(url, filename):
    """Download file dengan progress bar"""
    print(f"Downloading from: {url}")
    print(f"Saving to: {filename}")
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        sys.stdout.write(f'\rProgress: {percent:.1f}% ({downloaded/1024/1024:.1f}/{total_size/1024/1024:.1f} MB)')
                        sys.stdout.flush()
        
        print()
        print(f"✅ Download complete!")
        print(f"   Size: {os.path.getsize(filename) / 1024 / 1024:.2f} MB")
        return True
        
    except Exception as e:
        print(f"\n❌ Download failed: {e}")
        return False

if __name__ == "__main__":
    output_path = os.path.join(os.path.dirname(__file__), 'yolov3-tiny.weights')
    
    # URLs to try
    urls = [
        "https://pjreddie.com/media/files/yolov3-tiny.weights",
        "https://raw.githubusercontent.com/AlexeyAB/darknet/master/build/darknet/x64/data/yolov3-tiny.weights",
    ]
    
    print("="*70)
    print("YOLOv3-Tiny Weights Downloader")
    print("="*70)
    print()
    
    # Check if already exists
    if os.path.exists(output_path) and os.path.getsize(output_path) > 1000000:
        print(f"✅ File already exists: {output_path}")
        print(f"   Size: {os.path.getsize(output_path) / 1024 / 1024:.2f} MB")
        sys.exit(0)
    
    # Try each URL
    for i, url in enumerate(urls, 1):
        print(f"\nTrying URL {i}:")
        success = download_file(url, output_path)
        if success and os.path.getsize(output_path) > 1000000:
            print("\n✅ SUCCESS!")
            sys.exit(0)
        elif os.path.exists(output_path):
            os.remove(output_path)
    
    print("\n❌ All downloads failed!")
    sys.exit(1)
