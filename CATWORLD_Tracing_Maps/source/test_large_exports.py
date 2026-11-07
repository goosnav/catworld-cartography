"""Delivery regression: every culture must have a usable, large tracing canvas.

Run after rebuilding: python -m unittest discover -s CATWORLD_Tracing_Maps/source
"""
from pathlib import Path
import unittest
from PIL import Image

# These are locally generated masters, intentionally above Pillow's default
# 89 MP warning. Retain a finite bound rather than disabling the guard globally.
Image.MAX_IMAGE_PIXELS = 150_000_000

ROOT = Path(__file__).resolve().parents[1]


class LargeExportTests(unittest.TestCase):
    def test_all_maps_have_large_sheet_and_artwork_canvases(self):
        for key in ('birds', 'cats', 'reptiles', 'world'):
            for suffix in ('trace_master', 'trace_artwork'):
                with self.subTest(map=key, export=suffix):
                    path = ROOT / 'png' / f'{key}_{suffix}.png'
                    self.assertTrue(path.is_file(), f'Missing drawing canvas: {path.name}')
                    # Header inspection avoids decoding 135 megapixels per assertion.
                    with Image.open(path) as image:
                        self.assertEqual(image.width, 13200)
                        self.assertGreaterEqual(image.height, 6000)
                        self.assertLessEqual(image.height, 14000)
                        self.assertEqual(image.mode, 'L')
                        if suffix == 'trace_master':
                            self.assertEqual(image.size, (13200, 10200))
                        image.verify()


if __name__ == '__main__':
    unittest.main()
