# -*- coding:utf-8 -*-
import logging
import math

try:
    from collections.abc import Sequence
except ImportError:
    from collections import Sequence

from tiling import BaseTiles, ceil_int

logger = logging.getLogger('tiling')


class ConstStrideTiles(BaseTiles):
    """Class provides tile parameters (offset, extent) to extract data from image.

    Args:
        image_size (list/tuple of int): input image size in pixels (width, height)
        tile_size (int or list/tuple of int): output tile size in pixels (width, height)
        stride (list/tuple of int): horizontal and vertical strides in pixels.
            Values need to be positive larger than 1 pixel. Stride value is impacted with scale and corresponds
            to a sliding over scaled image.
        scale (float): Scaling applied to the input image parameters before extracting tile's extent
        origin (list or tuple of int): point in pixels in the original image from where to start the tiling.
            Values can be positive or negative.
        include_nodata (bool): Include or not nodata. If nodata is included then tile extents have all the
            same size, otherwise tiles at boundaries will be reduced
    """
    def __init__(self, image_size, tile_size, stride=(1, 1), scale=1.0, origin=(0, 0), include_nodata=True):
        super(ConstStrideTiles, self).__init__(image_size=image_size, tile_size=tile_size, scale=scale)

        if not (isinstance(stride, int) or (isinstance(stride, Sequence) and len(stride) == 2)):
            raise TypeError("Argument stride should be (sx, sy)")

        if isinstance(stride, int):
            stride = (stride, stride)

        # Apply scale on the stride
        stride = [int(math.floor(s / self.scale)) for s in stride]
        for v in stride:
            if v < 1:
                raise ValueError("Scaled stride values `floor(stride / scale)` should be larger than 1 pixel")

        self.stride = stride
        self.origin = origin
        self.include_nodata = include_nodata
        self.nx = ConstStrideTiles._compute_number_of_tiles(self.image_size[0], self.tile_extent[0],
                                                            self.origin[0], self.stride[0])
        self.ny = ConstStrideTiles._compute_number_of_tiles(self.image_size[1], self.tile_extent[1],
                                                            self.origin[1], self.stride[1])
        self._max_index = self.nx * self.ny

    def __len__(self):
        """Method to get total number of tiles
        """
        return self._max_index

    @staticmethod
    def _compute_tile_extent(idx, tile_extent, stride, origin, image_size, include_nodata):
        """Method to compute tile extent: offset, extent for a given index
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
        """Method to compute tile output size for a given computed extent.
        """
        if computed_extent < tile_extent:
            return ceil_int(1.0 * computed_extent * scale)
        return tile_size

    def __getitem__(self, idx):
        """Method to get the tile at index `idx`

        Args:
            idx: (int) tile index between `0` and `len(tiles)`

        Returns:
            (tuple) tile extent, output size

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
        """Method to compute number of overlapping tiles
        """
        max_extent = max(tile_extent, stride)
        return max(ceil_int(1 + (image_size - max_extent - origin) * 1.0 / stride), 1)
