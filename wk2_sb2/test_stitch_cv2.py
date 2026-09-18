# this just sucks wtf
# single stitching just omits chunks cuz it cant find anything
# continuous stitching just fails instantly cuz it just cant find connections at all

import os
import cv2

dirpath = os.path.dirname(os.path.abspath(__file__))

IMAGES_PATH = os.path.join(dirpath, "tmp", "mapping_test", "old test images", "2")
IMAGES = [
  os.path.join(IMAGES_PATH, name)
  for name in os.listdir(IMAGES_PATH)
  if name[0] == "(" and name.endswith(".png")]
IMAGES.sort()

def prnt(fn):
  print("=" * 50)
  print(fn.__name__)
  print("=" * 50)

def test_stitcher_single():
  prnt(test_stitcher_single)
  imgs = [cv2.imread(path) for path in IMAGES]
  if any(img is None for img in imgs):
     return
  stitcher = cv2.Stitcher.create(cv2.Stitcher_SCANS)
  status, scan = stitcher.stitch(imgs)
  cv2.imwrite(os.path.join(dirpath, "tmp", "stitcher_single.png"), scan)
  if status == cv2.Stitcher_OK:
    print("success")
  else:
    print("error", status)

def test_stitcher_cont():
  prnt(test_stitcher_cont)
  imgs = [cv2.imread(path) for path in IMAGES]
  if any(img is None for img in imgs):
     return
  stitcher = cv2.Stitcher.create(cv2.Stitcher_SCANS)
  N_INITIAL = 4
  i = N_INITIAL
  status, scan = stitcher.stitch(imgs[:N_INITIAL])
  if status != cv2.Stitcher_OK:
    print("error_initial", status, 0)
    return
  for img in imgs[N_INITIAL:]:
    status, scan_new = stitcher.stitch([scan, img])
    if status != cv2.Stitcher_OK:
      cv2.imwrite(os.path.join(dirpath, "tmp", "stitcher_cont.png"), scan)
      print("error_cont", status, i)
      return
    i += 1
    scan = scan_new
  print("success", i)
  cv2.imwrite(os.path.join(dirpath, "tmp", "stitcher_cont.png"), scan)

test_stitcher_single()
test_stitcher_cont()
