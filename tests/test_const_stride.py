
import unittest

import math


from tiling import ConstStrideTiles, ceil_int


class TestConstStrideTiles(unittest.TestCase):

    def test_get_version(self):
        from tiling import __version__
        self.assertTrue(isinstance(__version__, str))

    def test_wrong_args(self):

        assertRaisesRegex = self.assertRaisesRegex if hasattr(self, 'assertRaisesRegex') else self.assertRaisesRegexp

        with assertRaisesRegex(TypeError, "Argument image_size should be"):
            ConstStrideTiles(1.0, 1.0)

        with assertRaisesRegex(ValueError, "Values of image_size should be positive"):
            ConstStrideTiles((0, 0), 1.0)

        with assertRaisesRegex(TypeError, "Argument tile_size should be either int or pair of integers"):
            ConstStrideTiles((100, 100), "abc")

        with assertRaisesRegex(ValueError, "Values of tile_size should be positive"):
            ConstStrideTiles((100, 100), -1)

        with assertRaisesRegex(ValueError, "Values of tile_size should be positive"):
            ConstStrideTiles((100, 120), (10, -10))

        with assertRaisesRegex(ValueError, "Argument scale should be positive"):
            ConstStrideTiles((100, 120), (10, 10), scale=0.0)

        with assertRaisesRegex(ValueError, "should not be larger than image size"):
            ConstStrideTiles((1, 1), (10, 10), scale=1.0)

        with assertRaisesRegex(TypeError, "Argument stride should be"):
            ConstStrideTiles((100, 120), (10, 10), stride="abc")

        with assertRaisesRegex(ValueError, "should be larger than 1 pixel"):
            ConstStrideTiles((100, 120), (10, 10), stride=(10, -10))

    def test_wrong_index(self):

        with self.assertRaises(IndexError):
            tiles = ConstStrideTiles((100, 120), (10, 10), stride=(5, 5))
            tiles[10000]

    def test_with_nodata(self):

        def _test(im_size, ts, scale, stride, origin):

            debug_msg = "im_size={} ts={} scale={} stride={} origin={}\n"\
                .format(im_size, ts, scale, stride, origin)

            tiles = ConstStrideTiles((im_size, im_size),
                                     (ts, ts),
                                     stride=(stride, stride),
                                     scale=scale,
                                     origin=(origin, origin),
                                     include_nodata=True)

            debug_msg += "n={}\n".format(len(tiles))
            self.assertGreater(len(tiles), 0, debug_msg)
            self.assertLess(math.sqrt(len(tiles)), 1 + (im_size - origin) * 1.0 / tiles.stride[0], debug_msg)

            extent0, out_size0 = tiles[0]
            # Start at origin
            debug_msg += "extent0={}, out_size0={}\n".format(extent0, out_size0)
            self.assertEqual((extent0[0], extent0[1]), (origin, origin), debug_msg)
            self.assertEqual((out_size0[0], out_size0[1]), (ts, ts), debug_msg)
            # Extent
            d = (extent0[2], extent0[3])

            for i in range(1, len(tiles)):
                extent, out_size = tiles[i]
                prev_extent, _ = tiles[i - 1]
                # Check if constant extent
                self.assertEqual(d, (extent[2], extent[3]), debug_msg)
                # Check if constant stride
                if extent[0] - prev_extent[0] > 0:
                    self.assertEqual(tiles.stride[0], extent[0] - prev_extent[0], debug_msg)
                if extent[1] - prev_extent[1] > 0:
                    self.assertEqual(tiles.stride[1], extent[1] - prev_extent[1], debug_msg)
                else:
                    self.assertEqual(0, extent[1] - prev_extent[1], debug_msg)

                # Check if output size is the same
                self.assertEqual(out_size, out_size0)

            # Check the last tile ends at the boundary or out side and starts inside
            extent, _ = tiles[-1]
            debug_msg += "extent={}, out_size={}\n".format(extent, _)
            self.assertLess(extent[0], im_size, debug_msg)
            self.assertLess(extent[1], im_size, debug_msg)
            self.assertGreaterEqual(extent[0] + max(extent[2], tiles.stride[0]), im_size, debug_msg)
            self.assertGreaterEqual(extent[1] + max(extent[3], tiles.stride[1]), im_size, debug_msg)

        for scale in [0.7, 0.89, 0.99, 1.0, 1.78, 2.12]:
            for im_size in range(100, 120):
                for ext in range(32, int(im_size * scale) - 1, 3):
                    for stride in range(int(ext * scale) // 2, int(ext * scale) + 10, 5):
                        for origin in range(-5, 5):
                            _test(im_size, ext, scale, stride, origin)

    def test_as_iterator(self):
        tiles = ConstStrideTiles((100, 120), (10, 10), stride=(5, 5))
        counter = 0
        for extent, out_size in tiles:
            _extent, _out_size = tiles[counter]
            self.assertEqual(extent, _extent)
            self.assertEqual(out_size, _out_size)
            counter += 1

        for i, j in [(len(tiles) - 1, -1), (len(tiles) - 2, -2), (len(tiles) - 3, -3)]:
            extent1, out_size1 = tiles[i]
            extent2, out_size2 = tiles[j]
            self.assertEqual(extent1, extent2)
            self.assertEqual(out_size1, out_size2)

    def test_without_nodata(self):

        def _test(im_size, ts, scale, stride, origin):

            debug_msg = "im_size={} ts={} scale={} stride={} origin={}\n"\
                .format(im_size, ts, scale, stride, origin)

            tiles = ConstStrideTiles((im_size, im_size),
                                     ts,
                                     stride=stride,
                                     scale=scale,
                                     origin=(origin, origin),
                                     include_nodata=False)

            debug_msg += "n={}\n".format(len(tiles))
            self.assertGreater(len(tiles), 0, debug_msg)
            self.assertLess(math.sqrt(len(tiles)), 1 + (im_size - origin) * 1.0 / tiles.stride[0], debug_msg)

            extent0, out_size0 = tiles[0]
            # Start at origin but should be positive
            if origin < 0:
                debug_msg += "extent0={}, out_size0={}\n".format(extent0, out_size0)
                self.assertEqual((extent0[0], extent0[1]), (0, 0), debug_msg)
                self.assertLessEqual((out_size0[0], out_size0[1]), (ts, ts), debug_msg)
                self.assertLessEqual((extent0[2], extent0[3]), (ts / scale, ts / scale), debug_msg)
            else:
                debug_msg += "extent0={}, out_size0={}\n".format(extent0, out_size0)
                self.assertEqual((extent0[0], extent0[1]), (origin, origin), debug_msg)
                # Ensure that the first tile does not go beyond the image size
                if extent0[0] + extent0[2] < im_size:
                    self.assertEqual(out_size0[0], ts, debug_msg)
                else:
                    pass
                if extent0[1] + extent0[3] < im_size:
                    self.assertEqual(out_size0[1], ts, debug_msg)
                else:
                    pass
                self.assertLessEqual((extent0[2], extent0[3]), (ts / scale, ts / scale), debug_msg)

            for i in range(1, len(tiles)):
                extent, _ = tiles[i]
                prev_extent, out_size = tiles[i - 1]
                var_debug_msg = "i={} extent={} out_size={}\n"\
                    .format(i, extent, _)
                var_debug_msg += "prev_extent={} out_size={}\n"\
                    .format(prev_extent, out_size)

                if prev_extent[2] == tiles.tile_extent[0]:
                    # Check if constant stride
                    if extent[0] - prev_extent[0] > 0:
                        self.assertEqual(tiles.stride[0], extent[0] - prev_extent[0],
                                         debug_msg + var_debug_msg)

                    # Check if output size is the same
                    self.assertEqual(out_size[0], ts, debug_msg + var_debug_msg)
                else:
                    if extent[0] - prev_extent[0] > 0:
                        if prev_extent[0] == 0 and extent[0] + extent[2] < im_size:
                            # Check stride between the ends of tiles
                            self.assertEqual(tiles.stride[1], extent[0] + extent[2] - prev_extent[0] - prev_extent[2],
                                             debug_msg + var_debug_msg)
                        elif prev_extent[0] > 0 and extent[0] + extent[2] == im_size:
                            # Check stride between the starts of tiles
                            self.assertEqual(tiles.stride[0], extent[0] - prev_extent[0],
                                             debug_msg + var_debug_msg)

                if prev_extent[3] == tiles.tile_extent[1]:
                    if extent[1] - prev_extent[1] > 0:
                        self.assertEqual(tiles.stride[1], extent[1] - prev_extent[1],
                                         debug_msg + var_debug_msg)
                    else:
                        self.assertEqual(0, extent[1] - prev_extent[1], debug_msg + var_debug_msg)
                    self.assertEqual(out_size[1], ts, debug_msg + var_debug_msg)
                else:
                    if extent[1] - prev_extent[1] > 0:
                        if prev_extent[1] == 0 and extent[1] + extent[3] < im_size:
                            # Check stride between the ends of tiles
                            self.assertEqual(tiles.stride[1], extent[1] + extent[3] - prev_extent[1] - prev_extent[3],
                                             debug_msg + var_debug_msg)
                        elif prev_extent[1] > 0 and extent[1] + extent[3] == im_size:
                            self.assertEqual(tiles.stride[1], extent[1] - prev_extent[1],
                                             debug_msg + var_debug_msg)

            # Check the last tile ends at the boundary or out side and starts inside
            extent, _ = tiles[-1]
            debug_msg += "extent={}, out_size={}\n".format(extent, _)
            self.assertLess(extent[0], im_size, debug_msg)
            self.assertLess(extent[1], im_size, debug_msg)
            if tiles.stride[0] < tiles.tile_extent[0]:
                self.assertEqual(extent[0] + extent[2], im_size, debug_msg)
            else:
                self.assertLessEqual(extent[0] + extent[2], im_size, debug_msg)

            if tiles.stride[1] < tiles.tile_extent[1]:
                self.assertEqual(extent[1] + extent[3], im_size, debug_msg)
            else:
                self.assertLessEqual(extent[1] + extent[3], im_size, debug_msg)

        for scale in [0.7, 0.89, 0.99, 1.0, 1.78, 2.12]:
            for im_size in range(100, 120):
                for ext in range(32, int(im_size * scale) - 1, 3):
                    for stride in range(int(ext * scale) // 2, int(ext * scale) + 10, 5):
                        for origin in range(-5, 5):
                            _test(im_size, ext, scale, stride, origin)

    def test_int_ceil(self):
        self.assertEqual(2, ceil_int(1.789))


if __name__ == "__main__":
    unittest.main()
