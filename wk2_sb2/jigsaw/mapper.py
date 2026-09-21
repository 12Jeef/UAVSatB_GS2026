import math
import numpy as np
import cv2
from .image import Feature, Image

verbose = True

def set_verbose(vb):
  global verbose
  verbose = vb

def log(*a, **kwa):
  if not verbose:
    return
  print(*a, **kwa)

class Match:
  def __init__(self, feat_a: Feature, feat_b: Feature, match: cv2.DMatch):
    self.feat_a = feat_a
    self.feat_b = feat_b
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
    log(f"Mapper: detect")
    kps, dess = self.orb.detectAndCompute(img.mat, None)
    img.feats = [
      Feature(img, des.tolist(), (float(kp.pt[0]), float(kp.pt[1])))
      for kp, des in zip(kps, list(dess))]
    return img

  def match(self, img_a: Image, img_b: Image) -> Matches:
    log(f"Mapper: match")
    if img_a.feats is None:
      log(f"Mapper: match: img_a not populated")
      self.detect(img_a)
    if img_b.feats is None:
      log(f"Mapper: match: img_b not populated")
      self.detect(img_b)
    if img_a.feats is None:
      log(f"Mapper: match: ! img_a.feats is None")
      raise ValueError("Image A does not have features")
    if img_b.feats is None:
      log(f"Mapper: match: ! img_b.feats is None")
      raise ValueError("Image B does not have features")
    all_matches = self.matcher.knnMatch(
      np.array([feat.des for feat in img_a.feats], dtype=np.uint8),
      np.array([feat.des for feat in img_b.feats], dtype=np.uint8),
      k=2)
    good_matches: list[Match] = []
    for m, n in all_matches:
      if m.distance < self.lowe_ratio * n.distance:
        good_matches.append(Match(img_a.feats[m.queryIdx], img_b.feats[m.trainIdx], m))
    log(f"Mapper: match: found {len(good_matches)} good of {len(all_matches)} all")
    return Matches(img_a, img_b, good_matches)

  def align(self, matchess: list[Matches]) -> tuple[cv2.typing.MatLike, float] | None:
    log(f"Mapper: align")
    if len(matchess) <= 0:
      log(f"Mapper: align: ! no matches")
      raise ValueError("No matches provided")
    for matches in matchess:
      if matches.img_b != matchess[0].img_b:
        log(f"Mapper: align: ! inconsistent img_b")
        raise ValueError("Inconsistent image B")
    a_poss: list[tuple[float, float]] = []
    b_poss: list[tuple[float, float]] = []
    for matches in matchess:
      for m in matches.matches:
        if m.feat_a.world_pos is None:
          log(f"Mapper: align: ! world_pos is None")
          raise ValueError("Feature A does not have a world position")
        a_poss.append(m.feat_a.world_pos)
      b_poss.extend([m.feat_b.pos for m in matches.matches])
    if len(a_poss) <= self.min_n_feats:
      log(f"Mapper: align: ! not enough feats")
      return None
    M, mask = cv2.estimateAffinePartial2D(
      np.array(a_poss),
      np.array(b_poss),
      method=cv2.RANSAC,
      ransacReprojThreshold=25) # a onto b
    if M is None:
      log(f"Mapper: align: ! RANSAC failed")
      return None
    score = int(mask.sum()) / len(a_poss)
    if score < self.min_score:
      log(f"Mapper: align: ! RANSAC bad ({score} < {self.min_score})")
      return None
    scale = np.sqrt(M[0, 0]**2 + M[1, 0]**2)
    if scale < self.min_scale or scale > self.max_scale:
      log(f"Mapper: align: ! transform bad ({scale} < {self.min_scale} or > {self.max_scale})")
      return None
    M_inv = cv2.invertAffineTransform(M) # b onto a
    T = np.vstack([M_inv, [0, 0, 1]])
    return T, score

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
    for cx in range(mn[0], mx[0] + 1, 1):
      for cy in range(mn[1], mx[1] + 1, 1):
        self.add_chunk(cx, cy)
        chunk_poss.append((cx, cy))
    return chunk_poss

  def add_image_to(self, img: Image, chunk_pos: tuple[int, int]):
    img.populate_world()
    if img.world_mat is None:
      raise ValueError("Image has no world matrix")
    if img.world_mat_mask is None:
      raise ValueError("Image has no world matrix mask")
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
    src = img.world_mat[src_min_y:src_max_y, src_min_x:src_max_x]
    mask = img.world_mat_mask[src_min_y:src_max_y, src_min_x:src_max_x]
    dst = chunk[dst_min_y:dst_max_y, dst_min_x:dst_max_x]
    i = mask >= 128
    dst[i] = dst[i] / 2 + src[i] / 2

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

  def align_and_add_image(self, img: Image):
    self.mapper.detect(img)
    log(f"Map: align_and_add_image")
    if len(self.images) <= 0:
      log(f"Map: align_and_add_image: no images, add straight")
      self.add_image(img)
      return True
    latest = reversed(self.images[:5])
    matchess = [self.mapper.match(img_base, img) for img_base in latest]
    results = self.mapper.align(matchess)
    if results is None:
      log(f"Map: align_and_add_image: ! failed")
      return False
    T, _ = results
    img.T = T
    img.depopulate_world()
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
          # Find pixels that aren't completely black
    nonzero = np.any(img != 0, axis=2)
    if not np.any(nonzero):
      return img
    ys, xs = np.where(nonzero)
    min_x = xs.min()
    max_x = xs.max()
    min_y = ys.min()
    max_y = ys.max()
    return img[min_y:max_y + 1, min_x:max_x + 1]

__all__ = ["set_verbose", "Match", "Matches", "Mapper", "Map"]