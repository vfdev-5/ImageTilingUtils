tiling.const_size
=================

.. currentmodule:: tiling.const_size

Class provides constant size tile parameters (offset, extent) to extract data from image.

Generated tile extents can overlap, do not includes nodata paddings.
For example, tiling can look like this:

.. code-block:: text

      tile 0      tile 2      tile 4
    |<------>|  |<------>|  |<------>|
            tile 1      tile 3      tile 5
          |<------>|  |<------>|  |<------>|
    |<------------------------------------>|
    |                IMAGE                 |
    |                                      |


Basic usage:

.. code-block:: python

    from tiling import ConstSizeTiles

    tiles = ConstSizeTiles(image_size=(500, 500), tile_size=(256, 256), min_overlapping=100)

    print("Number of tiles: %i" % len(tiles))
    for x, y, width, height in tiles:
        data = read_data(x, y, width, height, tiles.tile_size[0], tiles.tile_size[0])
        print("data.shape: {}".format(data.shape))


.. autoclass:: ConstSizeTiles
   :members:
   :inherited-members:

