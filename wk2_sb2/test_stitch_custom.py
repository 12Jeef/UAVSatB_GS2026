import os
import time
import cv2
import jigsaw

dirpath = os.path.dirname(os.path.abspath(__file__))

def split_video(input_file: str, output_dir: str, period: float):
  os.makedirs(output_dir, exist_ok=True)
  cap = cv2.VideoCapture(input_file)
  fps = cap.get(cv2.CAP_PROP_FPS)
  frame_period = int(fps * period)
  frame_idx = 0
  output_idx = 0
  while True:
    ret, frame = cap.read()
    if not ret:
      break
    if frame_idx % frame_period == 0:
      output_file = os.path.join(output_dir, f"frame_{output_idx:05d}.png")
      cv2.imwrite(output_file, frame)
      output_idx += 1
    frame_idx += 1
  cap.release()

if True:
  # IMAGES_PATH = os.path.join(dirpath, "tmp", "mapping_test", "old test images", "1")
  IMAGES_PATH = os.path.join(dirpath, "tmp", "mapping_test", "old test images", "2")
else:
  IMAGES_PATH = os.path.join(dirpath, "tmp", "Minecraft_stitch_test")
  # split_video(
  #   os.path.join(dirpath, "tmp", "Minecraft_stitch_test.mp4"),
  #   IMAGES_PATH,
  #   1)

IMAGES = [
  os.path.join(IMAGES_PATH, name)
  for name in os.listdir(IMAGES_PATH)
  if (name[0] == "(" or name.startswith("frame_")) and name.endswith(".png")]
IMAGES.sort()

mapper = jigsaw.Mapper(min_score=0, lowe_ratio=1)
map = jigsaw.Map(mapper, chunk_size=2000)

first = True
i = 0
while len(IMAGES) > 0:
  path = IMAGES.pop(0)
  name = os.path.basename(path)
  print(f"reading {name}...")
  img_mat = cv2.imread(path)
  if img_mat is None:
    print("> failed to read")
    continue
  img = jigsaw.Image(img_mat)
  print(f"map and add {name}...")
  t0 = time.time()
  success = map.align_and_add_image(img)
  t1 = time.time()
  print(f"> duration={(t1-t0) * 1000:.04}ms")
  if not success:
    print("> failed to map")
    IMAGES.append(path)
    continue
  cv2.imshow(f"map - added {name}", map.combine())
  if cv2.waitKey(0) & 0xFF == ord("q"):
    break
  cv2.destroyAllWindows()
