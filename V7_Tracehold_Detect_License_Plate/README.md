# V7_Tracehold_Detect_License_Plate

ANPR (Automatic Number Plate Recognition) for Indonesian license plates with GUI interface.

## Features

- ✅ **GUI-based interface** - Easy to use, no command line needed
- ✅ **Select image from local file** - Browse and select vehicle images
- ✅ **License plate detection** - Detects plate location using contour analysis
- ✅ **Character recognition** - Uses KNN algorithm for character classification
- ✅ **Save results** - Save detection results with annotated images

## Method

This system uses:
1. **Viola-Jones Algorithm** - For initial vehicle/plate detection
2. **Contour Detection** - For precise plate location
3. **KNN (K-Nearest Neighbors)** - For character recognition

## Prerequisites

- Python 3.6+
- OpenCV 4.1.1.26
- NumPy 1.17.3
- Pillow

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure the following trained model files are present in the project directory:
   - `classifications.txt`
   - `flattened_images.txt`
   - `calibrated_value.txt`
   - `cascade.xml`

## Usage

### GUI Mode (Recommended)

Run the GUI application:
```bash
python gui.py
```

**Steps:**
1. Click **"Select Image"** button
2. Choose a vehicle image from your local files
3. Click **"Detect Plate"** button
4. View the detected plate number and result
5. Click **"Save Result"** to save the annotated image

### Supported Image Formats

- JPG/JPEG
- PNG
- BMP

## Project Structure

```
V7_Tracehold_Detect_License_Plate/
├── gui.py                      # Main GUI application
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
└── README.md                   # This file
```

## How It Works

### 1. Preprocessing
- Convert to grayscale
- Extract value channel
- Maximize contrast using top-hat and black-hat transforms
- Apply Gaussian blur
- Adaptive thresholding

### 2. Plate Detection
- Find contours in thresholded image
- Filter contours based on size and aspect ratio
- Group matching contours
- Extract and rotate plate region

### 3. Character Recognition
- Segment characters from plate image
- Resize characters to standard size
- Classify using KNN algorithm
- Sort characters left-to-right
- Combine into plate number string

## Tips for Best Results

1. **Image Quality**: Use clear, well-lit images
2. **Plate Visibility**: Ensure the license plate is fully visible
3. **Angle**: Frontal or slightly angled shots work best
4. **Resolution**: Higher resolution images provide better results
5. **Contrast**: Plates with good contrast against background work better

## Troubleshooting

### "KNN model not loaded" error
- Ensure `classifications.txt` and `flattened_images.txt` exist in the project directory
- Check file permissions

### "No license plate detected"
- Try a different image with better lighting
- Ensure the plate is clearly visible
- Check that the vehicle is not too far from the camera

### "No characters detected"
- Plate may be too small or blurry
- Try an image with higher resolution
- Ensure the plate is not at an extreme angle

## Comparison with Other Versions

| Feature | This Version (V7) | ALPR_Indonesia (GUI) | ANPR-Indonesian (CLI) |
|---------|------------------|---------------------|----------------------|
| Interface | Tkinter GUI | Tkinter GUI | Command Line |
| Detection Method | Contour + KNN | Deep Learning (CNN) | Contour + KNN |
| Plate Detection | ✅ Yes | ✅ Yes | ✅ Yes |
| Character Recognition | ✅ KNN | ✅ CNN | ✅ KNN |
| Live Camera | ❌ No | ❌ No | ✅ Yes |
| Image File | ✅ Yes | ✅ Yes | ✅ Yes |
| Video File | ❌ No | ❌ No | ✅ Yes |

## Known Limitations

- Only supports Indonesian license plate formats
- Works best with standard rectangular plates
- May struggle with extreme angles or poor lighting
- Not optimized for real-time video processing

## Credits

Based on the **ANPR-Indonesian** project:
- Original method: Viola-Jones + Contour Detection + KNN
- Training data: Indonesian license plate characters (0-9, A-Z)

## License

See original project LICENSE file.

## Author

Generated for V7_Tracehold_Detect_License_Plate project.

## Support

For issues or questions, please refer to the original ANPR-Indonesian repository.
