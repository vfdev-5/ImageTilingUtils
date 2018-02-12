# -*- coding:utf-8 -*-
from __future__ import absolute_import

# Python
import logging

# Numpy
import numpy as np


logger = logging.getLogger('tiling')

from . import BaseTiles


class ConstStrideTiles(BaseTiles):
    """
    Class provides tile parameters (offset, extent) to extract data from image.
    Generated tile extents starts from an origin, has constant stride and can optionally include nodata paddings.

    For example, tiling can look like this (origin is negative, include nodata)
    ```
          tile 0        tile 2      tile 4
        |<------->|   |<------>|  |<------>|     etc
                  tile 1      tile 3      tile 5     tile n-1
        ^      |<------->|  |<------>|  |<------>| |<------>|
        |        |<------------------------------------>|
     origin      |                IMAGE                 |
                 |                                      |
    ```

    Another example, tiling can look like this (origin is negative, no nodata, tile size is not constant at boundaries)
    ```
                tile 0    tile 2      tile 4
                |<->|   |<------>|  |<------>|     etc
                  tile 1      tile 3      tile 5     tile n-1
        ^       |<------>|  |<------>|  |<------>| |<->|
        |       |<------------------------------------>|
     origin     |                IMAGE                 |
                |                                      |
    ```

    Another example, tiling can look like this (origin is postive, no nodata, tile size is not constant at boundaries)
    ```
          tile 0        tile 2
        |<------->|   |<------>|      etc
                  tile 1      tile 3      tile n-1
        ^      |<------->|  |<------>|  |<-->|
    |<-------------------------------------->|
    |   |            IMAGE                   |
    | origin                                 |
    ```

    Usage:
    ```
    from tiling import ConstStrideTiles

    tiles = ConstStrideTiles(image_size=(500, 500), tile_size=(256, 256), stride=(100, 100))

    print("Number of tiles: %i" % len(tiles))
    for x, y, width, height, out_width, out_height in tiles:
        data = read_data(x, y, width, height, out_width, out_height)
        print("data.shape: {}".format(data.shape))

    # Get a tile params at linear index:
    extent, out_size = tiles[len(tiles)//2]
    ```
    """
    def __init__(self, image_size, tile_size, stride=(1, 1), scale=1.0, origin=(0, 0), include_nodata=True):
        """
        Initialize tiles
        :param image_size: (list or tuple of int) input image size in pixels (width, height)
        :param tile_size: (list or tuple of int) output tile size in pixels (width, height)
        :param stride: (list or tuple of int) horizontal and vertical strides in pixels.
        Values need to be positive larger than 1 pixel. Stride value is impacted with scale and corresponds to a
        sliding over scaled image.
        :param scale: (float) Scaling applied to the input image parameters before extracting tile's extent
        :param origin: (list or tuple of int) point in pixels in the original image from where to start the tiling.
        Values can be positive or negative
        :param include_nodata: (bool) Inlcude or not nodata. If nodata is included than tile extents have all the
        same size, otherwise tiles at boundaries will be reduced
        """
        super(ConstStrideTiles, self).__init__(image_size=image_size, tile_size=tile_size, scale=scale)
        assert isinstance(stride, int) or (isinstance(stride, (tuple, list)) and len(stride) == 2), \
            "Argument stride should be a tuple/list (sx, sy)"
        if isinstance(stride, int):
            stride = (stride, stride)
        # Apply scale on the stride
        stride = [int(np.floor(s / self.scale)) for s in stride]
        for v in stride:
            assert v > 0, "Scaled stride values `floor(stride / scale)` should be larger than 1 pixel"

        self.stride = stride
        self.origin = origin
        self.include_nodata = include_nodata
        self.nx = ConstStrideTiles._compute_number_of_tiles(self.image_size[0], self.tile_extent[0],
                                                            self.origin[0], self.stride[0])
        self.ny = ConstStrideTiles._compute_number_of_tiles(self.image_size[1], self.tile_extent[1],
                                                            self.origin[1], self.stride[1])
        self._max_index = self.nx * self.ny

    def __len__(self):
        """
        Method to get total number of tiles
        :return:
        """
        return self._max_index

    @staticmethod
    def _compute_tile_extent(idx, tile_extent, stride, origin, image_size, include_nodata):
        """
        Method to compute tile extent: offset, extent for a given index
        """

        offset = idx * stride + origin
        if not include_nodata:
            extent = max(offset + tile_extent, 0) - max(offset, 0)
            extent = min(extent, image_size - offset)
            offset = max(offset, 0)
        else:
            extent = tile_extent
        return offset, extent

    @staticmethod
    def _compute_out_size(computed_extent, tile_extent, tile_size, scale):
        """
        Method to compute tile output size for a given computed extent.
        """
        if computed_extent < tile_extent:
            return int(np.ceil(np.float32(computed_extent * scale)))
        return tile_size

    def __getitem__(self, idx):
        """
        Method to get the tile at index `idx`
        :param idx: (int) tile index between `0` and `len(tiles)`
        :return: (tuple) tile extent, output size
        Tile extent in pixels: x offset, y offset, x tile extent, y tile extent.
        If scale is 1.0, then x tile extent, y tile extent are equal to tile size
        Output size in pixels: output width, height. If include_nodata is False and other parameters are such that
        tiles can go outside the image, then tile extent and output size are cropped at boundaries.
        Otherwise, output size is equal the input tile size.
        """
        if idx < -self._max_index or idx >= self._max_index:
            raise IndexError("Index %i is out of ranges %i and %i" % (idx, 0, self._max_index))

        idx = idx % self._max_index  # Handle negative indexing as -1 is the last
        x_index = idx % self.nx
        y_index = int(idx * 1.0 / self.nx)

        x_offset, x_extent = self._compute_tile_extent(x_index, self.tile_extent[0],
                                                       self.stride[0], self.origin[0], self.image_size[0],
                                                       self.include_nodata)
        y_offset, y_extent = self._compute_tile_extent(y_index, self.tile_extent[1],
                                                       self.stride[1], self.origin[1], self.image_size[1],
                                                       self.include_nodata)
        x_out_size = self.tile_size[0] if self.include_nodata else \
            self._compute_out_size(x_extent, self.tile_extent[0], self.tile_size[0], self.scale)
        y_out_size = self.tile_size[1] if self.include_nodata else \
            self._compute_out_size(y_extent, self.tile_extent[1], self.tile_size[1], self.scale)
        return (x_offset, y_offset, x_extent, y_extent), (x_out_size, y_out_size)

    @staticmethod
    def _compute_number_of_tiles(image_size, tile_extent, origin, stride):
        """
        Method to compute number of overlapping tiles
        """
        max_extent = max(tile_extent, stride)
        return max(int(np.ceil(1 + (image_size - max_extent - origin) * 1.0 / stride)), 1)


def ceil_int(x):
    return int(np.ceil(x))
