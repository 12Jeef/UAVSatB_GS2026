import argparse
import os
import cv2

H_BINS = ["red", "yellow", "green", "cyan", "blue", "magenta"]
SHADE_S_THRESH = 64
BLACK_V_THRESH = 64
WHITE_V_THRESH = 224

parser = argparse.ArgumentParser(description="Split images by color")
parser.add_argument("filepaths", nargs="*", default=[], help="List of file paths")
parser.add_argument("-o", default=None, help="Output directory (default: current directory)")

args = parser.parse_args()
filepaths = args.filepaths
output_dir = args.o

def process_img(path):
  img = cv2.imread(path)
  if img is None:
    return
  hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
  hsv[:, :, 0] = (hsv[:, :, 0] + int(180 / len(H_BINS) / 2)) % 180 # shift to center distr
  mask_ranges = [
    # black: any hue, any saturation, low value
    ("black", (0, 0, 0), (180, 255, BLACK_V_THRESH - 1)),
    # gray: any hue, low saturation, medium value
    ("gray", (0, 0, BLACK_V_THRESH), (180, SHADE_S_THRESH - 1, WHITE_V_THRESH - 1)),
    # white: any hue, low saturation, high value
    ("white", (0, 0, WHITE_V_THRESH), (180, SHADE_S_THRESH - 1, 255)),
  ]
  for h_i, bin in enumerate(H_BINS):
    h_min = int(h_i / len(H_BINS) * 180)
    h_max = int((h_i + 1) / len(H_BINS) * 180)
    # color: select hue, high saturation, medium-to-high value
    mask_ranges.append((bin, (h_min, SHADE_S_THRESH, BLACK_V_THRESH), (h_max, 255, 255)))
  for label, mn, mx in mask_ranges:
    mask = cv2.inRange(hsv, mn, mx)
    if cv2.countNonZero(mask) < hsv.shape[0] * hsv.shape[1] * 0.01:
      continue
    out = cv2.bitwise_and(img, img, mask=mask)
    if output_dir is None:
      out_path = f"{os.path.splitext(path)[0]}_{label}.png"
    else:
      out_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(path))[0]}_{label}.png")
    cv2.imwrite(out_path, out)

for path in filepaths:
  process_img(os.path.join(os.getcwd(), path))
