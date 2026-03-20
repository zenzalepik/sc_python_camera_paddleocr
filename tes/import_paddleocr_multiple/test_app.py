"""
Test script untuk menjalankan app.py dengan error handling lengkap
"""

import sys
import os
import traceback

# Add path
sys.path.insert(0, os.path.dirname(__file__))

print("\n" + "="*70)
print("Testing app.py dengan error handling")
print("="*70 + "\n")

try:
    # Import app
    import app
    
    print("[OK] App imported successfully")
    print("[INFO] Running app...")
    
    # Run app
    app.main()
    
    print("\n[OK] App closed normally")
    
except Exception as e:
    print(f"\n[ERROR] App crashed!")
    print(f"[ERROR] Type: {type(e).__name__}")
    print(f"[ERROR] Message: {e}")
    print(f"\n[TRACEBACK]:")
    print(traceback.format_exc())
    
    # Save error log
    with open('error_log.txt', 'w') as f:
        f.write(f"Error: {e}\n\n")
        f.write(traceback.format_exc())
    
    print(f"\n[INFO] Error log saved to: error_log.txt")

print("\n" + "="*70)
print("Test complete")
print("="*70 + "\n")
