#
# import unittest
#
# import numpy as np
#
#
# from tiling import ConstSizeTiles
#
#
# class TestConstSizeTiles(unittest.TestCase):
#
#     def test__compute_number_of_tiles(self):
#         res = ConstSizeTiles._compute_number_of_tiles(32, 100, 0)
#         self.assertEqual(res, 4)
#         res = ConstSizeTiles._compute_number_of_tiles(32, 100, 7)
#         self.assertEqual(res, 4)
#         scale = 2.0
#         res = ConstSizeTiles._compute_number_of_tiles(3.0/scale, 10, 0)
#         self.assertEqual(res, 7)
#         res = ConstSizeTiles._compute_number_of_tiles(6.0/scale, 20, 1)
#         self.assertEqual(res, 10)
#
#     def test__compute_float_overlapping(self):
#         res = ConstSizeTiles._compute_float_overlapping(32, 100, 4)
#         self.assertEqual(res, 28.0 / 3.0)
#
#     def test__compute_tile_params(self):
#
#         def _test(width, size, overlapping, scale):
#
#             offset,  = ConstSizeTiles._compute_tile_params()
#
#
#         for scale in [0.7, 0.89, 0.99, 1.0, 1.78, 2.12]:
#             for im_size in range(50, 100, 3):
#                 for ext in range(12, int(im_size * scale) - 1):
#                     for min_ovr in range(0, int(ext / scale) - 1):
#                         _test(im_size, ext, min_ovr, scale)
#
#     def test_no_scale(self):
#
#         def _test(image_size, tile_size, min_overlapping):
#
#             tiles = ConstSizeTiles(image_size=image_size, tile_size=tile_size,
#                                    min_overlapping=min_overlapping, scale=1.0)
#
#             true_image = np.random.rand(image_size[1], image_size[0], 3)
#             tiled_image = np.zeros_like(true_image)
#             count = 0
#             for i, (x, y, width, height) in enumerate(tiles):
#                 count += 1
#                 self.assertTrue(0 <= x <= image_size[0] - tile_size[0],
#                                 "{}: 0 <= {} <= {}".format(i, x, image_size[0] - tile_size[0]))
#                 self.assertTrue(0 <= y <= image_size[1] - tile_size[1],
#                                 "{}: 0 <= {} <= {}".format(i, y, image_size[1] - tile_size[1]))
#                 self.assertEqual(width, tiles.tile_size[0])
#                 self.assertEqual(height, tiles.tile_size[1])
#                 self.assertTrue(x + width <= image_size[0],
#                                 "{}: 0 <= {} <= {}".format(i, x + width, image_size[0]))
#                 self.assertTrue(y + height <= image_size[1],
#                                 "{}: 0 <= {} <= {}".format(i, y + height, image_size[1]))
#                 tiled_image[y:y + height, x:x + width, :] = true_image[y:y + height, x:x + width, :]
#
#             self.assertEqual(len(tiles), count)
#             err = float(np.sum(np.abs(tiled_image - true_image)))
#             self.assertLess(err, 1e-10, "Err : %f" % err)
#
#         for o in [0, 5, 10, 15]:
#             _test((123, 234), (23, 34), o)
#             _test((256, 256), (32, 32), o)
#             _test((512, 512), (128, 128), o)
#
#     def test_with_scale(self):
#
#         def _test(image_size, tile_size, min_overlapping, scale):
#             tiles = ConstSizeTiles(image_size=image_size, tile_size=tile_size,
#                                    min_overlapping=min_overlapping, scale=scale)
#             count = 0
#             for i, (x, y, width, height) in enumerate(tiles):
#                 count += 1
#                 self.assertTrue(0 <= x <= image_size[0]*scale - tile_size[0],
#                                 "{}: 0 <= {} <= {}".format(i, x, image_size[0]*scale - tile_size[0]))
#                 self.assertTrue(0 <= y <= image_size[1]*scale - tile_size[1],
#                                 "{}: 0 <= {} <= {}".format(i, y, image_size[1]*scale - tile_size[1]))
#                 # self.assertEqual(width, tiles.tile_size[0])
#                 # self.assertEqual(height, tiles.tile_size[1])
#                 # self.assertTrue(x + width <= image_size[0],
#                 #                 "{}: 0 <= {} <= {}".format(i, x + width, image_size[0]))
#                 # self.assertTrue(y + height <= image_size[1],
#                 #                 "{}: 0 <= {} <= {}".format(i, y + height, image_size[1]))
#
#             self.assertEqual(len(tiles), count)
#
#         for s in [0.7, 0.88, 0.97, 1.0, 1.23, 1.89, 2.34]:
#             _test((123, 234), (23, 34), 15, s)
#             _test((256, 256), (32, 32), 15, s)
#             _test((512, 512), (128, 128), 15, s)
#
# if __name__ == "__main__":
#     unittest.main()
