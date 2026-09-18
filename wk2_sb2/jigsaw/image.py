import numpy as np
import cv2
import typing

class Image:
  def __init__(self, mat: cv2.typing.MatLike):
    self.mat = mat
    self.size = (int(mat.shape[1]), int(mat.shape[0]))

    self.kp: typing.Sequence[cv2.KeyPoint] | None = None
    self.des: cv2.typing.MatLike | None = None

    self.T = np.identity(3) # image -> world
    self._world_pop = False
    self.world_mat: cv2.typing.MatLike | None = None
    self.world_corner: tuple[int, int] | None = None
    self.world_size: tuple[int, int] | None = None

  def depopulate_world(self):
    self._world_pop = False
    self.world_mat = None
    self.world_corner = None
    self.world_size = None

  def populate_world(self):
    if self._world_pop:
      return
    self._world_pop = True

    # image corners
    corners = np.array([[0, 0], [1, 0], [0, 1], [1, 1]]) * self.size
    corners = np.hstack([corners, [[1], [1], [1], [1]]])
    # world corners
    world_corners = self.T @ corners.T
    world_corners = world_corners.T[:, :2]

    x = world_corners[:, 0]
    y = world_corners[:, 1]
    min_x = int(np.floor(np.min(x)))
    max_x = int(np.ceil(np.max(x)))
    min_y = int(np.floor(np.min(y)))
    max_y = int(np.ceil(np.max(y)))
    self.world_corner = (min_x, min_y)
    self.world_size = (max_x - min_x, max_y - min_y)

    # image to world
    M = self.T[:2, :].copy()
    M[0, 2] -= min_x
    M[1, 2] -= min_y
    # world to image
    M_inv = cv2.invertAffineTransform(M)
    self.world_mat = cv2.resize(self.mat, self.world_size) # cv2.warpAffine(self.mat, M_inv, self.world_size)


__all__ = ["Image"]
