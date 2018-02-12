
import unittest

import numpy as np


from tiling import ConstStrideTiles


class TestConstStrideTiles(unittest.TestCase):

    def test_wrong_args(self):

        with self.assertRaises(AssertionError):
            ConstStrideTiles(1.0, 1.0)

        with self.assertRaises(AssertionError):
            ConstStrideTiles(100, 1.0)

        with self.assertRaises(AssertionError):
            ConstStrideTiles(100, -10)

        with self.assertRaises(AssertionError):
            ConstStrideTiles(-100, 10)

        with self.assertRaises(AssertionError):
            ConstStrideTiles(100, 100)

        with self.assertRaises(AssertionError):
            ConstStrideTiles((100, 120), 100)

        with self.assertRaises(AssertionError):
            ConstStrideTiles((100, 120), (10, -10))

        with self.assertRaises(AssertionError):
            ConstStrideTiles((100, 120), (10, 10), stride=-10)

        with self.assertRaises(AssertionError):
            ConstStrideTiles((100, 120), (10, 10), stride=(10, -10))

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
            self.assertLess(np.sqrt(len(tiles)), 1 + (im_size - origin) * 1.0 / stride, debug_msg)

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
                    self.assertEqual(stride, extent[0] - prev_extent[0], debug_msg)
                if extent[1] - prev_extent[1] > 0:
                    self.assertEqual(stride, extent[1] - prev_extent[1], debug_msg)
                else:
                    self.assertEqual(0, extent[1] - prev_extent[1], debug_msg)

                # Check if output size is the same
                self.assertEqual(out_size, out_size0)

            # Check the last tile ends at the boundary or out side and starts inside
            extent, _ = tiles[-1]
            debug_msg += "extent={}, out_size={}\n".format(extent, _)
            self.assertLess(extent[0], im_size, debug_msg)
            self.assertLess(extent[1], im_size, debug_msg)
            self.assertGreaterEqual(extent[0] + max(extent[2], stride), im_size, debug_msg)
            self.assertGreaterEqual(extent[1] + max(extent[3], stride), im_size, debug_msg)

        for scale in [0.7, 0.89, 0.99, 1.0, 1.78, 2.12]:
            for im_size in range(100, 120):
                for ext in range(32, int(im_size * scale) - 1, 3):
                    for stride in range(ext // 2, ext + 10, 3):
                        for origin in range(-5, 5):
                            _test(im_size, ext, scale, stride, origin)

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
            self.assertLess(np.sqrt(len(tiles)), 1 + (im_size - origin) * 1.0 / stride, debug_msg)

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
                        self.assertEqual(stride, extent[0] - prev_extent[0],
                                         debug_msg + var_debug_msg)

                    # Check if output size is the same
                    self.assertEqual(out_size[0], ts, debug_msg + var_debug_msg)
                else:
                    if extent[0] - prev_extent[0] > 0:
                        if prev_extent[0] == 0 and extent[0] + extent[2] < im_size:
                            # Check stride between the ends of tiles
                            self.assertEqual(stride, extent[0] + extent[2] - prev_extent[0] - prev_extent[2],
                                             debug_msg + var_debug_msg)
                        elif prev_extent[0] > 0 and extent[0] + extent[2] == im_size:
                            # Check stride between the starts of tiles
                            self.assertEqual(stride, extent[0] - prev_extent[0],
                                             debug_msg + var_debug_msg)

                if prev_extent[3] == tiles.tile_extent[1]:
                    if extent[1] - prev_extent[1] > 0:
                        self.assertEqual(stride, extent[1] - prev_extent[1],
                                         debug_msg + var_debug_msg)
                    else:
                        self.assertEqual(0, extent[1] - prev_extent[1], debug_msg + var_debug_msg)
                    self.assertEqual(out_size[1], ts, debug_msg + var_debug_msg)
                else:
                    if extent[1] - prev_extent[1] > 0:
                        if prev_extent[1] == 0 and extent[1] + extent[3] < im_size:
                            # Check stride between the ends of tiles
                            self.assertEqual(stride, extent[1] + extent[3] - prev_extent[1] - prev_extent[3],
                                             debug_msg + var_debug_msg)
                        elif prev_extent[1] > 0 and extent[1] + extent[3] == im_size:
                            self.assertEqual(stride, extent[1] - prev_extent[1],
                                             debug_msg + var_debug_msg)

            # Check the last tile ends at the boundary or out side and starts inside
            extent, _ = tiles[-1]
            debug_msg += "extent={}, out_size={}\n".format(extent, _)
            self.assertLess(extent[0], im_size, debug_msg)
            self.assertLess(extent[1], im_size, debug_msg)
            if stride < tiles.tile_extent[0]:
                self.assertEqual(extent[0] + extent[2], im_size, debug_msg)
            else:
                self.assertLessEqual(extent[0] + extent[2], im_size, debug_msg)

            if stride < tiles.tile_extent[1]:
                self.assertEqual(extent[1] + extent[3], im_size, debug_msg)
            else:
                self.assertLessEqual(extent[1] + extent[3], im_size, debug_msg)

        for scale in [0.7, 0.89, 0.99, 1.0, 1.78, 2.12]:
            for im_size in range(100, 120):
                for ext in range(32, int(im_size * scale) - 1, 3):
                    for stride in range(ext // 2, ext + 10, 3):
                        for origin in range(-5, 5):
                            _test(im_size, ext, scale, stride, origin)


if __name__ == "__main__":
    unittest.main()
