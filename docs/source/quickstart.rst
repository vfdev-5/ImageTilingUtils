Quickstart
==========

Let's iterate over a large image with overlapping and extracting always the 
same size tiles (in pixels).  Let's assume the data access is provided with an example function


.. code-block:: python

    def read_data(x, y, width, height, out_width=None, out_height=None):
        out_width = width if out_width is None else out_width
        out_height = height if out_height is None else out_height
        img.read(x, y, width, height, out_width, out_height)

Thus, overlapping tiles can be extracted as  

.. code-block:: python

    from tiling import ConstStrideTiles


    tiles = ConstStrideTiles(image_size=(500, 500), tile_size=(256, 256),
                             stride=(100, 100))

    print("Number of tiles: %i" % len(tiles))
    for extent, out_size in tiles:
        x, y, width, height = extent
        data = read_data(x, y, width, height,
                         out_width=out_size[0],
                         out_height=out_size[1])
        print("data.shape: {}".format(data.shape))
    
    # Access a tile:
    i = len(tiles) // 2
    extent, out_size  = tiles[i]


.. image:: https://github.com/vfdev-5/ImageTilingUtils/raw/master/examples/example_tiles.png

