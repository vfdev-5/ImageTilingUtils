# -*- coding:utf-8 -*-
import logging
from tiling import BaseTiles, ceil_int


logger = logging.getLogger('tiling')


class ConstSizeTiles(BaseTiles):
    """Class provides constant size tile parameters (offset, extent) to extract data from image.
    Generated tile extents can overlap and do not includes nodata paddings.

    Args:
        image_size (list/tuple of int): input image size in pixels (width, height)
        tile_size (int or list/tuple of int): output tile size in pixels (width, height)
        min_overlapping (int): minimal overlapping in pixels between tiles.
        scale (float): Scaling applied to the input image parameters before extracting tile's extent
    """
    def __init__(self, image_size, tile_size, min_overlapping=0, scale=1.0):
        super(ConstSizeTiles, self).__init__(image_size=image_size, tile_size=tile_size, scale=scale)

        if not (0 <= min_overlapping < min(self.tile_extent[0], self.tile_extent[1])):
            raise ValueError("Argument min_overlapping should be between 0 and min tile_extent = tile_size / scale"
                             ", but given {}".format(min_overlapping))

        self.min_overlapping = min_overlapping
        # Compute number of tiles:
        self.nx = ConstSizeTiles._compute_number_of_tiles(self.tile_extent[0], self.image_size[0], min_overlapping)
        self.ny = ConstSizeTiles._compute_number_of_tiles(self.tile_extent[1], self.image_size[1], min_overlapping)

        if self.nx < 1:
            raise ValueError("Number of horizontal tiles is not positive. Wrong input parameters: {}, {}, {}".format(
                self.tile_extent[0], self.image_size[0], min_overlapping))

        if self.ny < 1:
            raise ValueError("Number of vertical tiles is not positive. Wrong input parameters: {}, {}, {}".format(
                self.tile_extent[1], self.image_size[1], min_overlapping))

        self.float_overlapping_x = ConstSizeTiles._compute_float_overlapping(self.tile_extent[0],
                                                                             self.image_size[0], self.nx)
        self.float_overlapping_y = ConstSizeTiles._compute_float_overlapping(self.tile_extent[1],
                                                                             self.image_size[1], self.ny)
        self._max_index = self.nx * self.ny

    def __len__(self):
        """Method to get total number of tiles
        """
        return self._max_index

    @staticmethod
    def _compute_tile_extent(idx, tile_extent, overlapping):
        """Method to compute tile extent: offset, extent for a given index
        """

        offset = int(round(idx * (tile_extent - overlapping)))
        return offset, int(round(tile_extent))

    def __getitem__(self, idx):
        """Method to get the tile at index `idx`

        Args:
            idx: (int) tile index between `0` and `len(tiles)`

        Returns:
            (tuple) tile extent in pixels: x offset, y offset, x tile extent, y tile extent

        If scale is 1.0, then x tile extent, y tile extent are equal to tile size
        """
        if idx < -self._max_index or idx >= self._max_index:
            raise IndexError("Index %i is out of ranges %i and %i" % (idx, 0, self._max_index))

        idx = idx % self._max_index  # Handle negative indexing as -1 is the last
        x_tile_index = idx % self.nx
        y_tile_index = int(idx * 1.0 / self.nx)

        x_tile_offset, x_tile_extent = self._compute_tile_extent(x_tile_index, self.tile_extent[0],
                                                                 self.float_overlapping_x)
        y_tile_offset, y_tile_extent = self._compute_tile_extent(y_tile_index, self.tile_extent[1],
                                                                 self.float_overlapping_y)
        return x_tile_offset, y_tile_offset, x_tile_extent, y_tile_extent

    @staticmethod
    def _compute_number_of_tiles(tile_extent, image_size, min_overlapping):
        """Method to compute number of overlapping tiles for a given image size
        """
        return ceil_int(image_size * 1.0 / (tile_extent - min_overlapping + 1e-10))

    @staticmethod
    def _compute_float_overlapping(tile_size, image_size, n):
        """Method to float overlapping
        """
        return (tile_size * n - image_size) * 1.0 / (n - 1.0) if n > 1 else 0
