import typing
import enum
import numpy as np
import cv2

SHADE_S_THRESH = 64
BLACK_V_THRESH = 64
WHITE_V_THRESH = 224

def hsv_to_bgr(hsv: tuple[int, int, int]):
  bgr_array = cv2.cvtColor(np.array([[hsv]], dtype=np.uint8), cv2.COLOR_HSV2BGR)
  b, g, r = bgr_array[0, 0]
  return int(b), int(g), int(r)

class Color(enum.Enum):
  RED = 0
  ORANGE = 30
  YELLOW = 60
  GREEN = 120
  CYAN = 180
  BLUE = 240
  PURPLE = 270
  MAGENTA = 300
  BLACK = -1
  GRAY = -2
  WHITE = -3

  def bgr(self):
    if self.value >= 0:
      return hsv_to_bgr((int(self.value / 360 * 180), 255, 255))
    return [(0, 0, 0), (128, 128, 128), (255, 255, 255)][abs(self.value) - 1]

COLORS_H = [
  Color.RED,
  Color.ORANGE,
  Color.YELLOW,
  Color.GREEN,
  Color.CYAN,
  Color.BLUE,
  Color.PURPLE,
  Color.MAGENTA,
]

def angle_rel(a: int, b: int) -> int:
  rel = (b - a) % 360
  if rel > 180:
    rel -= 360
  return rel

def get_h_range(color: Color) -> tuple[int, int]:
  if color not in COLORS_H:
    return (0, 0)
  i = COLORS_H.index(color)
  prv = COLORS_H[(i - 1) % len(COLORS_H)]
  nxt = COLORS_H[(i + 1) % len(COLORS_H)]
  return (
    int(color.value + 0.5 * angle_rel(color.value, prv.value)) % 360,
    int(color.value + 0.5 * angle_rel(color.value, nxt.value)) % 360,
  )

class Filter:
  def __init__(
      self, *,
      h: None | int | tuple[int, int] | list[tuple[int, int]],
      s: None | int | tuple[int, int],
      v: None | int | tuple[int, int],
      name: str | None = None,
    ):
    if h is None:
      self.h = [(0, 360)]
      self._hrepr = 0
    elif isinstance(h, int):
      self._hrepr = h
      h_min = (h - 30) % 360
      h_max = (h + 30) % 360
      if h_min < h_max:
        self.h = [(h_min, h_max)]
      else:
        self.h = [(0, h_max), (h_min, 360)]
    elif isinstance(h, tuple):
      self.h = [h]
      self._hrepr = int(sum(h) / len(h))
    else:
      self.h = h
      self._hrepr = int(sum(h[0]) / len(h[0])) if len(h) > 0 else 0
    if s is None:
      self.s = (0, 255)
    elif isinstance(s, int):
      self.s = (max(0, s - 32), min(255, s + 32))
    else:
      self.s = s
    if v is None:
      self.v = (0, 255)
    elif isinstance(v, int):
      self.v = (max(0, v - 32), min(255, v + 32))
    else:
      self.v = v
    self._bgr = hsv_to_bgr((int(self._hrepr / 360 * 180), int(max(self.s)), int(max(self.v))))
    self.name = name if name else "?"

  def bgr(self):
    return self._bgr

def detect(frame: cv2.typing.MatLike, color: Color | Filter, *, erode=5, dilate=5) -> tuple[cv2.typing.MatLike, typing.Sequence[cv2.typing.MatLike]]:
  hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
  h_ranges: list[tuple[int, int]] = []
  s_range: tuple[int, int] = (0, 0)
  v_range: tuple[int, int] = (0, 0)
  if color == Color.BLACK:
    h_ranges.append((0, 360))
    s_range = (0, 255)
    v_range = (0, BLACK_V_THRESH)
  elif color == Color.GRAY:
    h_ranges.append((0, 360))
    s_range = (0, SHADE_S_THRESH)
    v_range = (BLACK_V_THRESH, WHITE_V_THRESH)
  elif color == Color.WHITE:
    h_ranges.append((0, 360))
    s_range = (0, SHADE_S_THRESH)
    v_range = (WHITE_V_THRESH, 255)
  elif isinstance(color, Color):
    start, stop = get_h_range(color)
    if stop > start:
      h_ranges.append((start, stop))
    else:
      h_ranges.extend([(0, stop), (start, 360)])
    s_range = (SHADE_S_THRESH, 255)
    v_range = (BLACK_V_THRESH, 255)
  else:
    h_ranges = color.h
    s_range = color.s
    v_range = color.s
  h_ranges = [(int(start / 360 * 180), int(stop / 360 * 180)) for start, stop in h_ranges]
  s_min, s_max = s_range
  v_min, v_max = v_range
  mask: cv2.typing.MatLike | None = None
  for h_range in h_ranges:
    h_min, h_max = h_range
    mask2 = cv2.inRange(hsv, (h_min, s_min, v_min), (h_max, s_max, v_max))
    if mask is None:
      mask = mask2
    else:
      mask = cv2.bitwise_or(mask, mask2)
  if mask is None:
    raise Exception("Good job, you broke something")
  mask = cv2.erode(mask, None, iterations=erode, dst=mask) # type: ignore
  mask = cv2.dilate(mask, None, iterations=dilate, dst=mask) # type: ignore
  contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # type: ignore
  return mask, contours # type: ignore

__all__ = ["Color", "Filter", "detect"]
