import os
import cv2

dirpath = os.path.dirname(os.path.abspath(__file__))
filepath = os.path.join(dirpath, "img.png")

img = cv2.imread(filepath)
if img is None:
    exit()

img_zerog = img.copy()
img_zerog[:, :, 1] = 0
cv2.imwrite(os.path.join(dirpath, "img_zerog.png"), img_zerog)

img_stretch = cv2.resize(img, (int(img.shape[1] * 2), int(img.shape[0] * 1)))
cv2.imwrite(os.path.join(dirpath, "img_stretch.png"), img_stretch)

img_shuffle = img.copy()
img_r = img_shuffle[:, :, 2].copy()
img_g = img_shuffle[:, :, 1].copy()
img_b = img_shuffle[:, :, 0].copy()
img_shuffle[:, :, 0] = img_r
img_shuffle[:, :, 2] = img_b
img_shuffle[:, :, 1] = img_g
cv2.imwrite(os.path.join(dirpath, "img_shuffle.png"), img_shuffle)
