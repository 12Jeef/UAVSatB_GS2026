import typing
import numpy as np
import cv2
from detect import *

def draw_box(img: cv2.typing.MatLike, color: tuple[int, int, int], label: str, box: tuple[tuple[int, int], tuple[int, int]]):
  mn, mx = box
  x, y = mn
  cv2.rectangle(img, mn, mx, color, 2)
  cv2.putText(img, label, (x, y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)

def draw_contour(img: cv2.typing.MatLike, color: tuple[int, int, int], label: str, contour: cv2.typing.MatLike):
  xs = contour[:, 0, 0]
  ys = contour[:, 0, 1]
  draw_box(img, color, label, ((int(xs.min()), int(ys.min())), (int(xs.max()), int(ys.max()))))
  cv2.drawContours(img, [contour], 0, color, 2)

def test_objects():
  img = cv2.imread("objects.jpg")
  if img is None:
    return

  CUBE_COLOR = Filter(h=(240, 300), s=(64, 255), v=(64, 255))
  CONE_COLOR = Filter(h=(20, 60), s=(128, 255), v=(64, 255))
  NOTE_COLOR = Filter(h=[(0, 20), (330, 360)], s=(64, 255), v=(64, 255))

  _, cubes = detect(img, CUBE_COLOR, erode=15, dilate=15)
  _, cones = detect(img, CONE_COLOR, erode=5, dilate=5)
  _, notes = detect(img, NOTE_COLOR, erode=5, dilate=5)

  for cube in cubes:
    draw_contour(img, CUBE_COLOR.bgr(), "cube", cube)
  for cone in cones:
    draw_contour(img, CONE_COLOR.bgr(), "cone", cone)
  for note in notes:
    area = cv2.contourArea(note)
    perim = cv2.arcLength(note, True)
    score = 4 * np.pi * area / perim / perim
    if score < 0.5:
      continue
    draw_contour(img, NOTE_COLOR.bgr(), "note", note)

  cv2.imwrite("objects_detected.png", img)

def test_polka_dots_1():
  img = cv2.imread("polka_dots_1.png")
  if img is None:
    return

  colors: list[Color] = [Color.ORANGE, Color.YELLOW, Color.GREEN, Color.CYAN]
  contour_sets: list[typing.Sequence[cv2.typing.MatLike]] = []
  for color in colors:
    _, contours = detect(img, color)
    contour_sets.append(contours)
  for color, contours in zip(colors, contour_sets):
    for contour in contours:
      area = cv2.contourArea(contour)
      perim = cv2.arcLength(contour, True)
      score = 4 * np.pi * area / perim / perim
      if score < 0.75:
        continue
      draw_contour(img, color.bgr(), color.name, contour)

  cv2.imwrite("polka_dots_1_detected.png", img)


def test_polka_dots_2():
  img = cv2.imread("polka_dots_2.jpg")
  if img is None:
    return
  img_blur = cv2.GaussianBlur(img, (25, 25), 0)

  colors: list[Color | Filter] = [
    Filter(h=[(0, 15), (330, 360)], s=(64, 255), v=(0, 224), name="DARK_RED"),
    Filter(h=(80, 150), s=(0, 255), v=(64, 255), name="MINT"),
    Color.CYAN,
    Filter(h=270, s=(0, 255), v=(0, 128), name="DARK_PURPLE"),
    Filter(h=(285, 350), s=(0, 255), v=(128, 255), name="PINK"),
  ]
  contour_sets: list[typing.Sequence[cv2.typing.MatLike]] = []
  for color in colors:
    _, contours = detect(img_blur, color)
    contour_sets.append(contours)
  for color, contours in zip(colors, contour_sets):
    for contour in contours:
      area = cv2.contourArea(contour)
      perim = cv2.arcLength(contour, True)
      score = 4 * np.pi * area / perim / perim
      if score < 0.75:
        continue
      draw_contour(img, color.bgr(), color.name, contour)

  cv2.imwrite("polka_dots_2_detected.png", img)


test_objects()
test_polka_dots_1()
test_polka_dots_2()

# the rest i just dont wanna do cuz im lazy, sorry :/
