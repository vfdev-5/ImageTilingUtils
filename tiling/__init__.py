from abc import ABCMeta, abstractmethod
import math

try:
    from collections.abc import Sequence
except ImportError:
    from collections import Sequence

from six import with_metaclass


__version__ = '0.2.0'


class BaseTiles(with_metaclass(ABCMeta, object)):
    """
    Base class to tile an image.
    See the implementations
        - ConstSizeTiles
        - ConstStrideTiles
    """

    def __init__(self, image_size, tile_size=(128, 128), scale=1.0):
        """Initialize tiles

        Args:
            image_size (list/tuple): input image size in pixels
            tile_size (int or list/tuple): output tile size in pixels
            scale (float): tile scaling factor
        """

        if not (isinstance(image_size, Sequence) and len(image_size) == 2):
            raise TypeError("Argument image_size should be (sx, sy)")
        for s in image_size:
            if s < 1:
                raise ValueError("Values of image_size should be positive")

        if not (isinstance(tile_size, int) or (isinstance(tile_size, Sequence) and len(tile_size) == 2)):
            raise TypeError("Argument tile_size should be either int or pair of integers (sx, sy)")
        if isinstance(tile_size, int):
            tile_size = (tile_size, tile_size)
        for s in tile_size:
            if s < 1:
                raise ValueError("Values of tile_size should be positive")

        if scale <= 0:
            raise ValueError("Argument scale should be positive")

        for tile_dim, img_dim in zip(tile_size, image_size):
            if int(tile_dim / scale) >= img_dim:
                raise ValueError("Scale {} and tile size {} should not be larger "
                                 "than image size {}".format(scale, tile_dim, img_dim))

        self.image_size = image_size
        self.tile_size = tile_size
        self.scale = float(scale)
        # Apply floor to tile extent (tile size / scale)
        # Output size is then ceil(extent * scale), extent is <= tile_extent
        # ceil(extent * scale) < ceil(tile_extent * scale) = ceil(floor(tile_extent / scale) * scale)<= tile_size
        self.tile_extent = [int(math.floor(d / self.scale)) for d in self.tile_size]
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


def ceil_int(x):
    return int(math.ceil(x))


from tiling.const_stride import ConstStrideTiles
from tiling.const_size import ConstSizeTiles
