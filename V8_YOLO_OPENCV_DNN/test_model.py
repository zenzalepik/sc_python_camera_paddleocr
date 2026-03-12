"""
Test YOLO Model Loading
"""
import cv2
import os

print("="*70)
print("TEST YOLO MODEL LOADING")
print("="*70)

# Check model file
model_path = os.path.join(os.path.dirname(__file__), 'yolov8n.onnx')

print(f"\nChecking model file...")
print(f"Path: {model_path}")

if os.path.exists(model_path):
    print(f"✅ Model file EXISTS")
    print(f"   Size: {os.path.getsize(model_path) / 1024 / 1024:.2f} MB")
else:
    print(f"❌ Model file NOT FOUND!")
    print(f"   Please download yolov8n.onnx first!")
    exit(1)

# Try load with OpenCV DNN
print(f"\nLoading model with OpenCV DNN...")
print(f"OpenCV version: {cv2.__version__}")

try:
    net = cv2.dnn.readNetFromONNX(model_path)
    print(f"✅ Model loaded SUCCESSFULLY!")
    
    # Test inference
    print(f"\nTesting inference...")
    test_frame = cv2.imread('test_image.jpg') if os.path.exists('test_image.jpg') else cv2.imread('camera_test.png')
    
    if test_frame is None:
        print(f"⚠️  No test image found, creating dummy frame...")
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    blob = cv2.dnn.blobFromImage(test_frame, 1/255.0, (416, 416))
    net.setInput(blob)
    outputs = net.forward()
    
    print(f"✅ Inference SUCCESSFUL!")
    print(f"   Output shape: {outputs.shape}")
    print(f"   Inference time: N/A (single run)")
    
except Exception as e:
    print(f"❌ Error loading model: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
