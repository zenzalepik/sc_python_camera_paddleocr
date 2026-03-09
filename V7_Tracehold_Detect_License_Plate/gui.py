"""
ANPR Indonesian - License Plate Detection GUI
Based on ANPR-Indonesian project with KNN algorithm
Author: Generated for V7_Tracehold_Detect_License_Plate
"""

import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import sys

# Import detection modules
import DetectChars
import DetectPlates
import Preprocess
import PossiblePlate

# Constants
SCALAR_BLACK = (0.0, 0.0, 0.0)
SCALAR_WHITE = (255.0, 255.0, 255.0)
SCALAR_YELLOW = (0.0, 255.0, 255.0)
SCALAR_GREEN = (0.0, 255.0, 0.0)
SCALAR_RED = (0.0, 0.0, 255.0)
SCALAR_CYAN = (255.0, 223.0, 10.0)  # Cyan border color (#0ADFFF in BGR)
SCALAR_ORANGE = (0.0, 165.0, 255.0)  # Orange color for center box
BORDER_OPACITY = 0.5  # 50% opacity for border
CENTER_BOX_WIDTH_PERCENT = 0.5  # 50% of camera view width
CENTER_BOX_ASPECT_RATIO = 11.0/5.0  # Width:Height = 11:5 (horizontal rectangle)


class ANPRGUIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ANPR Indonesian - License Plate Detection")
        self.root.geometry("1400x1100")  # Increased window size for taller frames
        self.root.resizable(True, True)

        # Variables
        self.image_path = None
        self.original_image = None
        self.result_image = None
        self.detected_plate = ""
        self.list_of_possible_plates = []

        # Load KNN model
        self.knn_loaded = False
        self.load_knn_model()

        # Create GUI
        self.create_widgets()

    def load_knn_model(self):
        """Load KNN training data"""
        try:
            blnKNNTrainingSuccessful = DetectChars.loadKNNDataAndTrainKNN()
            if blnKNNTrainingSuccessful:
                self.knn_loaded = True
                print("KNN model loaded successfully!")
            else:
                self.knn_loaded = False
                messagebox.showerror("Error", "Failed to load KNN model!\nPlease ensure classifications.txt and flattened_images.txt exist.")
        except Exception as e:
            self.knn_loaded = False
            messagebox.showerror("Error", f"Failed to load KNN model:\n{str(e)}")

    def create_widgets(self):
        """Create GUI widgets"""
        # Create canvas and scrollbar for scrollable window
        main_canvas = tk.Canvas(self.root, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        
        # Scrollable frame
        self.scrollable_frame = tk.Frame(main_canvas)
        
        # Create window in canvas
        self.canvas_window = main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Update scrollregion and frame width when canvas resizes
        def _on_canvas_configure(event):
            main_canvas.itemconfig(self.canvas_window, width=event.width)
            main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        
        main_canvas.bind("<Configure>", _on_canvas_configure)
        
        # Update scrollregion when frame content changes
        def _on_frame_configure(event):
            main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        
        self.scrollable_frame.bind("<Configure>", _on_frame_configure)
        
        # Bind mouse wheel for scrolling
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Main frame inside scrollable frame
        main_frame = tk.Frame(self.scrollable_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Title
        title_label = tk.Label(main_frame, text="🚗 ANPR Indonesian - License Plate Detection",
                              font=("Arial", 18, "bold"))
        title_label.pack(pady=10)

        # Top image frame (Original and Result) - INCREASED HEIGHT
        top_image_frame = tk.Frame(main_frame)
        top_image_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        top_image_frame.pack_propagate(False)  # Prevent frame from shrinking to fit children
        top_image_frame.config(height=450)  # Set fixed height

        # Left side - Original image
        left_frame = tk.LabelFrame(top_image_frame, text="Original Image", font=("Arial", 12, "bold"))
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        left_frame.pack_propagate(False)  # Prevent frame from shrinking
        left_frame.config(height=450)  # Set fixed height

        self.original_label = tk.Label(left_frame, text="No image selected\nClick 'Select Image' to load",
                                       bg="#f0f0f0", relief=tk.SUNKEN, font=("Arial", 12))
        self.original_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Right side - Result image
        right_frame = tk.LabelFrame(top_image_frame, text="Detection Result", font=("Arial", 12, "bold"))
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        right_frame.pack_propagate(False)  # Prevent frame from shrinking
        right_frame.config(height=450)  # Set fixed height

        self.result_label = tk.Label(right_frame, text="Result will appear here\nafter detection",
                                     bg="#f0f0f0", relief=tk.SUNKEN, font=("Arial", 12))
        self.result_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Bottom image frame (Grayscale and Threshold) - INCREASED HEIGHT
        bottom_image_frame = tk.Frame(main_frame)
        bottom_image_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        bottom_image_frame.pack_propagate(False)  # Prevent frame from shrinking
        bottom_image_frame.config(height=450)  # Set fixed height

        # Left bottom - Grayscale image
        grayscale_frame = tk.LabelFrame(bottom_image_frame, text="Grayscale", font=("Arial", 12, "bold"))
        grayscale_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        grayscale_frame.pack_propagate(False)  # Prevent frame from shrinking
        grayscale_frame.config(height=450)  # Set fixed height

        self.grayscale_label = tk.Label(grayscale_frame, text="Grayscale will appear\nafter detection",
                                        bg="#f0f0f0", relief=tk.SUNKEN, font=("Arial", 10))
        self.grayscale_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Right bottom - Threshold image
        threshold_frame = tk.LabelFrame(bottom_image_frame, text="Threshold", font=("Arial", 12, "bold"))
        threshold_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        threshold_frame.pack_propagate(False)  # Prevent frame from shrinking
        threshold_frame.config(height=450)  # Set fixed height

        self.threshold_label = tk.Label(threshold_frame, text="Threshold will appear\nafter detection",
                                        bg="#f0f0f0", relief=tk.SUNKEN, font=("Arial", 10))
        self.threshold_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Button frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        # Select image button
        self.select_btn = tk.Button(button_frame, text="📁 Select Image",
                                   command=self.select_image,
                                   font=("Arial", 12, "bold"),
                                   bg="#4CAF50", fg="white",
                                   padx=20, pady=10)
        self.select_btn.pack(side=tk.LEFT, padx=5)

        # Detect plate button
        self.detect_btn = tk.Button(button_frame, text="🔍 Detect Plate",
                                   command=self.detect_plate,
                                   font=("Arial", 12, "bold"),
                                   bg="#2196F3", fg="white",
                                   padx=20, pady=10,
                                   state=tk.DISABLED)
        self.detect_btn.pack(side=tk.LEFT, padx=5)

        # Save result button
        self.save_btn = tk.Button(button_frame, text="💾 Save Result",
                                 command=self.save_result,
                                 font=("Arial", 12, "bold"),
                                 bg="#FF9800", fg="white",
                                 padx=20, pady=10,
                                 state=tk.DISABLED)
        self.save_btn.pack(side=tk.LEFT, padx=5)

        # Clear button
        self.clear_btn = tk.Button(button_frame, text="🗑️ Clear",
                                  command=self.clear_all,
                                  font=("Arial", 12, "bold"),
                                  bg="#f44336", fg="white",
                                  padx=20, pady=10)
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        # Status frame
        status_frame = tk.LabelFrame(main_frame, text="Status", font=("Arial", 12, "bold"))
        status_frame.pack(fill=tk.X, padx=10, pady=10)

        self.status_label = tk.Label(status_frame, text="Ready! Select an image to start...",
                                     font=("Arial", 11), anchor=tk.W, padx=10, pady=5)
        self.status_label.pack(fill=tk.X, padx=5, pady=5)

        # Result text frame
        result_text_frame = tk.LabelFrame(main_frame, text="Detected Plate Number", font=("Arial", 12, "bold"))
        result_text_frame.pack(fill=tk.X, padx=10, pady=10)

        self.result_text_widget = tk.Label(result_text_frame, text="No result yet",
                                           font=("Arial", 28, "bold"),
                                           fg="#2196F3", pady=15, bg="#e8e8e8",
                                           relief=tk.SUNKEN)
        self.result_text_widget.pack(fill=tk.X, padx=5, pady=5)

        # Info frame
        info_frame = tk.LabelFrame(main_frame, text="Information", font=("Arial", 10, "bold"))
        info_frame.pack(fill=tk.X, padx=10, pady=10)

        info_text = tk.Text(info_frame, height=4, font=("Consolas", 10), wrap=tk.WORD)
        info_text.pack(fill=tk.X, padx=5, pady=5)
        info_text.insert(tk.END, 
            "Method: Viola-Jones Algorithm + Contour Detection + KNN Classification\n"
            "Supports: Indonesian license plates (white on black / black on white)\n"
            "Tips: Ensure the plate is clearly visible and well-lit for best results.")
        info_text.config(state=tk.DISABLED)

    def select_image(self):
        """Select image from file dialog"""
        file_path = filedialog.askopenfilename(
            title="Select Vehicle Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")],
            initialdir="."
        )

        if file_path:
            self.image_path = file_path
            self.load_image(file_path)

    def load_image(self, path):
        """Load and display selected image"""
        try:
            # Load image with OpenCV
            img = cv2.imread(path)
            if img is None:
                messagebox.showerror("Error", "Could not read image!")
                return

            # Store original
            self.original_image = img.copy()

            # Draw center box on display copy
            img_with_center_box = img.copy()
            self._draw_center_box(img_with_center_box)

            # Display original image with center box
            self.display_image_on_label(self.original_label, img_with_center_box, "Original Image")

            # Reset result
            self.result_image = None
            self.result_label.config(image="", text="Result will appear here\nafter detection")
            self.grayscale_label.config(image="", text="Grayscale will appear\nafter detection")
            self.threshold_label.config(image="", text="Threshold will appear\nafter detection")
            self.result_text_widget.config(text="No result yet")
            self.detected_plate = ""

            # Enable detect button
            self.detect_btn.config(state=tk.NORMAL)
            self.save_btn.config(state=tk.DISABLED)

            # Update status
            self.update_status(f"Image loaded: {os.path.basename(path)} ({img.shape[1]}x{img.shape[0]})")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image:\n{str(e)}")

    def display_image_on_label(self, label, img, default_text=""):
        """Display OpenCV image on tkinter label"""
        try:
            # Convert BGR to RGB
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Get label size
            label_width = label.winfo_width()
            label_height = label.winfo_height()

            # If label size not available yet, use default
            if label_width <= 1 or label_height <= 1:
                label_width = 500
                label_height = 400

            # Resize image to fit label (maintain aspect ratio)
            height, width = img_rgb.shape[:2]
            scale = min(label_width / width, label_height / height) * 0.95
            new_width = int(width * scale)
            new_height = int(height * scale)

            if new_width > 0 and new_height > 0:
                img_resized = cv2.resize(img_rgb, (new_width, new_height))
            else:
                img_resized = img_rgb

            # Convert to PIL Image
            img_pil = Image.fromarray(img_resized)
            img_tk = ImageTk.PhotoImage(image=img_pil)

            # Store reference to prevent garbage collection
            label.img_tk = img_tk

            # Display
            label.config(image=img_tk, text="")

        except Exception as e:
            label.config(image="", text=f"Error displaying image:\n{str(e)}")

    def detect_plate(self):
        """Detect license plate in the image"""
        if self.original_image is None:
            messagebox.showwarning("Warning", "Please select an image first!")
            return

        if not self.knn_loaded:
            messagebox.showwarning("Warning", "KNN model not loaded!\nCannot perform detection.")
            return

        self.update_status("Processing... Detecting license plate...")
        self.root.update()

        try:
            # Make a copy for processing
            imgOriginalScene = self.original_image.copy()

            # Preprocess
            self.update_status("Preprocessing image...")
            self.root.update()
            imgGrayscale, imgThresh = Preprocess.preprocess(imgOriginalScene)

            # Detect plates
            self.update_status("Detecting plates...")
            self.root.update()
            listOfPossiblePlates = DetectPlates.detectPlatesInScene(imgOriginalScene)

            self.update_status(f"Found {len(listOfPossiblePlates)} potential plate(s)...")
            self.root.update()

            # Detect chars
            self.update_status("Recognizing characters...")
            self.root.update()
            listOfPossiblePlates = DetectChars.detectCharsInPlates(listOfPossiblePlates)

            # Display grayscale and threshold images
            self.display_grayscale_threshold(imgGrayscale, imgThresh)

            if len(listOfPossiblePlates) == 0:
                self.update_status("❌ No license plates detected!")
                messagebox.showwarning("No Plate Found", 
                    "No license plate was detected in this image.\n\n"
                    "Tips:\n"
                    "• Ensure the plate is clearly visible\n"
                    "• Check lighting conditions\n"
                    "• Try a different angle/image")
                return

            # Sort by string length (most chars first)
            listOfPossiblePlates.sort(key=lambda possiblePlate: len(possiblePlate.strChars), reverse=True)

            # Get the best result
            licPlate = listOfPossiblePlates[0]
            self.list_of_possible_plates = listOfPossiblePlates

            if len(licPlate.strChars) == 0:
                self.update_status("❌ No characters detected!")
                messagebox.showwarning("No Characters", 
                    "Plate detected but no characters could be recognized.")
                return

            # Draw rectangle around plate
            self.drawRedRectangleAroundPlate(imgOriginalScene, licPlate)

            # Draw center box on result image
            self._draw_center_box(imgOriginalScene)

            # Store result
            self.result_image = imgOriginalScene.copy()
            self.detected_plate = licPlate.strChars

            # Display result
            self.display_image_on_label(self.result_label, self.result_image, "Detection Result")

            # Update result text
            self.result_text_widget.config(text=f"Plate: {self.detected_plate}")

            # Update status
            self.update_status(f"✅ Detection successful! Plate: {self.detected_plate}")

            # Enable save button
            self.save_btn.config(state=tk.NORMAL)

            # Show additional info
            self.show_plate_details(licPlate)

        except Exception as e:
            self.update_status(f"❌ Error: {str(e)}")
            messagebox.showerror("Error", f"Detection failed:\n{str(e)}")
            import traceback
            traceback.print_exc()

    def display_grayscale_threshold(self, imgGrayscale, imgThresh):
        """Display grayscale and threshold images in bottom panels"""
        try:
            # Display grayscale image
            if imgGrayscale is not None:
                # Convert to RGB for display
                img_gray_rgb = cv2.cvtColor(imgGrayscale, cv2.COLOR_GRAY2RGB)
                self.display_image_on_label(self.grayscale_label, img_gray_rgb, "Grayscale")
            
            # Display threshold image
            if imgThresh is not None:
                # Convert to RGB for display
                img_thresh_rgb = cv2.cvtColor(imgThresh, cv2.COLOR_GRAY2RGB)
                self.display_image_on_label(self.threshold_label, img_thresh_rgb, "Threshold")
        except Exception as e:
            pass

    def drawRedRectangleAroundPlate(self, imgOriginalScene, licPlate):
        """Draw dashed cyan rectangle with 20% opacity around detected plate"""
        if licPlate is None or licPlate.rrLocationOfPlateInScene is None:
            return
        try:
            p2fRectPoints = cv2.boxPoints(licPlate.rrLocationOfPlateInScene)
            pts = np.int32(p2fRectPoints)
            
            # Draw dashed lines with 20% opacity
            self._draw_dashed_line(imgOriginalScene, tuple(pts[0]), tuple(pts[1]), SCALAR_CYAN, 1, BORDER_OPACITY)
            self._draw_dashed_line(imgOriginalScene, tuple(pts[1]), tuple(pts[2]), SCALAR_CYAN, 1, BORDER_OPACITY)
            self._draw_dashed_line(imgOriginalScene, tuple(pts[2]), tuple(pts[3]), SCALAR_CYAN, 1, BORDER_OPACITY)
            self._draw_dashed_line(imgOriginalScene, tuple(pts[3]), tuple(pts[0]), SCALAR_CYAN, 1, BORDER_OPACITY)
            
            # Add label with plate dimensions
            self._draw_plate_label(imgOriginalScene, licPlate)
        except Exception as e:
            pass
    
    def _draw_dashed_line(self, img, pt1, pt2, color, thickness, opacity=0.2, dash_length=10):
        """Draw a dashed line between two points with opacity"""
        x1, y1 = pt1
        x2, y2 = pt2
        
        # Calculate line length
        length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
        if length == 0:
            return
        
        # Calculate step size
        dx = (x2 - x1) / length
        dy = (y2 - y1) / length
        
        # Create overlay for transparency
        overlay = img.copy()
        
        # Draw dashed line
        current_pos = 0
        while current_pos < length:
            dash_end = min(current_pos + dash_length, length)
            
            # Calculate start and end points for this dash
            x_start = int(x1 + dx * current_pos)
            y_start = int(y1 + dy * current_pos)
            x_end = int(x1 + dx * dash_end)
            y_end = int(y1 + dy * dash_end)
            
            cv2.line(overlay, (x_start, y_start), (x_end, y_end), color, thickness)
            
            # Skip gap length
            current_pos += dash_length + dash_length  # dash + gap
        
        # Blend overlay with original image
        cv2.addWeighted(overlay, opacity, img, 1 - opacity, 0, img)
    
    def _draw_center_box(self, img):
        """Draw orange center box with 50% width and 11:5 aspect ratio (horizontal)"""
        img_height, img_width = img.shape[:2]
        
        # Calculate box dimensions
        box_width = int(img_width * CENTER_BOX_WIDTH_PERCENT)  # 50% of width
        box_height = int(box_width * 5.0 / 11.0)  # 11:5 ratio (height = width × 5/11)
        
        # Calculate center position
        center_x = img_width // 2
        center_y = img_height // 2
        
        # Calculate top-left and bottom-right corners
        x1 = center_x - box_width // 2
        y1 = center_y - box_height // 2
        x2 = center_x + box_width // 2
        y2 = center_y + box_height // 2
        
        # Draw orange rectangle (2px thickness)
        cv2.rectangle(img, (x1, y1), (x2, y2), SCALAR_ORANGE, 2)
        
        # Calculate percentages
        width_percent = (box_width / img_width) * 100
        height_percent = (box_height / img_height) * 100
        
        # Create label text
        label_text = f"{width_percent:.1f}% ({box_width}px) x {height_percent:.1f}% ({box_height}px)"
        
        # Position label above the box
        label_y = y1 - 5  # 5px above the box
        
        # Ensure label is within image bounds
        if label_y < 20:
            label_y = y2 + 5  # Put below if not enough space above
        
        # Draw label background (semi-transparent)
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.25  # Half size (was 0.5)
        thickness = 1
        (text_width, text_height), baseline = cv2.getTextSize(label_text, font, font_scale, thickness)
        
        # Create overlay for label background
        overlay = img.copy()
        cv2.rectangle(overlay, 
                     (x1, label_y - text_height - 5), 
                     (x1 + text_width + 5, label_y + baseline + 5), 
                     (0, 0, 0), -1)
        
        # Blend overlay
        cv2.addWeighted(overlay, 0.6, img, 0.4, 0, img)
        
        # Draw label text (white)
        cv2.putText(img, label_text, (x1, label_y), 
                   font, font_scale, (255, 255, 255), thickness)
    
    def _draw_plate_label(self, img, licPlate):
        """Draw label with plate dimensions at bottom-left corner"""
        if licPlate.rrLocationOfPlateInScene is None:
            return
        
        # Get plate dimensions
        (center, size, angle) = licPlate.rrLocationOfPlateInScene
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
        
        # Draw label background (semi-transparent)
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.25  # Half size (was 0.5)
        thickness = 1
        (text_width, text_height), baseline = cv2.getTextSize(label_text, font, font_scale, thickness)
        
        # Create overlay for label background
        overlay = img.copy()
        cv2.rectangle(overlay, 
                     (label_x - 5, label_y - text_height - 5), 
                     (label_x + text_width + 5, label_y + baseline + 5), 
                     (0, 0, 0), -1)
        
        # Blend overlay
        cv2.addWeighted(overlay, 0.6, img, 0.4, 0, img)
        
        # Draw label text (white)
        cv2.putText(img, label_text, (label_x, label_y), 
                   font, font_scale, (255, 255, 255), thickness)

    def show_plate_details(self, licPlate):
        """Show details about detected plate"""
        details = f"Plate Number: {licPlate.strChars}\n"
        if licPlate.rrLocationOfPlateInScene is not None:
            (center, size, angle) = licPlate.rrLocationOfPlateInScene
            details += f"Location: Center={center}, Size={size}, Angle={angle:.2f}°"
        
        # Also show plate crop if available
        if hasattr(licPlate, 'imgPlate') and licPlate.imgPlate is not None:
            details += f"\nPlate image size: {licPlate.imgPlate.shape}"
        
        print(details)

    def save_result(self):
        """Save result image"""
        if self.result_image is None:
            messagebox.showwarning("Warning", "No result to save!")
            return

        file_path = filedialog.asksaveasfilename(
            title="Save Result",
            defaultextension=".jpg",
            filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png")],
            initialfile=f"result_{self.detected_plate}.jpg" if self.detected_plate else "result.jpg"
        )

        if file_path:
            try:
                cv2.imwrite(file_path, self.result_image)
                self.update_status(f"✅ Result saved to: {file_path}")
                messagebox.showinfo("Success", f"Result saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save:\n{str(e)}")

    def clear_all(self):
        """Clear all and reset"""
        self.image_path = None
        self.original_image = None
        self.result_image = None
        self.detected_plate = ""
        self.list_of_possible_plates = []

        self.original_label.config(image="", text="No image selected\nClick 'Select Image' to load")
        self.result_label.config(image="", text="Result will appear here\nafter detection")
        self.grayscale_label.config(image="", text="Grayscale will appear\nafter detection")
        self.threshold_label.config(image="", text="Threshold will appear\nafter detection")
        self.result_text_widget.config(text="No result yet")

        self.detect_btn.config(state=tk.DISABLED)
        self.save_btn.config(state=tk.DISABLED)

        self.update_status("Ready! Select an image to start...")

    def update_status(self, message):
        """Update status text"""
        self.status_label.config(text=message)
        self.root.update_idletasks()


def main():
    """Main entry point"""
    root = tk.Tk()
    app = ANPRGUIApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
