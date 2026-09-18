import math
import numpy as np
import cv2
from .image import Image

class Match:
  def __init__(self, kp_a: cv2.KeyPoint, kp_b: cv2.KeyPoint, match: cv2.DMatch):
    self.kp_a = kp_a
    self.kp_b = kp_b
    self.match = match

class Matches:
  def __init__(self, img_a: Image, img_b: Image, matches: list[Match]):
    self.img_a = img_a
    self.img_b = img_b
    self.matches = matches

class Mapper:
  def __init__(self, *, n_feats=2000, lowe_ratio=0.75, min_n_feats=5, min_score=0.75, min_scale=0.25, max_scale=1.75):
    self.orb = cv2.ORB.create(nfeatures=n_feats)
    self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING)

    self.lowe_ratio = lowe_ratio
    self.min_n_feats = min_n_feats
    self.min_score = min_score
    self.min_scale = min_scale
    self.max_scale = max_scale

  def detect(self, img: Image) -> Image:
    img.kp, img.des = self.orb.detectAndCompute(img.mat, None)
    return img

  def match(self, img_a: Image, img_b: Image) -> Matches:
    if img_a.kp is None or img_a.des is None:
      self.detect(img_a)
    if img_b.kp is None or img_b.des is None:
      self.detect(img_b)
    if img_a.kp is None:
      raise ValueError("Image A does not have key points")
    if img_a.des is None:
      raise ValueError("Image A does not have descriptors")
    if img_b.kp is None:
      raise ValueError("Image B does not have key points")
    if img_b.des is None:
      raise ValueError("Image B does not have descriptors")
    all_matches = self.matcher.knnMatch(img_a.des, img_b.des, k=2)
    good_matches: list[Match] = []
    for m, n in all_matches:
      if m.distance < self.lowe_ratio * n.distance:
        good_matches.append(Match(img_a.kp[m.queryIdx], img_b.kp[m.trainIdx], m))
    return Matches(img_a, img_b, good_matches)

  def transform_b_onto_a(self, matches: Matches) -> tuple[cv2.typing.MatLike, float] | None:
    if len(matches.matches) < self.min_n_feats:
      return None
    M, mask = cv2.estimateAffinePartial2D(
      np.array([m.kp_a.pt for m in matches.matches]),
      np.array([m.kp_b.pt for m in matches.matches]),
      method=cv2.RANSAC,
      ransacReprojThreshold=5) # a onto b
    if M is None:
      return None
    score = int(mask.sum()) / len(matches.matches)
    if score < self.min_score:
      return None
    scale = np.sqrt(M[0, 0]**2 + M[1, 0]**2)
    if scale < self.min_scale or scale > self.max_scale:
      return None
    M_inv = cv2.invertAffineTransform(M) # b onto a
    T = np.vstack([M_inv, [0, 0, 1]])
    return T, score

  def apply_b_onto_a(self, img_a: Image, img_b: Image, *, T_cache: cv2.typing.MatLike | None = None) -> Image | None:
    if T_cache is None:
      results = self.transform_b_onto_a(self.match(img_a, img_b))
      if results is None:
        return None
      T = results[0] # b onto a
    else:
      T = T_cache # b onto a
    img_b.T = img_a.T @ T # (a onto world) x (b onto a)
    img_b.depopulate_world()
    return img_b

class Map:
  def __init__(self, mapper: Mapper, *, chunk_size: int):
    self.mapper = mapper
    self.chunk_size = int(chunk_size)
    self.chunks: dict[tuple[int, int], cv2.typing.MatLike] = {}
    self.images: list[Image] = []

  def add_chunk(self, cx: int, cy: int):
    if (cx, cy) not in self.chunks:
      self.chunks[(cx, cy)] = np.zeros((self.chunk_size, self.chunk_size, 3), dtype=np.uint8)
    return self.chunks[(cx, cy)]

  def add_chunks(self, corner: tuple[int, int], size: tuple[int, int]):
    mn = (math.floor(corner[0] / self.chunk_size), math.floor(corner[1] / self.chunk_size))
    mx = (math.ceil((corner[0] + size[0]) / self.chunk_size), math.ceil((corner[1] + size[1]) / self.chunk_size))
    chunk_poss: list[tuple[int, int]] = []
    for cx in range(mn[0], mx[0], 1):
      for cy in range(mn[1], mx[1], 1):
        self.add_chunk(cx, cy)
        chunk_poss.append((cx, cy))
    return chunk_poss

  def add_image_to(self, img: Image, chunk_pos: tuple[int, int]):
    img.populate_world()
    if img.world_mat is None:
      raise ValueError("Image has no world matrix")
    if img.world_corner is None:
      raise ValueError("Image has no world corner")
    if img.world_size is None:
      raise ValueError("Image has no world size")
    cx, cy = chunk_pos
    chunk = self.add_chunk(cx, cy)
    chunk_world_x = cx * self.chunk_size
    chunk_world_y = cy * self.chunk_size
    chunk_max_world_x = chunk_world_x + self.chunk_size
    chunk_max_world_y = chunk_world_y + self.chunk_size
    img_max_world_x = img.world_corner[0] + img.world_size[0]
    img_max_world_y = img.world_corner[1] + img.world_size[1]
    src_min_x = max(chunk_world_x - img.world_corner[0], 0)
    src_min_y = max(chunk_world_y - img.world_corner[1], 0)
    src_max_x = min(chunk_max_world_x - img.world_corner[0], img.world_size[0])
    src_max_y = min(chunk_max_world_y - img.world_corner[1], img.world_size[1])
    dst_min_x = max(img.world_corner[0] - chunk_world_x, 0)
    dst_min_y = max(img.world_corner[1] - chunk_world_y, 0)
    dst_max_x = min(img_max_world_x - chunk_world_x, self.chunk_size)
    dst_max_y = min(img_max_world_y - chunk_world_y, self.chunk_size)
    if src_min_x >= src_max_x:
      return
    if src_min_y >= src_max_y:
      return
    chunk[dst_min_y:dst_max_y, dst_min_x:dst_max_x, :] = img.world_mat[src_min_y:src_max_y, src_min_x:src_max_x, :]

  def add_image(self, img: Image):
    img.populate_world()
    if img.world_mat is None:
      raise ValueError("Image has no world matrix")
    if img.world_corner is None:
      raise ValueError("Image has no world corner")
    if img.world_size is None:
      raise ValueError("Image has no world size")
    self.images.append(img)
    chunk_poss = self.add_chunks(img.world_corner, img.world_size)
    for chunk_pos in chunk_poss:
      self.add_image_to(img, chunk_pos)

  def map_and_add_image(self, img: Image):
    if len(self.images) <= 0:
      self.add_image(img)
      return True
    latest = reversed(self.images[:5])
    latest_scored = [(img_src, self.mapper.transform_b_onto_a(self.mapper.match(img_src, img))) for img_src in latest]
    latest_scored = [(img_src, results) for img_src, results in latest_scored if results is not None]
    if len(latest_scored) <= 0:
      return False
    latest_scored.sort(key=lambda item: item[1][1], reverse=True) # (img, (T, score)) -> greatest score
    img_src, (T, _) = latest_scored[0]
    self.mapper.apply_b_onto_a(img_src, img, T_cache=T)
    self.add_image(img)
    return True

  def combine(self) -> cv2.typing.MatLike:
    chunk_poss = list(self.chunks.keys())
    cx = [cx for cx, _ in chunk_poss]
    cy = [cy for _, cy in chunk_poss]
    min_cx = min(cx)
    max_cx = max(cx)
    min_cy = min(cy)
    max_cy = max(cy)
    img = np.zeros(((max_cy - min_cy + 1) * self.chunk_size, (max_cx - min_cx + 1) * self.chunk_size, 3), dtype=np.uint8)
    for (cx, cy), mat in self.chunks.items():
      cx -= min_cx
      cy -= min_cy
      chunk_world_x = cx * self.chunk_size
      chunk_world_y = cy * self.chunk_size
      chunk_max_world_x = chunk_world_x + self.chunk_size
      chunk_max_world_y = chunk_world_y + self.chunk_size
      img[chunk_world_y:chunk_max_world_y, chunk_world_x:chunk_max_world_x, :] = mat
    return img

__all__ = ["Match", "Matches", "Mapper", "Map"]