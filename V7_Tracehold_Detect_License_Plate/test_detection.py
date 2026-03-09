"""
Test script for ANPR detection without GUI
"""

import cv2
import numpy as np
import DetectChars
import DetectPlates
import Preprocess

def test_detection(image_path):
    """Test plate detection on a single image"""
    print(f"\nTesting detection on: {image_path}")
    print("-" * 60)
    
    # Load image
    imgOriginalScene = cv2.imread(image_path)
    if imgOriginalScene is None:
        print(f"Error: Could not read image {image_path}")
        return None
    
    print(f"Image loaded: {imgOriginalScene.shape[1]}x{imgOriginalScene.shape[0]}")
    
    # Load KNN model
    print("Loading KNN model...")
    blnKNNTrainingSuccessful = DetectChars.loadKNNDataAndTrainKNN()
    if not blnKNNTrainingSuccessful:
        print("Error: KNN training failed!")
        return None
    print("KNN model loaded successfully!")
    
    # Preprocess
    print("Preprocessing image...")
    imgGrayscale, imgThresh = Preprocess.preprocess(imgOriginalScene)
    
    # Detect plates
    print("Detecting plates...")
    listOfPossiblePlates = DetectPlates.detectPlatesInScene(imgOriginalScene)
    print(f"Found {len(listOfPossiblePlates)} potential plate(s)")
    
    # Detect chars
    print("Recognizing characters...")
    listOfPossiblePlates = DetectChars.detectCharsInPlates(listOfPossiblePlates)
    
    if len(listOfPossiblePlates) == 0:
        print("[WARNING] No license plates detected!")
        return None
    
    # Sort by string length
    listOfPossiblePlates.sort(key=lambda x: len(x.strChars), reverse=True)
    
    # Show results
    print("\n" + "=" * 60)
    print("DETECTION RESULTS:")
    print("=" * 60)
    
    for i, plate in enumerate(listOfPossiblePlates[:5], 1):
        if plate.strChars:
            print(f"{i}. Plate: {plate.strChars}")
        else:
            print(f"{i}. Plate: (no chars detected)")
    
    # Get best result
    best_plate = listOfPossiblePlates[0]
    
    if best_plate.strChars:
        print(f"\n[SUCCESS] Detection successful! Plate: {best_plate.strChars}")
        
        # Get plate dimensions
        (center, size, angle) = best_plate.rrLocationOfPlateInScene
        width, height = size
        print(f"Plate dimensions: {int(width)}x{int(height)} pixels")
        
        # Draw dashed cyan rectangle with 50% opacity (#0ADFFF, 1px thickness)
        SCALAR_CYAN = (255, 223, 10)  # BGR for #0ADFFF
        BORDER_OPACITY = 0.5  # 50% opacity
        
        def draw_dashed_line(img, pt1, pt2, color, thickness, opacity=0.2, dash_length=10):
            """Draw a dashed line between two points with opacity"""
            x1, y1 = pt1
            x2, y2 = pt2
            length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            if length == 0:
                return
            dx = (x2 - x1) / length
            dy = (y2 - y1) / length
            
            # Create overlay for transparency
            overlay = img.copy()
            
            current_pos = 0
            while current_pos < length:
                dash_end = min(current_pos + dash_length, length)
                x_start = int(x1 + dx * current_pos)
                y_start = int(y1 + dy * current_pos)
                x_end = int(x1 + dx * dash_end)
                y_end = int(y1 + dy * dash_end)
                cv2.line(overlay, (x_start, y_start), (x_end, y_end), color, thickness)
                current_pos += dash_length + dash_length
            
            # Blend overlay with original image
            cv2.addWeighted(overlay, opacity, img, 1 - opacity, 0, img)
        
        def draw_plate_label(img, plate):
            """Draw label with plate dimensions at bottom-left corner"""
            if plate.rrLocationOfPlateInScene is None:
                return
            
            (center, size, angle) = plate.rrLocationOfPlateInScene
            width, height = size
            
            # Get image dimensions
            img_height, img_width = img.shape[:2]
            
            # Calculate width percentage relative to camera view
            width_percentage = (width / img_width) * 100
            
            # Position at bottom-left corner with padding
            label_x = 10  # Left padding
            label_y = img_height - 10  # Bottom padding
            
            # Create label text with width percentage
            label_text = f"{width_percentage:.1f}% w={int(width)}px h={int(height)}px"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            thickness = 1
            (text_width, text_height), baseline = cv2.getTextSize(label_text, font, font_scale, thickness)
            
            # Draw label background (semi-transparent)
            overlay = img.copy()
            cv2.rectangle(overlay, 
                         (label_x - 5, label_y - text_height - 5), 
                         (label_x + text_width + 5, label_y + baseline + 5), 
                         (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.6, img, 0.4, 0, img)
            
            # Draw label text (white)
            cv2.putText(img, label_text, (label_x, label_y), 
                       font, font_scale, (255, 255, 255), thickness)
        
        if best_plate.rrLocationOfPlateInScene is not None:
            p2fRectPoints = cv2.boxPoints(best_plate.rrLocationOfPlateInScene)
            pts = np.int32(p2fRectPoints)
            draw_dashed_line(imgOriginalScene, tuple(pts[0]), tuple(pts[1]), SCALAR_CYAN, 1, BORDER_OPACITY)
            draw_dashed_line(imgOriginalScene, tuple(pts[1]), tuple(pts[2]), SCALAR_CYAN, 1, BORDER_OPACITY)
            draw_dashed_line(imgOriginalScene, tuple(pts[2]), tuple(pts[3]), SCALAR_CYAN, 1, BORDER_OPACITY)
            draw_dashed_line(imgOriginalScene, tuple(pts[3]), tuple(pts[0]), SCALAR_CYAN, 1, BORDER_OPACITY)
            draw_plate_label(imgOriginalScene, best_plate)
        
        # Save result
        result_path = f"test_result_{best_plate.strChars}.jpg"
        cv2.imwrite(result_path, imgOriginalScene)
        print(f"Result saved to: {result_path}")
    else:
        print("\n[ERROR] No characters detected in the best plate")
    
    return best_plate

if __name__ == "__main__":
    import sys
    
    # Test with default image or command line argument
    if len(sys.argv) > 1:
        test_image = sys.argv[1]
    else:
        test_image = "test_images/H6756QI.jpg"
    
    test_detection(test_image)
