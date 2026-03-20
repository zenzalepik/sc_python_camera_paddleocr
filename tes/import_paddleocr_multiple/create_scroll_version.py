"""
App Grid dengan Vertical Scroll - UPDATED
Scroll functionality untuk grid thumbnail
"""

# Import file asli dan tambahkan scroll
import sys
import os

# Baca file asli
with open('app_grid.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Tambahkan scroll variable di __init__
if 'self.grid_scroll_offset = 0' not in content:
    content = content.replace(
        'self.selected_index = -1  # Selected image in grid',
        'self.selected_index = -1  # Selected image in grid\n        self.grid_scroll_offset = 0  # Scroll offset (pixels)\n        self.grid_rows = 0  # Jumlah rows'
    )

# Save
with open('app_grid_scroll.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Created app_grid_scroll.py with scroll variables!")
print("Now you need to update draw_grid() and on_mouse_click() manually")
