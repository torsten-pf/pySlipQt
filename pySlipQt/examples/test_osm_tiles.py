"""
Test the OSM tiles code.

Requires a PyQt5 application to be created before use.
If we can create a bitmap without PyQt5, we could remove this dependency.
"""

import os
import sys
import glob
import pickle
import unittest
import shutil

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel,
                             QSpinBox, QVBoxLayout, QVBoxLayout, QAction,
                             QHBoxLayout, QVBoxLayout, QGridLayout,
                             QErrorMessage)

# initialize the logging system
import pySlipQt.log as log
log = log.Log('pyslipqt.log')

import pySlipQt.open_street_map as tiles


######
# Various demo constants
######

# where the OSM tiles are cached on disk
TilesDir = 'test_osm_tiles'

DemoName = 'OSM Tiles Cache Test'
DemoVersion = '0.1'

DemoWidth = 300
DemoHeight = 250


class AppFrame(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setGeometry(300, 300, DemoWidth, DemoHeight)
        self.setWindowTitle('%s %s' % (DemoName, DemoVersion))
        self.show()

        unittest.main()

    def onClose(self, event):
        self.Destroy()

class TestOSMTiles(unittest.TestCase):

    # for OSM tiles
    TileWidth = 256
    TileHeight = 256

    def testSimple(self):
        """Simple tests."""

        # read all tiles in all rows of all levels
        cache = tiles.Tiles(tiles_dir=TilesDir)
        for level in cache.levels:
            cache.UseLevel(level)
            info = cache.GetInfo(level)
            if info:
                (width_px, height_px, ppd_x, ppd_y) = info
                num_tiles_width = int(width_px / self.TileWidth)
                num_tiles_height = int(height_px / self.TileHeight)
                y = 0
                for x in range(num_tiles_width):
#                    for y in range(num_tiles_height):
                        bmp = cache.GetTile(x, y)
                        msg = "Can't find tile (%d,%d,%d)!?" % (level, x, y)
                        self.assertFalse(bmp is None, msg)
            else:
                print('level %d not available' % level)

    def XtestErrors(self):
        """Test possible errors."""

        # check that using level outside map levels returns None
        cache = tiles.Tiles(tiles_dir=TilesDir)
        level = cache.levels[-1] + 1      # get level # that DOESN'T exist
        info = cache.UseLevel(level)
        self.assertTrue(info is None,
                        'Using bad level (%d) got info=%s' % (level, str(info)))

        # check that reading tile outside map returns None
        cache = tiles.Tiles(tiles_dir=TilesDir)
        level = cache.levels[0]
        info = cache.UseLevel(level)
        (width_px, height_px, ppd_x, ppd_y) = info
        num_tiles_width = int(width_px / self.TileWidth)
        num_tiles_height = int(height_px / self.TileHeight)
        self.assertFalse(info is None,
                        'Using good level (%d) got info=%s' % (level, str(info)))
# OSM returns an empty tile if you request outside map limits
#        bmp = cache.GetTile(num_tiles_width, num_tiles_height)
#        self.assertTrue(bmp is None,
#                        'Using bad coords (%d,%d) got bmp=%s'
#                        % (num_tiles_width, num_tiles_height, str(bmp)))
        info = cache.UseLevel(1)
        bmp = cache.GetTile(0, 0)
        bmp.SaveFile('xyzzy00.jpg', wx.BITMAP_TYPE_JPEG)
        bmp = cache.GetTile(0, 1)
        bmp.SaveFile('xyzzy01.jpg', wx.BITMAP_TYPE_JPEG)
        bmp = cache.GetTile(1, 0)
        bmp.SaveFile('xyzzy10.jpg', wx.BITMAP_TYPE_JPEG)
        bmp = cache.GetTile(1, 1)
        bmp.SaveFile('xyzzy11.jpg', wx.BITMAP_TYPE_JPEG)

    def XtestConvert(self):
        """Test geo2map conversions.

        This can't be automatic, it's a 'by hand' thing.
        So it's generally turned off.
        """

        import time

        cache = tiles.Tiles(tiles_dir=TilesDir)

        # get tile covering Greenwich observatory
        #xgeo = -0.0005  # Greenwich observatory
        #ygeo = 51.4768534
        xgeo = 7.605916 # Deutsches Eck
        ygeo = 50.364444
        for level in [0, 1, 2, 3, 4]:
            info = cache.UseLevel(level)
            (xtile, ytile) = cache.Geo2Tile(xgeo, ygeo)
            bmp = cache.GetTile(int(xtile), int(ytile))

            pt_px_x = int((xtile - int(xtile)) * cache.tile_size_x)
            pt_px_y = int((ytile - int(ytile)) * cache.tile_size_y)

            dc = wx.MemoryDC()
            dc.SelectObject(bmp)
            text = "o"
            (tw, th) = dc.GetTextExtent(text)
            dc.DrawText(text, pt_px_x-tw/2,  pt_px_y-th/2)
            dc.SelectObject(wx.NullBitmap)

            bmp.SaveFile('xyzzy_%d.jpg' % level, wx.BITMAP_TYPE_JPEG)
        # we have to delay for internet response
        time.sleep(30)


log(DemoName)
app = QApplication(sys.argv)
ex = AppFrame()
sys.exit(app.exec_())

