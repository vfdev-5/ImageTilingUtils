tiling.const_stride
===================

.. currentmodule:: tiling.const_stride

Class provides tile parameters (offset, extent) to extract data from image.

Generated tile extents starts from an origin, has constant stride and can optionally include nodata paddings.
For example, tiling can look like this (origin is negative, include nodata)

.. code-block:: text

        tile 0        tile 2      tile 4
        |<------->|   |<------>|  |<------>|     etc
                  tile 1      tile 3      tile 5     tile n-1
        ^      |<------->|  |<------>|  |<------>| |<------>|
        |        |<------------------------------------>|
     origin      |                IMAGE                 |
                 |                                      |


Another example, tiling can look like this (origin is negative, no nodata, tile size is not constant at boundaries)

.. code-block:: text

                tile 0    tile 2      tile 4
                |<->|   |<------>|  |<------>|     etc
                  tile 1      tile 3      tile 5     tile n-1
        ^       |<------>|  |<------>|  |<------>| |<->|
        |       |<------------------------------------>|
     origin     |                IMAGE                 |
                |                                      |


Another example, tiling can look like this (origin is postive, no nodata, tile size is not constant at boundaries)

.. code-block:: text

          tile 0        tile 2
        |<------->|   |<------>|      etc
                  tile 1      tile 3      tile n-1
        ^      |<------->|  |<------>|  |<-->|
    |<-------------------------------------->|
    |   |            IMAGE                   |
    | origin                                 |


Basic usage:

.. code-block:: python

    from tiling import ConstStrideTiles

    tiles = ConstStrideTiles(image_size=(500, 500), tile_size=(256, 256), stride=(100, 100))

    print("Number of tiles: %i" % len(tiles))
    for (x, y, width, height), (out_width, out_height) in tiles:
        data = read_data(x, y, width, height, out_width, out_height)
        print("data.shape: {}".format(data.shape))

    # Get a tile params at linear index:
    extent, out_size = tiles[len(tiles)//2]


.. autoclass:: ConstStrideTiles
   :members:
   :inherited-members:
