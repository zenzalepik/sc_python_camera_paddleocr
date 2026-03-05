"""
PaddleOCR Mobile - Desktop GUI Application
Aplikasi desktop upload gambar dengan PaddleOCR v5 Mobile untuk deteksi teks otomatis

Fitur:
- GUI sederhana dengan Tkinter
- Upload gambar (drag & drop atau browse)
- Preview gambar
- Deteksi teks otomatis dengan PaddleOCR v5 Mobile
- Tampilkan hasil teks dengan confidence score
- Export hasil ke TXT/JSON
- Copy hasil ke clipboard
"""

import os
import sys
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import threading
from datetime import datetime

import cv2
import numpy as np
from PIL import Image, ImageTk
from dotenv import load_dotenv

# Import PaddleOCR
try:
    from paddleocr import PaddleOCR
    # Disable model source check
    import os
    os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'
except ImportError:
    print("❌ PaddleOCR tidak terinstall!")
    print("💡 Install dengan: pip install paddlepaddle paddleocr")
    sys.exit(1)

# Load konfigurasi
load_dotenv()


class PaddleOCRDesktopApp:
    """PaddleOCR Mobile - Desktop GUI Application."""

    def __init__(self, root):
        """Initialize Desktop App."""
        self.root = root
        self.root.title("📱 PaddleOCR Mobile - Text Detection")
        self.root.geometry("1200x700")
        self.root.minsize(1000, 600)
        
        # Set icon (if available)
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass
        
        # OCR Settings
        self.lang = os.getenv('OCR_LANG', 'en')
        self.use_gpu = os.getenv('USE_GPU', 'False') == 'True'
        self.use_angle_cls = os.getenv('USE_ANGLE_CLS', 'True') == 'True'
        self.conf_threshold = float(os.getenv('CONF_THRESHOLD', '0.5'))
        self.output_dir = os.getenv('OUTPUT_DIR', 'output')
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # State variables
        self.current_image = None
        self.current_image_path = None
        self.current_result = None
        self.photo_image = None
        
        # Initialize PaddleOCR
        self.ocr = None
        self.init_ocr()
        
        # Build UI
        self.build_ui()
        
        # Bind events
        self.bind_events()

    def init_ocr(self):
        """Initialize PaddleOCR engine."""
        print("🔍 Initializing PaddleOCR v5 Mobile...")
        try:
            # PaddleOCR v5 new API - use mobile models
            self.ocr = PaddleOCR(
                lang=self.lang,
                text_detection_model_name='PP-OCRv5_mobile_det',
                text_recognition_model_name='PP-OCRv5_mobile_rec',
            )
            print("✅ PaddleOCR v5 Mobile initialized!")
        except Exception as e:
            print(f"❌ Error initializing PaddleOCR: {e}")
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
            text="📱 PaddleOCR Mobile - Text Detection",
            font=('Helvetica', 16, 'bold')
        )
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Create paned window
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Left panel (Image)
        left_frame = ttk.Frame(paned, padding="5")
        paned.add(left_frame, weight=1)
        
        # Image label
        image_label = ttk.Label(left_frame, text="📷 Image Preview", font=('Helvetica', 12, 'bold'))
        image_label.pack(anchor=tk.W)
        
        # Image canvas
        self.image_frame = ttk.Frame(left_frame, relief=tk.SUNKEN, borderwidth=2)
        self.image_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.image_label = ttk.Label(self.image_frame, text="No image loaded")
        self.image_label.pack(expand=True)
        
        # Upload button
        upload_btn = ttk.Button(
            left_frame, 
            text="📁 Upload Image", 
            command=self.upload_image
        )
        upload_btn.pack(fill=tk.X, pady=5)
        
        # Right panel (Results)
        right_frame = ttk.Frame(paned, padding="5")
        paned.add(right_frame, weight=1)
        
        # Result label
        result_label = ttk.Label(right_frame, text="📝 Detected Text", font=('Helvetica', 12, 'bold'))
        result_label.pack(anchor=tk.W)
        
        # Result text area
        self.result_text = scrolledtext.ScrolledText(
            right_frame, 
            wrap=tk.WORD, 
            width=40, 
            height=20,
            font=('Consolas', 10)
        )
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Button frame
        btn_frame = ttk.Frame(right_frame)
        btn_frame.pack(fill=tk.X)
        
        # Detect button
        self.detect_btn = ttk.Button(
            btn_frame,
            text="🔍 Detect Text",
            command=self.detect_text_thread,
            state=tk.DISABLED
        )
        self.detect_btn.pack(side=tk.LEFT, padx=2)
        
        # Copy button
        copy_btn = ttk.Button(
            btn_frame,
            text="📋 Copy",
            command=self.copy_to_clipboard
        )
        copy_btn.pack(side=tk.LEFT, padx=2)
        
        # Save button
        save_btn = ttk.Button(
            btn_frame,
            text="💾 Save",
            command=self.save_result
        )
        save_btn.pack(side=tk.LEFT, padx=2)
        
        # Clear button
        clear_btn = ttk.Button(
            btn_frame,
            text="🗑️ Clear",
            command=self.clear_all
        )
        clear_btn.pack(side=tk.LEFT, padx=2)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
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

    def bind_events(self):
        """Bind drag and drop events."""
        # Drag and drop support
        self.image_frame.drop_target_register(tk.DND_FILES)
        self.image_frame.dnd_bind('<<Drop>>', self.on_drop)
        
        # Keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self.upload_image())
        self.root.bind('<Control-d>', lambda e: self.detect_text_thread())
        self.root.bind('<Control-c>', lambda e: self.copy_to_clipboard())
        self.root.bind('<Control-s>', lambda e: self.save_result())
        self.root.bind('<Delete>', lambda e: self.clear_all())

    def upload_image(self):
        """Open file dialog to upload image."""
        filetypes = [
            ("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp"),
            ("All files", "*.*")
        ]
        
        filepath = filedialog.askopenfilename(
            title="Select Image",
            filetypes=filetypes
        )
        
        if filepath:
            self.load_image(filepath)

    def on_drop(self, event):
        """Handle drag and drop event."""
        filepath = event.data.strip('{}')  # Remove curly braces from path
        if os.path.isfile(filepath):
            self.load_image(filepath)

    def load_image(self, filepath):
        """
        Load and display image.
        
        Args:
            filepath: Path to image file
        """
        try:
            # Read image with OpenCV
            image = cv2.imread(filepath)
            if image is None:
                messagebox.showerror("Error", "Cannot read image file")
                return
            
            self.current_image = image
            self.current_image_path = filepath
            
            # Convert to RGB for PIL
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
            self.photo_image = ImageTk.PhotoImage(Image.fromarray(image_rgb))
            
            # Display
            self.image_label.config(image=self.photo_image, text="")
            
            # Enable detect button
            self.detect_btn.config(state=tk.NORMAL)
            
            # Update status
            filename = os.path.basename(filepath)
            self.status_var.set(f"Loaded: {filename} ({w}x{h})")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image:\n{e}")

    def detect_text_thread(self):
        """Run OCR detection in separate thread."""
        if self.current_image is None:
            messagebox.showwarning("Warning", "Please upload an image first")
            return
        
        # Disable button during processing
        self.detect_btn.config(state=tk.DISABLED)
        self.progress.start()
        self.status_var.set("Detecting text...")
        
        # Run in thread
        thread = threading.Thread(target=self.detect_text)
        thread.daemon = True
        thread.start()

    def detect_text(self):
        """Run OCR detection."""
        try:
            start_time = datetime.now()
            
            # Run PaddleOCR
            result = self.ocr.predict(self.current_image)
            
            # Parse result
            texts = []
            if result and len(result) > 0:
                first_result = result[0]
                if isinstance(first_result, dict):
                    rec_texts = first_result.get('rec_texts', [])
                    rec_scores = first_result.get('rec_scores', [])
                    rec_polys = first_result.get('rec_polys', [])
                    
                    for i, (text, score, poly) in enumerate(zip(rec_texts, rec_scores, rec_polys)):
                        if score >= self.conf_threshold:
                            texts.append({
                                'text': text.strip(),
                                'confidence': float(score),
                                'bbox': poly.tolist() if hasattr(poly, 'tolist') else poly
                            })
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            self.current_result = {
                'texts': texts,
                'total_texts': len(texts),
                'processing_time': processing_time,
                'image_path': self.current_image_path,
                'timestamp': datetime.now().isoformat()
            }
            
            # Update UI in main thread
            self.root.after(0, self.update_result_ui)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Detection failed:\n{e}"))
        finally:
            self.root.after(0, self.detect_complete)

    def update_result_ui(self):
        """Update result display."""
        if self.current_result is None:
            return
        
        # Clear text area
        self.result_text.delete(1.0, tk.END)
        
        # Display results
        texts = self.current_result['texts']
        
        if texts:
            for i, item in enumerate(texts, 1):
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
        
        # Configure tags
        self.result_text.tag_config('text', font=('Consolas', 11))
        self.result_text.tag_config('confidence', font=('Consolas', 9), foreground='gray')
        
        # Update status
        self.status_var.set(
            f"Detected {len(texts)} text(s) in {self.current_result['processing_time']:.2f}s"
        )

    def detect_complete(self):
        """Detection complete callback."""
        self.detect_btn.config(state=tk.NORMAL)
        self.progress.stop()

    def copy_to_clipboard(self):
        """Copy detected text to clipboard."""
        if self.current_result is None or not self.current_result['texts']:
            messagebox.showinfo("Info", "No text to copy")
            return
        
        # Extract texts
        all_text = "\n".join([item['text'] for item in self.current_result['texts']])
        
        # Copy to clipboard
        self.root.clipboard_clear()
        self.root.clipboard_append(all_text)
        
        self.status_var.set("Copied to clipboard!")
        messagebox.showinfo("Success", "Text copied to clipboard!")

    def save_result(self):
        """Save result to file."""
        if self.current_result is None:
            messagebox.showwarning("Warning", "No result to save")
            return
        
        # Ask for filename
        filetypes = [
            ("JSON files", "*.json"),
            ("Text files", "*.txt"),
            ("All files", "*.*")
        ]
        
        filepath = filedialog.asksaveasfilename(
            title="Save Result",
            defaultextension=".json",
            filetypes=filetypes
        )
        
        if not filepath:
            return
        
        try:
            if filepath.endswith('.json'):
                # Save as JSON
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(self.current_result, f, indent=2, ensure_ascii=False)
            else:
                # Save as TXT
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("PaddleOCR Text Detection Result\n")
                    f.write("="*60 + "\n\n")
                    f.write(f"Image: {self.current_result['image_path']}\n")
                    f.write(f"Timestamp: {self.current_result['timestamp']}\n")
                    f.write(f"Processing Time: {self.current_result['processing_time']:.2f}s\n")
                    f.write(f"Total Texts: {self.current_result['total_texts']}\n")
                    f.write("="*60 + "\n\n")
                    
                    for i, item in enumerate(self.current_result['texts'], 1):
                        f.write(f"[{i}] {item['text']}\n")
                        f.write(f"    Confidence: {item['confidence']:.2f}\n\n")
            
            self.status_var.set(f"Saved: {os.path.basename(filepath)}")
            messagebox.showinfo("Success", f"Result saved to:\n{filepath}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save:\n{e}")

    def clear_all(self):
        """Clear all data."""
        self.current_image = None
        self.current_image_path = None
        self.current_result = None
        self.photo_image = None
        
        self.image_label.config(image='', text="No image loaded")
        self.result_text.delete(1.0, tk.END)
        self.detect_btn.config(state=tk.DISABLED)
        self.status_var.set("Ready")


def main():
    """Main entry point."""
    root = tk.Tk()
    app = PaddleOCRDesktopApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
