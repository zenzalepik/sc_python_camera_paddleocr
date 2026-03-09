# Quick Start Guide - ANPR Indonesian License Plate Detection

## Project Overview
This project implements an Automatic Number Plate Recognition (ANPR) system for Indonesian license plates with a user-friendly GUI interface. The system can detect license plate areas and recognize the characters using the K-Nearest Neighbors (KNN) algorithm.

## What's New in V7
✅ **GUI Interface** - Easy-to-use graphical interface (no command line needed)
✅ **Plate Area Detection** - Automatically detects and highlights license plate location
✅ **Character Recognition** - Recognizes plate numbers using KNN algorithm
✅ **Image File Support** - Select images from local storage
✅ **Save Results** - Save detection results with annotated images

## Installation

### Step 1: Install Dependencies
Open Command Prompt in the project directory and run:
```bash
pip install -r requirements.txt
```

### Step 2: Verify Installation
Ensure the following files exist:
- `classifications.txt` (KNN training data)
- `flattened_images.txt` (KNN training images)
- `calibrated_value.txt` (Calibration parameters)
- `cascade.xml` (Cascade classifier)

## Usage

### Method 1: Using Batch File (Easiest)
Double-click `Run GUI.bat` to start the application.

### Method 2: Using Command Line
```bash
python gui.py
```

### Method 3: Test Detection (Command Line)
```bash
python test_detection.py test_images\H6756QI.jpg
```

## GUI Workflow

1. **Launch the Application**
   - Run `Run GUI.bat` or `python gui.py`
   - Wait for KNN model to load

2. **Select Image**
   - Click "📁 Select Image" button
   - Browse and select a vehicle image from your local files
   - Supported formats: JPG, JPEG, PNG, BMP

3. **Detect Plate**
   - Click "🔍 Detect Plate" button
   - Wait for processing (may take a few seconds)
   - View the detected plate number

4. **View Results**
   - Left panel: Original image
   - Right panel: Result with detected plate highlighted
   - Bottom: Detected plate number displayed

5. **Save Result** (Optional)
   - Click "💾 Save Result" button
   - Choose location and filename
   - Result image includes red rectangle around detected plate

6. **Clear & Reset**
   - Click "🗑️ Clear" button to reset the application

## Testing

### Test Images
Sample test images are included in the `test_images` folder:
- `H6756QI.jpg`
- `AA4795BE.jpg`
- `BH2618MA.jpg`
- And 30+ more images

### Run Tests
```bash
# Test single image
python test_detection.py test_images\H6756QI.jpg

# Test multiple images
python test_detection.py test_images\AA4795BE.jpg
```

## Detection Capabilities

### ✅ What It Can Detect
- Indonesian license plates (standard format)
- White text on black background
- Black text on white background
- Rectangular plates
- Multiple plates in one image (shows best match)

### 📊 Detection Results
The system provides:
1. **Plate Location** - Red rectangle around detected plate
2. **Plate Number** - Text recognition result
3. **Confidence** - Based on KNN classification

## Tips for Best Results

### Image Quality
✅ Use clear, well-lit images
✅ Ensure the plate is fully visible
✅ Frontal or slightly angled shots work best
✅ Higher resolution images provide better results

### Avoid
❌ Blurry or low-quality images
❌ Extreme angles (>45 degrees)
❌ Plates partially obscured
❌ Very dark or overexposed images

## Troubleshooting

### "KNN model not loaded"
**Problem:** KNN training data files missing
**Solution:** Ensure these files exist in the project directory:
- `classifications.txt`
- `flattened_images.txt`

### "No license plate detected"
**Problem:** Plate not found in image
**Solutions:**
- Try a different image with better lighting
- Ensure the plate is clearly visible
- Check that the vehicle is not too far from the camera
- Use images where the plate is facing the camera

### "No characters detected"
**Problem:** Plate found but characters not recognized
**Solutions:**
- Try an image with higher resolution
- Ensure the plate is not at an extreme angle
- Check that the text is clearly visible

### GUI doesn't open
**Problem:** Tkinter or PIL not installed
**Solution:** 
```bash
pip install Pillow
pip install opencv-python
```

## Technical Details

### Detection Pipeline
1. **Preprocessing**
   - Convert to grayscale
   - Maximize contrast (top-hat/black-hat transforms)
   - Gaussian blur
   - Adaptive thresholding

2. **Plate Detection**
   - Find contours
   - Filter by size and aspect ratio
   - Group matching contours
   - Extract and rotate plate region

3. **Character Recognition**
   - Segment characters
   - Resize to standard size (20x30)
   - Classify using KNN (K=1)
   - Sort left-to-right
   - Combine into plate string

### Performance
- Detection time: ~1-3 seconds (depends on image size)
- Accuracy: Varies based on image quality
- Best results: Clear, frontal plate images

## Project Structure

```
V7_Tracehold_Detect_License_Plate/
├── gui.py                      # Main GUI application
├── test_detection.py           # Command-line test script
├── Constants.py                # Color constants and config
├── DetectPlates.py             # Plate detection module
├── DetectChars.py              # Character detection & recognition
├── Preprocess.py               # Image preprocessing
├── PossiblePlate.py            # Plate data structure
├── PossibleChar.py             # Character data structure
├── imutils.py                  # Image utilities
├── classifications.txt         # KNN training data (labels)
├── flattened_images.txt        # KNN training data (images)
├── calibrated_value.txt        # Calibration parameters
├── cascade.xml                 # Cascade classifier
├── requirements.txt            # Python dependencies
├── Run GUI.bat                 # Windows batch launcher
├── README.md                   # Full documentation
├── QUICK_START.md              # This file
└── test_images/                # Sample test images
```

## Comparison with Other Versions

| Feature | V7 (This Version) | ALPR_Indonesia | ANPR-Indonesian CLI |
|---------|------------------|----------------|---------------------|
| Interface | Tkinter GUI | Tkinter GUI | Command Line |
| Detection Method | Contour + KNN | Deep Learning (CNN) | Contour + KNN |
| Plate Detection | ✅ Yes | ✅ Yes | ✅ Yes |
| Character Recognition | ✅ KNN | ✅ CNN | ✅ KNN |
| Image File Input | ✅ Yes | ✅ Yes | ✅ Yes |
| Live Camera | ❌ No | ❌ No | ✅ Yes |
| Video File | ❌ No | ❌ No | ✅ Yes |
| Plate Area Highlight | ✅ Yes | ✅ Yes | ✅ Yes |

## License
Based on the original ANPR-Indonesian project. See LICENSE file.

## Support
For issues or questions, refer to the original ANPR-Indonesian repository or check the README.md file.

---
**Created:** 2026-03-09
**Version:** V7_Tracehold_Detect_License_Plate
