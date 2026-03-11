"""
PaddleOCR Mobile - Multiple Image Input Support
Aplikasi desktop upload multiple gambar dengan PaddleOCR v5 Mobile untuk deteksi teks otomatis

Fitur:
- GUI sederhana dengan Tkinter
- File picker untuk pilih multiple gambar sekaligus
- Preview gambar per item
- Deteksi teks otomatis dengan PaddleOCR v5 Mobile untuk semua gambar
- Tampilkan hasil teks dengan confidence score per gambar
- Export hasil ke TXT/JSON
- Copy hasil ke clipboard
- Grouping hasil berdasarkan gambar
"""

import os
import sys
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import threading
import time
from datetime import datetime

import cv2
import numpy as np
from PIL import Image, ImageTk
from dotenv import load_dotenv

# Import PaddleOCR
try:
    from paddleocr import PaddleOCR
    # Disable model source check
    os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'
except ImportError:
    print("PaddleOCR tidak terinstall!")
    print("Install dengan: pip install paddlepaddle paddleocr")
    sys.exit(1)

# Load konfigurasi
load_dotenv()


class PaddleOCRMultipleInputGUI:
    """PaddleOCR Mobile - Multiple Image Input GUI Application."""

    def __init__(self, root):
        """Initialize Multiple Input GUI App."""
        self.root = root
        self.root.title("PaddleOCR Mobile - Multiple Image Detection")
        self.root.geometry("1400x750")
        self.root.minsize(1200, 650)

        # OCR Settings
        self.lang = os.getenv('OCR_LANG', 'en')
        self.conf_threshold = float(os.getenv('CONF_THRESHOLD', '0.5'))
        self.delete_space = os.getenv('DELETE_SPACE', 'False') == 'True'
        self.group_by_line = os.getenv('GROUP_BY_LINE', 'False') == 'True'
        self.line_tolerance = int(os.getenv('LINE_TOLERANCE', '10'))
        self.hide_popup_unknown_exception = os.getenv('HIDE_POPUP_UNKNOWN_EXCEPTION', 'False') == 'True'
        self.output_dir = os.getenv('OUTPUT_DIR', 'output')

        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)

        # State variables
        self.images = []  # List of {path, image, photo, result}
        self.current_index = -1
        self.ocr = None
        
        # Initialize PaddleOCR
        self.init_ocr()

        # Build UI
        self.build_ui()

    def init_ocr(self):
        """Initialize PaddleOCR engine."""
        print("Initializing PaddleOCR v5 Mobile...")
        try:
            # PaddleOCR v5 new API - use mobile models
            self.ocr = PaddleOCR(
                lang=self.lang,
                text_detection_model_name='PP-OCRv5_mobile_det',
                text_recognition_model_name='PP-OCRv5_mobile_rec',
            )
            print("[OK] PaddleOCR v5 Mobile initialized!")
            print(f"    - Language: {self.lang.upper()}")
            print(f"    - Delete Space: {'ON' if self.delete_space else 'OFF'}")
            print(f"    - Group by Line: {'ON' if self.group_by_line else 'OFF'}")
            if self.group_by_line:
                print(f"    - Line Tolerance: {self.line_tolerance}px")
        except Exception as e:
            print(f"[ERROR] Error initializing PaddleOCR: {e}")
            messagebox.showerror("Error", f"Failed to initialize PaddleOCR:\n{e}")

    def build_ui(self):
        """Build user interface."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="PaddleOCR Mobile - Multiple Image Detection",
            font=('Helvetica', 16, 'bold')
        )
        title_label.grid(row=0, column=0, pady=(0, 10))

        # Create paned window (3 sections)
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Left panel (Image List)
        left_frame = ttk.Frame(paned, padding="5", width=250)
        paned.add(left_frame, weight=1)

        # Image list label
        list_label = ttk.Label(left_frame, text="Image List", font=('Helvetica', 12, 'bold'))
        list_label.pack(anchor=tk.W)

        # Image list with scrollbar
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.image_listbox = tk.Listbox(
            list_frame,
            font=('Consolas', 9),
            selectmode=tk.SINGLE,
            activestyle='dotbox'
        )
        self.image_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        list_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.image_listbox.yview)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.image_listbox.config(yscrollcommand=list_scrollbar.set)

        # Image list buttons
        list_btn_frame = ttk.Frame(left_frame)
        list_btn_frame.pack(fill=tk.X, pady=5)

        # Add images button
        add_btn = ttk.Button(
            list_btn_frame,
            text="Add Images",
            command=self.add_images
        )
        add_btn.pack(side=tk.LEFT, padx=2)

        # Remove button
        remove_btn = ttk.Button(
            list_btn_frame,
            text="Remove",
            command=self.remove_selected
        )
        remove_btn.pack(side=tk.LEFT, padx=2)

        # Clear all button
        clear_btn = ttk.Button(
            list_btn_frame,
            text="Clear All",
            command=self.clear_all_images
        )
        clear_btn.pack(side=tk.LEFT, padx=2)

        # Middle panel (Image Preview)
        middle_frame = ttk.Frame(paned, padding="5")
        paned.add(middle_frame, weight=2)

        # Preview label
        preview_label = ttk.Label(middle_frame, text="Image Preview", font=('Helvetica', 12, 'bold'))
        preview_label.pack(anchor=tk.W)

        # Image canvas
        self.image_frame = ttk.Frame(middle_frame, relief=tk.SUNKEN, borderwidth=2)
        self.image_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.image_label = ttk.Label(self.image_frame, text="No image selected\n\nSelect an image from the list")
        self.image_label.pack(expand=True)

        # Detect button for single image
        self.detect_btn = ttk.Button(
            middle_frame,
            text="Detect Text (Selected)",
            command=self.detect_single_thread,
            state=tk.DISABLED
        )
        self.detect_btn.pack(fill=tk.X, pady=5)

        # Right panel (Results)
        right_frame = ttk.Frame(paned, padding="5")
        paned.add(right_frame, weight=3)

        # Result label
        result_label = ttk.Label(right_frame, text="Detected Text Results", font=('Helvetica', 12, 'bold'))
        result_label.pack(anchor=tk.W)

        # Control buttons
        control_frame = ttk.Frame(right_frame)
        control_frame.pack(fill=tk.X, pady=5)

        # Detect all button
        self.detect_all_btn = ttk.Button(
            control_frame,
            text="Detect All Images",
            command=self.detect_all_thread
        )
        self.detect_all_btn.pack(side=tk.LEFT, padx=2)

        # Copy all button
        copy_all_btn = ttk.Button(
            control_frame,
            text="Copy All",
            command=self.copy_all_to_clipboard
        )
        copy_all_btn.pack(side=tk.LEFT, padx=2)

        # Save all button
        save_all_btn = ttk.Button(
            control_frame,
            text="Save All",
            command=self.save_all_results
        )
        save_all_btn.pack(side=tk.LEFT, padx=2)

        # Clear results button
        clear_results_btn = ttk.Button(
            control_frame,
            text="Clear Results",
            command=self.clear_results
        )
        clear_results_btn.pack(side=tk.LEFT, padx=2)

        # Result text area
        self.result_text = scrolledtext.ScrolledText(
            right_frame,
            wrap=tk.WORD,
            width=50,
            height=20,
            font=('Consolas', 10)
        )
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=5)

        # Configure text tags
        self.result_text.tag_config('image_header', font=('Consolas', 11, 'bold'), foreground='blue')
        self.result_text.tag_config('text', font=('Consolas', 11))
        self.result_text.tag_config('text_grouped', font=('Consolas', 11, 'bold'), foreground='blue')
        self.result_text.tag_config('confidence', font=('Consolas', 9), foreground='gray')
        self.result_text.tag_config('separator', font=('Consolas', 8), foreground='lightgray')

        # Status bar
        space_mode = "NO SPACE" if self.delete_space else "WITH SPACE"
        self.status_var = tk.StringVar(value=f"Ready - Add images to start ({space_mode})")
        status_bar = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_bar.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(5, 0))

        # Keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self.add_images())
        self.root.bind('<Control-a>', lambda e: self.detect_all_thread())
        self.root.bind('<Control-d>', lambda e: self.detect_single_thread())
        self.root.bind('<Delete>', lambda e: self.remove_selected())
        self.root.bind('<Control-BackSpace>', lambda e: self.clear_all_images())

        # Bind listbox selection
        self.image_listbox.bind('<<ListboxSelect>>', self.on_image_select)

    def add_images(self):
        """Open file dialog to select multiple images."""
        filetypes = [
            ("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp"),
            ("All files", "*.*")
        ]

        filepaths = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=filetypes
        )

        if filepaths:
            for filepath in filepaths:
                self.load_image(filepath)

    def load_image(self, filepath):
        """
        Load and add image to list.

        Args:
            filepath: Path to image file
        """
        try:
            # Read image with OpenCV
            image = cv2.imread(filepath)
            if image is None:
                messagebox.showerror("Error", f"Cannot read image file: {filepath}")
                return

            # Add to images list
            img_data = {
                'path': filepath,
                'filename': os.path.basename(filepath),
                'image': image,
                'photo': None,
                'result': None,
                'status': 'pending'  # pending, detected, error
            }
            self.images.append(img_data)

            # Add to listbox
            self.image_listbox.insert(tk.END, f"{len(self.images)}. {os.path.basename(filepath)}")

            # Select the newly added image
            self.image_listbox.selection_clear(0, tk.END)
            self.image_listbox.selection_set(tk.END)
            self.image_listbox.see(tk.END)
            self.on_image_select(None)

            # Update status
            self.status_var.set(f"Added {len(self.images)} image(s)")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image:\n{e}")

    def on_image_select(self, event):
        """Handle image selection from list."""
        selection = self.image_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        self.current_index = index
        img_data = self.images[index]

        # Display image
        try:
            image = img_data['image']
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Resize to fit frame
            h, w = image.shape[:2]
            max_h = self.image_frame.winfo_height() - 20
            max_w = self.image_frame.winfo_width() - 20

            if max_h > 0 and max_w > 0:
                scale = min(max_w / w, max_h / h)
                new_w = int(w * scale)
                new_h = int(h * scale)
                image_rgb = cv2.resize(image_rgb, (new_w, new_h))

            # Convert to PhotoImage
            img_data['photo'] = ImageTk.PhotoImage(Image.fromarray(image_rgb))

            # Display
            self.image_label.config(image=img_data['photo'], text="")

            # Enable detect button if image not detected yet
            if img_data['status'] == 'pending':
                self.detect_btn.config(state=tk.NORMAL)
            else:
                self.detect_btn.config(state=tk.DISABLED)

            # Update status
            self.status_var.set(f"Selected: {img_data['filename']} ({w}x{h}) - {img_data['status'].upper()}")

        except Exception as e:
            self.image_label.config(image='', text="Error loading preview")
            print(f"Error loading preview: {e}")

    def remove_selected(self):
        """Remove selected image from list."""
        selection = self.image_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        
        # Remove from list and listbox
        self.images.pop(index)
        self.image_listbox.delete(index)

        # Update indices
        if self.current_index >= len(self.images):
            self.current_index = len(self.images) - 1

        # Update listbox numbering
        self.update_listbox_numbers()

        # Refresh display
        if self.current_index >= 0:
            self.image_listbox.selection_clear(0, tk.END)
            self.image_listbox.selection_set(self.current_index)
            self.on_image_select(None)
        else:
            self.image_label.config(image='', text="No image selected\n\nSelect an image from the list")
            self.detect_btn.config(state=tk.DISABLED)

        self.status_var.set(f"Removed image. {len(self.images)} image(s) remaining")

    def update_listbox_numbers(self):
        """Update numbering in listbox."""
        for i in range(len(self.images)):
            filename = self.images[i]['filename']
            self.image_listbox.delete(i)
            self.image_listbox.insert(i, f"{i+1}. {filename}")

    def clear_all_images(self):
        """Clear all images and results."""
        if not self.images:
            return

        if not messagebox.askyesno("Confirm", "Clear all images and results?"):
            return

        self.images.clear()
        self.current_index = -1
        self.image_listbox.delete(0, tk.END)
        self.image_label.config(image='', text="No image selected\n\nSelect an image from the list")
        self.detect_btn.config(state=tk.DISABLED)
        self.clear_results()
        self.status_var.set("Cleared all images")

    def detect_single_thread(self):
        """Run OCR detection for selected image in separate thread."""
        if self.current_index < 0 or self.current_index >= len(self.images):
            messagebox.showwarning("Warning", "Please select an image first")
            return

        img_data = self.images[self.current_index]
        if img_data['status'] == 'detected':
            if not messagebox.askyesno("Confirm", "This image already has results. Detect again?"):
                return

        # Disable button during processing
        self.detect_btn.config(state=tk.DISABLED)
        self.progress.start()
        self.status_var.set(f"Detecting text in: {img_data['filename']}...")

        # Run in thread
        thread = threading.Thread(target=self.detect_single, args=(self.current_index,))
        thread.daemon = True
        thread.start()

    def detect_single(self, index):
        """Run OCR detection for single image."""
        img_data = self.images[index]
        
        try:
            start_time = datetime.now()
            print(f"[{start_time.strftime('%H:%M:%S')}] [OCR] Running PaddleOCR prediction...")

            # Run PaddleOCR
            result = self.ocr.predict(img_data['image'])
            elapsed = (datetime.now() - start_time).total_seconds()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [OCR] Completed in {elapsed:.2f}s")

            # Parse result
            texts = self.parse_ocr_result(result)

            processing_time = (datetime.now() - start_time).total_seconds()

            img_data['result'] = {
                'texts': texts,
                'total_texts': len(texts),
                'processing_time': processing_time,
                'image_path': img_data['path'],
                'timestamp': datetime.now().isoformat()
            }
            img_data['status'] = 'detected'

            print(f"[{datetime.now().strftime('%H:%M:%S')}] [DEBUG] Found {len(texts)} text(s)")

            # Update UI in main thread
            self.root.after(0, lambda: self.update_single_result_ui(index))
            self.root.after(0, self.detect_complete)

        except Exception as e:
            error_message = str(e)
            print(f"[ERROR] Detection failed: {error_message}")
            img_data['status'] = 'error'
            self.root.after(0, lambda: messagebox.showerror("Error", f"Detection failed:\n{error_message}"))
            self.root.after(0, self.detect_complete)

    def detect_all_thread(self):
        """Run OCR detection for all images in separate thread."""
        if not self.images:
            messagebox.showwarning("Warning", "Please add images first")
            return

        # Disable button during processing
        self.detect_all_btn.config(state=tk.DISABLED)
        self.progress.start()
        self.status_var.set("Detecting text in all images...")

        # Run in thread
        thread = threading.Thread(target=self.detect_all)
        thread.daemon = True
        thread.start()

    def detect_all(self):
        """Run OCR detection for all images."""
        total_start = datetime.now()
        
        for i, img_data in enumerate(self.images):
            self.root.after(0, lambda idx=i: self.status_var.set(f"Processing {idx+1}/{len(self.images)}: {self.images[idx]['filename']}..."))
            
            try:
                start_time = datetime.now()
                print(f"[{start_time.strftime('%H:%M:%S')}] [OCR] Processing image {i+1}/{len(self.images)}...")

                # Run PaddleOCR
                result = self.ocr.predict(img_data['image'])
                elapsed = (datetime.now() - start_time).total_seconds()
                print(f"[{datetime.now().strftime('%H:%M:%S')}] [OCR] Completed in {elapsed:.2f}s")

                # Parse result
                texts = self.parse_ocr_result(result)

                processing_time = (datetime.now() - start_time).total_seconds()

                img_data['result'] = {
                    'texts': texts,
                    'total_texts': len(texts),
                    'processing_time': processing_time,
                    'image_path': img_data['path'],
                    'timestamp': datetime.now().isoformat()
                }
                img_data['status'] = 'detected'

                print(f"[{datetime.now().strftime('%H:%M:%S')}] [DEBUG] Found {len(texts)} text(s)")

            except Exception as e:
                error_message = str(e)
                print(f"[ERROR] Detection failed: {error_message}")
                img_data['status'] = 'error'

        total_elapsed = (datetime.now() - total_start).total_seconds()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [OCR] All detection completed in {total_elapsed:.2f}s")

        # Update UI in main thread
        self.root.after(0, self.update_all_results_ui)
        self.root.after(0, self.detect_all_complete)

    def parse_ocr_result(self, result):
        """Parse PaddleOCR result into structured format."""
        texts = []
        if result and len(result) > 0:
            first_result = result[0]
            if isinstance(first_result, dict):
                rec_texts = first_result.get('rec_texts', [])
                rec_scores = first_result.get('rec_scores', [])
                rec_polys = first_result.get('rec_polys', [])

                for i, (text, score, poly) in enumerate(zip(rec_texts, rec_scores, rec_polys)):
                    if score >= self.conf_threshold:
                        processed_text = text.strip()
                        if self.delete_space:
                            processed_text = processed_text.replace(' ', '')

                        bbox = poly.tolist() if hasattr(poly, 'tolist') else poly
                        avg_y = sum([pt[1] for pt in bbox]) / 4 if len(bbox) == 4 else 0
                        x_min = min([pt[0] for pt in bbox]) if len(bbox) == 4 else 0

                        texts.append({
                            'text': processed_text,
                            'confidence': float(score),
                            'bbox': bbox,
                            'original_text': text.strip(),
                            'avg_y': avg_y,
                            'x_min': x_min
                        })

                if self.group_by_line:
                    texts = self.group_texts_by_line(texts)

        return texts

    def group_texts_by_line(self, texts):
        """Group texts that are on the same horizontal line."""
        if not texts:
            return []

        # Sort by y-coordinate first
        texts_sorted = sorted(texts, key=lambda x: x['avg_y'])

        grouped = []
        current_line = [texts_sorted[0]]

        for i in range(1, len(texts_sorted)):
            current = texts_sorted[i]
            prev_avg_y = current_line[-1]['avg_y']

            # Check if current text is on the same line as previous
            if abs(current['avg_y'] - prev_avg_y) <= self.line_tolerance:
                # Same line - add to current group
                current_line.append(current)
            else:
                # Different line - finalize current line and start new one
                if len(current_line) > 1:
                    # Merge texts in the same line
                    merged_text = self.merge_line_texts(current_line)
                    grouped.append(merged_text)
                else:
                    # Single text on this line
                    grouped.append(current_line[0])
                current_line = [current]

        # Don't forget the last line
        if len(current_line) > 1:
            merged_text = self.merge_line_texts(current_line)
            grouped.append(merged_text)
        else:
            grouped.append(current_line[0])

        # Sort by y-coordinate (top to bottom)
        grouped.sort(key=lambda x: x['avg_y'])

        return grouped

    def merge_line_texts(self, texts):
        """Merge multiple texts on the same line into one."""
        # Sort by x-coordinate (left to right)
        texts_sorted = sorted(texts, key=lambda x: x['x_min'])

        # Merge texts
        merged_text = ' '.join([t['text'] for t in texts_sorted])
        merged_original = ' '.join([t['original_text'] for t in texts_sorted])

        # Apply DELETE_SPACE to merged result if enabled
        if self.delete_space:
            merged_text = merged_text.replace(' ', '')
            merged_original = merged_original.replace(' ', '')

        # Average confidence
        avg_confidence = sum([t['confidence'] for t in texts_sorted]) / len(texts_sorted)

        # Use bounding box of first text
        first_text = texts_sorted[0]

        return {
            'text': merged_text,
            'original_text': merged_original,
            'confidence': avg_confidence,
            'bbox': first_text['bbox'],
            'avg_y': first_text['avg_y'],
            'is_grouped': True,
            'line_count': len(texts_sorted)
        }

    def update_single_result_ui(self, index):
        """Update result display for single image."""
        img_data = self.images[index]
        if img_data['result'] is None:
            return

        # Clear and show only this image's result
        self.result_text.delete(1.0, tk.END)

        # Display header
        self.result_text.insert(tk.END, f"Image: {img_data['filename']}\n", 'image_header')
        self.result_text.insert(tk.END, "="*60 + "\n\n", 'separator')

        # Display results
        texts = img_data['result']['texts']

        if texts:
            for i, item in enumerate(texts, 1):
                if item.get('is_grouped', False):
                    line_count = item.get('line_count', 0)
                    self.result_text.insert(
                        tk.END,
                        f"[{i}] {item['text']} (merged {line_count} parts)\n",
                        'text_grouped'
                    )
                else:
                    self.result_text.insert(
                        tk.END,
                        f"[{i}] {item['text']}\n",
                        'text'
                    )

                self.result_text.insert(
                    tk.END,
                    f"    Confidence: {item['confidence']:.2f}\n\n",
                    'confidence'
                )
        else:
            self.result_text.insert(tk.END, "No text detected\n")

        # Update status
        self.status_var.set(
            f"Detected {len(texts)} text(s) in {img_data['result']['processing_time']:.2f}s"
        )

        # Update listbox item
        self.image_listbox.delete(index)
        status_icon = "✓" if img_data['status'] == 'detected' else "✗"
        self.image_listbox.insert(index, f"{index+1}. {img_data['filename']} {status_icon}")

    def update_all_results_ui(self):
        """Update result display for all images."""
        # Clear text area
        self.result_text.delete(1.0, tk.END)

        total_texts = 0
        detected_count = 0

        # Display results grouped by image
        for i, img_data in enumerate(self.images):
            if img_data['result'] is None:
                continue

            detected_count += 1
            total_texts += img_data['result']['total_texts']

            # Display header
            self.result_text.insert(tk.END, f"Image {i+1}: {img_data['filename']}\n", 'image_header')
            self.result_text.insert(tk.END, "-"*60 + "\n", 'separator')

            # Display results
            texts = img_data['result']['texts']

            if texts:
                for j, item in enumerate(texts, 1):
                    if item.get('is_grouped', False):
                        line_count = item.get('line_count', 0)
                        self.result_text.insert(
                            tk.END,
                            f"  [{j}] {item['text']} (merged {line_count} parts)\n",
                            'text_grouped'
                        )
                    else:
                        self.result_text.insert(
                            tk.END,
                            f"  [{j}] {item['text']}\n",
                            'text'
                        )

                    self.result_text.insert(
                        tk.END,
                        f"      Confidence: {item['confidence']:.2f}\n\n",
                        'confidence'
                    )
            else:
                self.result_text.insert(tk.END, "  No text detected\n")

            self.result_text.insert(tk.END, "\n", 'separator')

        # Update status
        self.status_var.set(f"Detected {total_texts} text(s) from {detected_count}/{len(self.images)} images")

    def detect_complete(self):
        """Single detection complete callback."""
        self.detect_btn.config(state=tk.NORMAL)
        self.progress.stop()

    def detect_all_complete(self):
        """All detection complete callback."""
        self.detect_all_btn.config(state=tk.NORMAL)
        self.progress.stop()

        # Refresh current selection
        if self.current_index >= 0:
            self.image_listbox.selection_clear(0, tk.END)
            self.image_listbox.selection_set(self.current_index)
            self.on_image_select(None)

    def copy_all_to_clipboard(self):
        """Copy all detected text to clipboard."""
        all_text = []
        
        for img_data in self.images:
            if img_data['result'] and img_data['result']['texts']:
                all_text.append(f"=== {img_data['filename']} ===")
                for item in img_data['result']['texts']:
                    all_text.append(item['text'])
                all_text.append("")

        if not all_text:
            messagebox.showinfo("Info", "No text to copy")
            return

        # Copy to clipboard
        self.root.clipboard_clear()
        self.root.clipboard_append("\n".join(all_text))

        self.status_var.set("Copied all text to clipboard!")
        messagebox.showinfo("Success", f"Text from {len([i for i in self.images if i['result']])} images copied to clipboard!")

    def save_all_results(self):
        """Save all results to file."""
        if not any(img_data['result'] for img_data in self.images):
            messagebox.showwarning("Warning", "No results to save")
            return

        # Ask for filename
        filetypes = [
            ("JSON files", "*.json"),
            ("Text files", "*.txt"),
            ("All files", "*.*")
        ]

        filepath = filedialog.asksaveasfilename(
            title="Save All Results",
            defaultextension=".json",
            filetypes=filetypes
        )

        if not filepath:
            return

        try:
            if filepath.endswith('.json'):
                # Save as JSON
                results = []
                for img_data in self.images:
                    if img_data['result']:
                        results.append(img_data['result'])
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
            else:
                # Save as TXT
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("PaddleOCR Multiple Image Text Detection Result\n")
                    f.write("="*60 + "\n\n")
                    f.write(f"Total Images: {len(self.images)}\n")
                    f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                    f.write("="*60 + "\n\n")

                    for i, img_data in enumerate(self.images, 1):
                        if not img_data['result']:
                            continue

                        f.write(f"Image {i}: {img_data['filename']}\n")
                        f.write("-"*60 + "\n")
                        f.write(f"  Path: {img_data['path']}\n")
                        f.write(f"  Processing Time: {img_data['result']['processing_time']:.2f}s\n")
                        f.write(f"  Total Texts: {img_data['result']['total_texts']}\n")
                        f.write("\n")

                        for j, item in enumerate(img_data['result']['texts'], 1):
                            f.write(f"  [{j}] {item['text']}\n")
                            f.write(f"      Confidence: {item['confidence']:.2f}\n\n")

                        f.write("\n")

            self.status_var.set(f"Saved: {os.path.basename(filepath)}")
            messagebox.showinfo("Success", f"Results saved to:\n{filepath}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save:\n{e}")

    def clear_results(self):
        """Clear all results but keep images."""
        self.result_text.delete(1.0, tk.END)
        for img_data in self.images:
            img_data['result'] = None
            img_data['status'] = 'pending'
        
        # Update listbox
        for i in range(len(self.images)):
            self.image_listbox.delete(i)
            self.image_listbox.insert(i, f"{i+1}. {self.images[i]['filename']}")
        
        self.status_var.set("Cleared results. Ready to detect.")

    def refresh_after_detect(self):
        """Refresh UI after detection."""
        if self.current_index >= 0:
            self.image_listbox.selection_clear(0, tk.END)
            self.image_listbox.selection_set(self.current_index)
            self.on_image_select(None)


def main():
    """Main entry point."""
    root = tk.Tk()
    app = PaddleOCRMultipleInputGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
