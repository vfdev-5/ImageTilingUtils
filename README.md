[![Build Status](https://travis-ci.org/vfdev-5/ImageTilingUtils.svg?branch=master)](https://travis-ci.org/vfdev-5/ImageTilingUtils)
[![Coverage Status](https://coveralls.io/repos/github/vfdev-5/ImageTilingUtils/badge.svg?branch=master)](https://coveralls.io/github/vfdev-5/ImageTilingUtils?branch=master)
[![Documentation Status](https://readthedocs.org/projects/imagetilingutils/badge/?version=latest)](http://imagetilingutils.readthedocs.io/en/latest/?badge=latest)

# Image Tiling Utils
Minimalistic set of image reader agnostic tools to easily iterate over large images

**Example 1**

Let's iterate over a large image with overlapping tiles of the 
same size tiles in pixels. At boundaries we add "no-data" pixels. 
Let's assume the data access is provided with an example function
```python
def read_data(x, y, width, height, out_width=None, out_height=None):
    out_width = width if out_width is None else out_width
    out_height = height if out_height is None else out_height    
    img.read(x, y, width, height, out_width, out_height)
``` 
Thus, overlapping tiles can be extracted as  
```python
from tiling import ConstStrideTiles

tiles = ConstStrideTiles(image_size=(500, 500), tile_size=(256, 256), stride=(100, 100), 
                         origin=(-100, -100),
                         scale=1.0,
                         include_nodata=True)
                       
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
```

![example 1 tiles](assets/example_const_stride_tiles.png)


**Example 2**

Let's iterate over a large image with overlapping tiles of the same size in pixels. 
In this case we prefer to not going outside the input image and fill tiles with `nodata`.
In this situation, overlapping is not constant. 
Let's assume the data access is provided with an example function
```python
def read_data(x, y, width, height, out_width=None, out_height=None):
    out_width = width if out_width is None else out_width
    out_height = height if out_height is None else out_height    
    img.read(x, y, width, height, out_width, out_height)
``` 
Thus, overlapping tiles can be extracted as  
```python
from tiling import ConstSizeTiles

tiles = ConstSizeTiles(image_size=(500, 500), tile_size=(256, 256), min_overlapping=15, scale=1.0)
                       
print("Number of tiles: %i" % len(tiles))
for extent in tiles:
    x, y, width, height = extent
    data = read_data(x, y, width, height, 
                     out_width=tiles.tile_size[0], 
                     out_height=tiles.tile_size[1])
    print("data.shape: {}".format(data.shape))

# Access a tile:
i = len(tiles) // 2 
extent  = tiles[i]
```

![example 2 tiles](assets/example_const_size_tiles.png)


## Installation:

#### from pip
```bash
pip install tiling
```

#### from sources

```bash
pip install git+https://github.com/vfdev-5/ImageTilingUtils.git
```

## Examples 

For more practical examples, see [notebooks](examples)
