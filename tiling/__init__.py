from __future__ import absolute_import
from abc import ABCMeta, abstractmethod
import numpy as np


__version__ = '0.1.2'


class BaseTiles(object):
    """Base class to tile an image.

    See the implementations
        - ConstSizeTiles
    """
    __metaclass__ = ABCMeta

    def __init__(self, image_size, tile_size=(128, 128), scale=1.0):
        """Initialize tiles

        Args:
            image_size (list or tuple): input image size in pixels
            tile_size (int or list or tuple): output tile size in pixels
            scale (float): tile scaling factor
        """
        assert isinstance(image_size, (tuple, list)) and len(image_size) == 2, \
            "Argument image_size should be a tuple/list (sx, sy)"
        for s in image_size:
            assert s > 0, "Values of image_size should be positive"
        assert isinstance(tile_size, int) or (isinstance(tile_size, (tuple, list)) and len(tile_size) == 2), \
            "Argument tile_size should be a tuple/list (sx, sy)"
        if isinstance(tile_size, int):
            tile_size = (tile_size, tile_size)
        for s in tile_size:
            assert s > 0, "Values of image_size should be positive"
        assert scale > 0, "Argument scale should be positive"

        for tile_dim, img_dim in zip(tile_size, image_size):
            assert int(tile_dim / scale) < img_dim, \
                "Scale and tile size should not be larger than image size"

        self.image_size = image_size
        self.tile_size = tile_size
        self.scale = float(scale)
        # Apply floor to tile extent (tile size / scale)
        # Output size is then ceil(extent * scale), extent is <= tile_extent
        # ceil(extent * scale) < ceil(tile_extent * scale) = ceil(floor(tile_extent / scale) * scale)<= tile_size
        self.tile_extent = [int(np.floor(d / self.scale)) for d in self.tile_size]
        self._index = 0
        self._max_index = 0

    @abstractmethod
    def __len__(self):
        """Method to get total number of tiles
        """

    @abstractmethod
    def __getitem__(self, idx):
        """Method to get the tile at index

        Args:
            idx: (int)
        """

    def next(self):
        """Method to get next tile

        Returns:
            tile data (ndarray), tile extent (list) in the original image, in pixels
        """
        if self._index < 0 or self._index >= self._max_index:
            raise StopIteration()

        res = self[self._index]
        # ++
        self._index += 1

        return res

    __next__ = next


from tiling.const_stride import *
