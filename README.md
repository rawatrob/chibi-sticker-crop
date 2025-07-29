# Sticker Crop & Background Removal

A Python utility to split a 3×3 grid of stickers into individual PNGs, automatically crop each sticker, and remove only the true background (grey or red) while preserving any in‑art grey or white outlines. 

![Example output](./examples/sticker_0_1.png)

## Features

- **Adaptive background detection**  
  Samples the outer border of the source image to find the exact background color (grey or red), so you don’t need to hard‑code any RGB values.

- **Grid‑aware cropping**  
  Assumes a fixed `COLS × ROWS` layout (default 3×3), finds the nine largest non‑background regions, and sorts them in reading order (left→right, top→bottom).

- **True‑background removal**  
  Uses connected‑component labeling to distinguish the “outer” background from any same‑hue pixels inside the sticker art (e.g. grey shadows or white outlines). Only those background regions that touch the image edge get made transparent.

- **RGBA output**  
  Exports each sticker as a tight, alpha‑masked PNG (`sticker_<row>_<col>.png`) with perfect transparency around the art.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/sticker-cropper.git
   cd sticker-cropper

2. Install dependencies (tested with Python 3.9+):
```bash
pip install Pillow numpy opencv-python

How It Works
Sample Background Color
Take the median RGB of the outer 5 px border to find the exact background shade.

Mask Background Pixels
Compute the Euclidean distance of each pixel’s RGB to that background color; mark any within threshold as background.

Label & Identify True Background
Run connected‑component analysis on the full-image background mask; track which components touch the very edge of the image.

Locate Sticker Regions
Invert the background mask to find “content” pixels, label those regions, pick the nine largest, and order them left‑to‑right, top‑to‑bottom.

Crop & Clean Each Sticker
For each region, crop out its bounding box, then make transparent only those background pixels whose connected‑component label was flagged as “edge‑touching.”

Save PNGs
Export each cleaned sticker as sticker_<row>_<col>.png with a transparent background.

```bash
python crop_stickers.py
