"""
Selamat Datang - Parent Application
Aplikasi parent yang mengimport dan menampilkan Object Distance Widget
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

# Add widget path to sys.path untuk import
widget_path = os.path.join(os.path.dirname(__file__), '..', 'v6_Deteksi_Object_Mendekat', 'export_to_widget')
sys.path.insert(0, widget_path)

# Import widget
from object_distance_widget import ObjectDistanceWidget


class WelcomeApp:
    """Aplikasi Parent untuk Object Distance Detection Widget."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Selamat Datang - Object Distance Detection System")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a1a')
        
        # Configure grid weights
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create UI
        self._create_header()
        self._create_content()
        self._create_footer()
        
        # Widget reference
        self.detection_widget = None
    
    def _create_header(self):
        """Create header section."""
        header_frame = tk.Frame(self.root, bg='#2d2d2d', height=80)
        header_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=10)
        header_frame.grid_propagate(False)
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="🎯 Object Distance Detection System",
            font=("Arial", 24, "bold"),
            bg='#2d2d2d',
            fg='#00ff00'
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=20)
        
        # Subtitle
        subtitle_label = tk.Label(
            header_frame,
            text="Real-time Object Detection dengan YOLO - Parking System",
            font=("Arial", 12),
            bg='#2d2d2d',
            fg='#888888'
        )
        subtitle_label.pack(side=tk.LEFT, padx=20, pady=25)
    
    def _create_content(self):
        """Create content section with widget."""
        content_frame = tk.Frame(self.root, bg='#1a1a1a')
        content_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=2)
        
        # Left panel - Information
        info_frame = tk.Frame(content_frame, bg='#2d2d2d', width=300)
        info_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 5), pady=5)
        info_frame.grid_propagate(False)
        
        self._create_info_panel(info_frame)
        
        # Right panel - Widget
        widget_container = tk.Frame(content_frame, bg='#000000')
        widget_container.grid(row=0, column=1, sticky='nsew', padx=(5, 0), pady=5)
        widget_container.grid_rowconfigure(0, weight=1)
        widget_container.grid_columnconfigure(0, weight=1)
        
        self._create_widget_container(widget_container)
    
    def _create_info_panel(self, parent):
        """Create information panel."""
        # Title
        title_label = tk.Label(
            parent,
            text="📋 Informasi",
            font=("Arial", 16, "bold"),
            bg='#2d2d2d',
            fg='#00ff00',
            anchor='w'
        )
        title_label.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        # Separator
        sep = tk.Frame(parent, bg='#444444', height=2)
        sep.pack(fill=tk.X, padx=15, pady=5)
        
        # Info text
        info_text = tk.Text(
            parent,
            bg='#2d2d2d',
            fg='#cccccc',
            font=("Consolas", 10),
            wrap=tk.WORD,
            borderwidth=0,
            highlightthickness=0
        )
        info_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        info_content = """
SELAMAT DATANG di
Object Distance Detection System

═══════════════════════════════════

🎯 FITUR UTAMA:
• Deteksi object mendekat/menjauh
• SIAGA alert system
• Parking system 4 fase
• Real-time tracking dengan YOLO

═══════════════════════════════════

🅿️ PARKING SYSTEM:

FASE 1 - SIAGA (3 frame)
  → Object terdeteksi mendekat

FASE 2 - TETAP (5 frame)
  → Object berhenti

FASE 3 - LOOP (3 frame)
  → Trigger loop detector

FASE 4 - TAP (3 frame)
  → Trigger tap card

═══════════════════════════════════

⌨️ KEYBOARD SHORTCUTS:

Y - Toggle YOLO ON/OFF
R - Reset tracking
L - Trigger Loop Detector
T - Trigger Tap Card
Q - Quit

═══════════════════════════════════

🎨 STATUS INDIKATOR:

🔴 MERAH   = Mendekat
🟢 HIJAU   = Tetap
🔵 BIRU    = Menjauh
🟠 ORANGE  = SIAGA Alert

═══════════════════════════════════

💡 TIPS:
• Pastikan kamera terhubung
• Pencahayaan cukup untuk deteksi optimal
• Object harus terlihat jelas di frame
• Widget ini reusable - bisa dipasang di frame apapun!
"""
        
        info_text.insert('1.0', info_content)
        info_text.config(state='disabled')
        
        # Control buttons
        button_frame = tk.Frame(parent, bg='#2d2d2d')
        button_frame.pack(fill=tk.X, padx=15, pady=15)
        
        self.start_btn = tk.Button(
            button_frame,
            text="▶ START",
            command=self._on_start,
            font=("Arial", 11, "bold"),
            bg='#00aa00',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            activebackground='#00cc00',
            activeforeground='white'
        )
        self.start_btn.pack(fill=tk.X, pady=5)
        
        self.stop_btn = tk.Button(
            button_frame,
            text="⏹ STOP",
            command=self._on_stop,
            font=("Arial", 11, "bold"),
            bg='#aa0000',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            activebackground='#cc0000',
            activeforeground='white',
            state='disabled'
        )
        self.stop_btn.pack(fill=tk.X, pady=5)
        
        self.toggle_yolo_btn = tk.Button(
            button_frame,
            text="🔄 Toggle YOLO",
            command=self._on_toggle_yolo,
            font=("Arial", 10),
            bg='#0066aa',
            fg='white',
            padx=15,
            pady=6,
            cursor='hand2',
            activebackground='#0088cc',
            activeforeground='white',
            state='disabled'
        )
        self.toggle_yolo_btn.pack(fill=tk.X, pady=5)
        
        self.reset_btn = tk.Button(
            button_frame,
            text="🔄 Reset Tracking",
            command=self._on_reset,
            font=("Arial", 10),
            bg='#666666',
            fg='white',
            padx=15,
            pady=6,
            cursor='hand2',
            activebackground='#888888',
            activeforeground='white',
            state='disabled'
        )
        self.reset_btn.pack(fill=tk.X, pady=5)
    
    def _create_widget_container(self, parent):
        """Create container for detection widget."""
        # Welcome label (will be replaced by widget)
        self.welcome_label = tk.Label(
            parent,
            text="👋 Selamat Datang!\n\nKlik tombol START untuk memulai deteksi",
            font=("Arial", 18, "bold"),
            bg='#000000',
            fg='#00ff00',
            justify=tk.CENTER
        )
        self.welcome_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    def _create_footer(self):
        """Create footer section."""
        footer_frame = tk.Frame(self.root, bg='#2d2d2d', height=40)
        footer_frame.grid(row=2, column=0, sticky='ew', padx=10, pady=(5, 10))
        footer_frame.grid_propagate(False)
        
        # Status label
        self.status_label = tk.Label(
            footer_frame,
            text="Status: Ready",
            font=("Arial", 10),
            bg='#2d2d2d',
            fg='#888888',
            anchor='w'
        )
        self.status_label.pack(side=tk.LEFT, padx=20)
        
        # Version label
        version_label = tk.Label(
            footer_frame,
            text="Widget Version: 1.0.0 | Parent App: 1.0.0",
            font=("Arial", 9),
            bg='#2d2d2d',
            fg='#666666',
            anchor='e'
        )
        version_label.pack(side=tk.RIGHT, padx=20)
    
    def _create_widget(self):
        """Create and initialize detection widget."""
        if self.detection_widget:
            return
        
        # Destroy welcome label
        if self.welcome_label:
            self.welcome_label.destroy()
        
        # Create widget
        self.detection_widget = ObjectDistanceWidget(
            self.root.winfo_children()[1].winfo_children()[0].winfo_children()[1],
            camera_id=0,
            on_session_complete=self._on_session_complete,
            bg='#000000'
        )
        self.detection_widget.pack(fill=tk.BOTH, expand=True)
    
    def _on_start(self):
        """Handle start button click."""
        try:
            # Create widget if not exists
            if not self.detection_widget:
                self._create_widget()
            
            # Start detection
            self.detection_widget.start()
            
            # Update UI
            self.start_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            self.toggle_yolo_btn.config(state='normal')
            self.reset_btn.config(state='normal')
            self.status_label.config(text="Status: Running")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start detection:\n{str(e)}")
    
    def _on_stop(self):
        """Handle stop button click."""
        if self.detection_widget:
            self.detection_widget.stop()
            
            # Update UI
            self.start_btn.config(state='normal')
            self.stop_btn.config(state='disabled')
            self.toggle_yolo_btn.config(state='disabled')
            self.reset_btn.config(state='disabled')
            self.status_label.config(text="Status: Stopped")
    
    def _on_toggle_yolo(self):
        """Handle toggle YOLO button click."""
        if self.detection_widget:
            self.detection_widget.toggle_yolo()
            
            # Update status
            if self.detection_widget.is_yolo_enabled():
                self.status_label.config(text="Status: YOLO ON")
            else:
                self.status_label.config(text="Status: YOLO OFF")
    
    def _on_reset(self):
        """Handle reset button click."""
        if self.detection_widget:
            self.detection_widget.reset_tracking()
            self.status_label.config(text="Status: Tracking Reset")
    
    def _on_session_complete(self, session):
        """Callback when parking session completes."""
        print(f"✅ Session Complete: {session.session_id}")
        print(f"   Vehicle: {session.vehicle_id}")
        print(f"   Captures saved to: captures/{session.session_id}/")
        
        # Show notification
        self.status_label.config(text=f"✅ Session Complete: {session.session_id}")
        
        # Optional: Show message box
        # messagebox.showinfo(
        #     "Session Complete",
        #     f"Parking session completed!\n\n"
        #     f"Session ID: {session.session_id}\n"
        #     f"Vehicle: {session.vehicle_id}\n"
        #     f"Captures saved to: captures/{session.session_id}/"
        # )


def main():
    """Main function."""
    root = tk.Tk()
    app = WelcomeApp(root)
    
    # Bind keyboard shortcuts
    def on_key_press(event):
        if event.char == 'q' or event.char == 'Q':
            if app.detection_widget:
                app._on_stop()
            root.quit()
    
    root.bind('<Key>', on_key_press)
    
    # Center window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()


if __name__ == "__main__":
    main()
