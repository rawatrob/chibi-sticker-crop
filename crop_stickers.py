import os
from PIL import Image
import numpy as np
import cv2

# === CONFIG ===
INPUT_PATH  = './replicate-prediction-bj0gbaantnrma0cramjsxattt0.png'
OUTPUT_DIR  = 'sticker_transparent'
COLS, ROWS = 3, 3

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load image as before
pil_img = Image.open(INPUT_PATH).convert('RGB')
arr = np.array(pil_img)
h, w, _ = arr.shape

# 1) Estimate background color
border_pixels = np.concatenate([
    arr[:5, :, :].reshape(-1, 3),
    arr[-5:, :, :].reshape(-1, 3),
    arr[:, :5, :].reshape(-1, 3),
    arr[:, -5:, :].reshape(-1, 3)
])
bg_color = np.median(border_pixels, axis=0).astype(np.uint8)

# 2) Background mask by color‑distance
dist = np.linalg.norm(arr.astype(float) - bg_color[None, None, :], axis=2)
bg_mask = dist < 30  # tweak if needed

# 3) Connected components to locate stickers
content_mask = (~bg_mask).astype(np.uint8)
num_labels, labels = cv2.connectedComponents(content_mask)

# 4) Gather sticker bboxes
components = []
for label in range(1, num_labels):
    ys, xs = np.where(labels == label)
    if not ys.size:
        continue
    size = ys.size
    x0, y0 = xs.min(), ys.min()
    x1, y1 = xs.max()+1, ys.max()+1
    components.append((label, size, (x0, y0, x1, y1)))

# 5) Take top 9 and sort in reading order
components = sorted(components, key=lambda x: x[1], reverse=True)[:9]
components.sort(key=lambda c: (c[2][1], c[2][0]))

# 6) Crop & only remove the “edge‑connected” grey
for idx, (_, _, (x0, y0, x1, y1)) in enumerate(components):
    crop = pil_img.crop((x0, y0, x1, y1)).convert('RGBA')
    crop_arr = np.array(crop)

    # a) extract the grey mask for this crop
    mask_crop = bg_mask[y0:y1, x0:x1].astype(np.uint8)

    # b) label connected regions in that mask
    num_lbls, lbls = cv2.connectedComponents(mask_crop, connectivity=8)

    # c) find which labels touch the border of this crop
    edge_labels = set()
    edge_labels.update(np.unique(lbls[0, :]))    # top row
    edge_labels.update(np.unique(lbls[-1, :]))   # bottom row
    edge_labels.update(np.unique(lbls[:, 0]))    # left col
    edge_labels.update(np.unique(lbls[:, -1]))   # right col
    edge_labels.discard(0)  # 0 == non-grey

    # d) build final transparency mask: only those grey pixels in edge_labels
    edge_mask = np.isin(lbls, list(edge_labels))

    # e) zero out alpha on just that edge‑mask
    crop_arr[edge_mask, 3] = 0

    # f) save
    row, col = divmod(idx, COLS)
    out = Image.fromarray(crop_arr, mode='RGBA')
    out.save(os.path.join(OUTPUT_DIR, f'sticker_{row}_{col}.png'))

print(f"Saved 9 transparent stickers (only true bg removed) to: {OUTPUT_DIR}")
