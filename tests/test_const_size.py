import unittest

from tiling import ConstSizeTiles


class TestConstSizeTiles(unittest.TestCase):
    def test_wrong_args(self):

        assertRaisesRegex = self.assertRaisesRegex if hasattr(self, "assertRaisesRegex") else self.assertRaisesRegexp

        with assertRaisesRegex(
            ValueError, "Argument min_overlapping should be between 0 and min tile_extent",
        ):
            ConstSizeTiles((500, 500), (256, 256), min_overlapping=-1)

        with assertRaisesRegex(
            ValueError, "Argument min_overlapping should be between 0 and min tile_extent",
        ):
            ConstSizeTiles((500, 500), (256, 256), min_overlapping=300)

        with assertRaisesRegex(
            ValueError, "Argument min_overlapping should be between 0 and min tile_extent",
        ):
            ConstSizeTiles((500, 500), (256, 256), min_overlapping=256)

    def test_wrong_index(self):
        with self.assertRaises(IndexError):
            tiles = ConstSizeTiles((100, 120), (10, 10), min_overlapping=5)
            tiles[10000]

    def test__compute_number_of_tiles(self):
        res = ConstSizeTiles._compute_number_of_tiles(32, 100, 0)
        self.assertEqual(res, 4)
        res = ConstSizeTiles._compute_number_of_tiles(32, 100, 7)
        self.assertEqual(res, 4)
        scale = 2.0
        res = ConstSizeTiles._compute_number_of_tiles(3.0 / scale, 10, 0)
        self.assertEqual(res, 7)
        res = ConstSizeTiles._compute_number_of_tiles(6.0 / scale, 20, 1)
        self.assertEqual(res, 10)

    def test__compute_float_overlapping(self):
        res = ConstSizeTiles._compute_float_overlapping(32, 100, 4)
        self.assertEqual(res, 28.0 / 3.0)

    def test_as_iterator(self):
        tiles = ConstSizeTiles((100, 120), (10, 10), min_overlapping=5)
        counter = 0
        for extent, _ in tiles:
            _extent, _out_size = tiles[counter]
            self.assertEqual(extent, _extent)
            self.assertEqual(tiles.tile_size, _out_size)
            counter += 1

        for i, j in [(len(tiles) - 1, -1), (len(tiles) - 2, -2), (len(tiles) - 3, -3)]:
            extent1 = tiles[i]
            extent2 = tiles[j]
            self.assertEqual(extent1, extent2)

    def test_all(self):
        def _test(im_size, ts, scale, min_overlapping):

            debug_msg = "im_size={} ts={} scale={} min_overlapping={}\n".format(im_size, ts, scale, min_overlapping)

            tiles = ConstSizeTiles((im_size, im_size), ts, min_overlapping=min_overlapping, scale=scale)

            debug_msg += "n={}\n".format(len(tiles))
            self.assertGreater(len(tiles), 0, debug_msg)

            extent0, out_size = tiles[0]
            # Start at origin but should be positive
            debug_msg += "extent0={}\n".format(extent0)
            self.assertEqual((extent0[0], extent0[1]), (0, 0), debug_msg)
            self.assertEqual(tiles.tile_size[0], ts, debug_msg)
            self.assertEqual(tiles.tile_size[1], ts, debug_msg)
            self.assertLessEqual((extent0[2], extent0[3]), (ts / scale, ts / scale), debug_msg)

            for i in range(1, len(tiles)):
                extent, _ = tiles[i]
                prev_extent, _ = tiles[i - 1]
                var_debug_msg = "i={} extent={}\n".format(i, extent)
                var_debug_msg += "prev_extent={}\n".format(prev_extent)

                for j in [0, 1]:
                    self.assertGreaterEqual(
                        tiles.tile_size[j] / tiles.scale - tiles.min_overlapping,
                        extent[j] - prev_extent[j],
                        debug_msg + var_debug_msg,
                    )

            # Check the last tile ends at the boundary
            extent, _ = tiles[-1]
            debug_msg += "extent={}\n".format(extent)
            for j in [0, 1]:
                self.assertLess(extent[j], im_size, debug_msg)
                self.assertEqual(extent[j] + extent[j + 2], im_size, debug_msg)

        for scale in [0.7, 0.89, 0.99, 1.0, 1.78, 2.12]:
            for im_size in range(100, 120):
                for ts in range(32, int(im_size * scale) - 1, 3):
                    for min_overlapping in range(int(ts / scale) // 2, int(ts / scale) - 1, 5):
                        _test(im_size, ts, scale, min_overlapping)


if __name__ == "__main__":
    unittest.main()
