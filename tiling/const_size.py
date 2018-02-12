# # -*- coding:utf-8 -*-
# from __future__ import absolute_import
#
# # Python
# import logging
#
# # Numpy
# import numpy as np
#
#
# logger = logging.getLogger('tiling')
#
# from . import BaseTiles
#
#
# class ConstSizeTiles(BaseTiles):
#     """
#     Class provides constant size tile parameters (offset, extent) to extract data from image.
#     Generated tile extents can overlap, do not includes nodata paddings.
#
#     For example, tiling can look like this:
#     ```
#       tile 0      tile 2      tile 4
#     |<------>|  |<------>|  |<------>|
#             tile 1      tile 3      tile 5
#           |<------>|  |<------>|  |<------>|
#     |<------------------------------------>|
#     |                IMAGE                 |
#     |                                      |
#     ```
#
#     Usage:
#     ```
#     from tiling import ConstSizeTiles
#
#     tiles = ConstSizeTiles(image_size=(500, 500), tile_size=(256, 256), min_overlapping=100)
#
#     print("Number of tiles: %i" % len(tiles))
#     for x, y, width, height in tiles:
#         data = read_data(x, y, width, height, tiles.tile_size[0], tiles.tile_size[0])
#         print("data.shape: {}".format(data.shape))
#
#     ```
#     """
#
#     def __init__(self, image_size, tile_size, min_overlapping=0, scale=1.0):
#         """
#         Initialize tiles
#         :param image_size: (list or tuple of int) input image size in pixels (width, height)
#         :param tile_size: (list or tuple of int) output tile size in pixels (width, height)
#         :param min_overlapping: (int) minimal overlapping in pixels. Actual overlapping between tiles will not be
#         constant, minimal overlapping value is the minimum boundary value.
#         :param scale: (float) Scaling applied to the input image parameters before extracting tile's extent
#         """
#         super(ConstSizeTiles, self).__init__(image_size=image_size, tile_size=tile_size, scale=scale)
#         assert 0 <= min_overlapping < min(self.tile_extent[0], self.tile_extent[1]), \
#             "minimal overlapping should be between 0 and min tile_extent = tile_size / scale"
#
#         self.min_overlapping = min_overlapping
#         # Compute number of tiles as if tile extent is floor(float_tile_extent)
#         self.nx = ConstSizeTiles._compute_number_of_tiles(self.tile_extent[0], self.image_size[0], min_overlapping)
#
#         assert self.nx > 0, \
#             "Something wrong with input parameters: {}, {}, {}".format(
#                 self.tile_extent[0], self.image_size[0], min_overlapping)
#
#         self.ny = ConstSizeTiles._compute_number_of_tiles(self.tile_extent[1], self.image_size[1], min_overlapping)
#         assert self.nx > 0, \
#             "Something wrong with input parameters: {}, {}, {}".format(
#                 self.tile_extent[0], self.image_size[0], min_overlapping)
#
#         self.float_overlapping_x = ConstSizeTiles._compute_float_overlapping(self.float_tile_extent[0],
#                                                                              self.image_size[0], self.nx)
#         self.float_overlapping_y = ConstSizeTiles._compute_float_overlapping(self.float_tile_extent[1],
#                                                                              self.image_size[1], self.ny)
#         self._max_index = self.nx * self.ny
#
#     def __len__(self):
#         """
#         Method to get total number of tiles
#         :return:
#         """
#         return self._max_index
#
#     @staticmethod
#     def _compute_tile_params(idx, tile_extent, overlapping):
#         """
#         Method to compute tile params: offset, extent and output size for a given index
#
#         tile offset is
#
#         :param idx: (int) input tile index
#         :param tile_extent: (float) tile float extent
#         :param overlapping: (float) overlapping
#         :param scale: (float) scale
#         :return: tuple integer offset, integer extent and output size in pixels
#         """
#         offset = int(np.round(idx * (tile_extent - overlapping)))
#         return offset, int(np.round(tile_extent))
#
#     def __getitem__(self, idx):
#         """
#         Method to get the tile at index `idx`
#         :param idx: (int) tile index between `0` and `len(tiles)`
#         :return: (tuple) tile extent in pixels: x offset, y offset, x tile extent, y tile extent
#         If scale is 1.0, then x tile extent, y tile extent are equal to tile size
#         """
#         if idx < 0 or idx >= self._max_index:
#             raise IndexError("Index %i is out of ranges %i and %i" % (idx, 0, self._max_index))
#
#         x_tile_index = idx % self.nx
#         y_tile_index = int(idx * 1.0 / self.nx)
#
#         x_tile_offset, x_tile_extent = self._compute_tile_params(x_tile_index, self.tile_extent[0],
#                                                                  self.float_overlapping_x)
#         y_tile_offset, y_tile_extent = self._compute_tile_params(y_tile_index, self.tile_extent[1],
#                                                                  self.float_overlapping_y)
#         return x_tile_offset, y_tile_offset, x_tile_extent, y_tile_extent
#
#     @staticmethod
#     def _compute_number_of_tiles(tile_extent, image_size, min_overlapping):
#         """
#         Method to compute number of overlapping tiles for a given image size
#         n = ceil(image_size / (tile_size - min_overlapping))
#         """
#         return ceil_int(image_size * 1.0 / (tile_extent - min_overlapping))
#
#     @staticmethod
#     def _compute_float_overlapping(tile_size, image_size, n):
#         """
#         Method to float overlapping
#
#         delta = tile_size * n - image_size
#         overlapping = delta / (n - 1)
#         """
#         return (tile_size * n - image_size) * 1.0 / (n - 1.0) if n > 1 else 0
#
#
# def ceil_int(x):
#     return int(np.ceil(x))
