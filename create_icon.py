#!/usr/bin/env python3
"""
Simple script to create a basic tray icon file
"""

import os
from PIL import Image, ImageDraw

def create_simple_icon():
    """Create a simple Discord-style icon"""
    try:
        # Create a 32x32 icon with PIL
        size = 32
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw a simple Discord-like icon (rounded rectangle with a chat bubble)
        # Main shape - rounded rectangle
        draw.rounded_rectangle([4, 8, 28, 24], radius=4, fill=(88, 101, 242, 255))  # Discord blue
        
        # Simple dots for "eyes"
        draw.ellipse([9, 12, 11, 14], fill=(255, 255, 255, 255))
        draw.ellipse([21, 12, 23, 14], fill=(255, 255, 255, 255))
        
        # Simple line for "mouth"
        draw.line([12, 18, 20, 18], fill=(255, 255, 255, 255), width=2)
        
        # Save as ICO
        img.save('tray_icon.ico', format='ICO', sizes=[(16, 16), (32, 32)])
        print("✓ Created tray_icon.ico")
        
    except ImportError:
        print("PIL/Pillow not available, creating placeholder icon file...")
        create_placeholder_icon()

def create_placeholder_icon():
    """Create a placeholder icon file if PIL is not available"""
    # Create a minimal ICO file manually
    ico_data = bytearray([
        # ICO header
        0x00, 0x00,  # Reserved
        0x01, 0x00,  # Type (1 = ICO)
        0x01, 0x00,  # Number of images
        
        # Directory entry
        0x10,  # Width (16)
        0x10,  # Height (16)
        0x00,  # Colors (0 = 256)
        0x00,  # Reserved
        0x01, 0x00,  # Color planes
        0x20, 0x00,  # Bits per pixel (32)
        0x00, 0x04, 0x00, 0x00,  # Image size (1024 bytes)
        0x16, 0x00, 0x00, 0x00,  # Image offset
    ])
    
    # Add a simple 16x16 32-bit image data (transparent with a simple pattern)
    image_data = bytearray(1024)  # 16x16x4 bytes (RGBA)
    
    # Create a simple pattern
    for y in range(16):
        for x in range(16):
            offset = (y * 16 + x) * 4
            if 4 <= x <= 11 and 4 <= y <= 11:
                image_data[offset] = 88      # Blue
                image_data[offset + 1] = 101  # Green
                image_data[offset + 2] = 242  # Red
                image_data[offset + 3] = 255  # Alpha
    
    ico_data.extend(image_data)
    
    with open('tray_icon.ico', 'wb') as f:
        f.write(ico_data)
    
    print("✓ Created placeholder tray_icon.ico")

def main():
    """Create the icon file"""
    print("Creating application icon...")
    
    try:
        create_simple_icon()
    except Exception as e:
        print(f"Error creating icon: {e}")
        create_placeholder_icon()

if __name__ == "__main__":
    main() 