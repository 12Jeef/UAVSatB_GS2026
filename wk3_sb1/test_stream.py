import cv2
from detect import *

colors = [
  Color.RED,
  Color.ORANGE,
  Color.YELLOW,
  Color.GREEN,
  Color.CYAN,
  Color.BLUE,
  Color.PURPLE,
  Color.MAGENTA,
  Color.BLACK,
  Color.GRAY,
  Color.WHITE,
]
colors_bgr = [color.bgr() for color in colors]

color_i = 0

cap = cv2.VideoCapture(0)

while True:
  key = cv2.waitKey(1) & 0xFF
  if key == ord("q"):
    break
  if key == 2: # left
    color_i -= 1
  if key == 3: # right
    color_i += 1
  color_i %= len(colors)
  ret, frame = cap.read()
  if not ret:
    break

  mask, contours = detect(frame, colors[color_i])

  bgr = colors_bgr[color_i]
  frame[:60, :60] = bgr
  # bgr = (0, 0, 255)
  cv2.drawContours(frame, contours, -1, bgr, thickness=1)
  frame[mask > 0] = frame[mask > 0] * 0.5 + (bgr[0] * 0.5, bgr[1] * 0.5, bgr[2] * 0.5)

  cv2.imshow("video", frame)

cap.release()
cv2.destroyAllWindows()
