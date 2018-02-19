"""
A "slip map" widget for PyQt5.
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QSizePolicy
from PyQt5.QtGui import QPainter

# if we don't have log.py, don't crash
try:
#    from . import log
    import log
    log = log.Log('pyslipqt.log')
except AttributeError:
    # means log already set up
    pass
except ImportError as e:
    # if we don't have log.py, don't crash
    # fake all log(), log.debug(), ... calls
    def logit(*args, **kwargs):
        pass
    log = logit
    log.debug = logit
    log.info = logit
    log.warn = logit
    log.error = logit
    log.critical = logit


# version number of the widget
__version__ = '0.1.0'


class PySlipQt(QLabel):

    TileWidth = 256
    TileHeight = 256

    def __init__(self, parent, tile_src, start_level=0, **kwargs):
        """Initialize the pySlipQt widget.

        parent       the GUI parent widget
        tile_src     a Tiles object, source of tiles
        start_level  level to initially display
        kwargs       keyword args passed through to the underlying QLabel
        """

        super().__init__(parent)

        self.tile_src = tile_src

        # the tile coordinates
        self.level = start_level
        self.view_offset_x = 0
        self.view_offset_y = 0

        # set tile levels stuff - allowed levels, etc
        self.max_level = max(tile_src.levels)
        self.min_level = min(tile_src.levels)

        self.tile_size_x = tile_src.tile_size_x
        self.tile_size_y = tile_src.tile_size_y

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(self.TileWidth, self.TileHeight)

        tile_src.setCallback(self.update)

        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.lightGray)
        self.setPalette(p)

    def use_level(self, level):
        self.level = level
        self.tile_src.UseLevel(level)
        (self.num_tiles_x,
         self.num_tiles_y, _, _) = self.tile_src.GetInfo(self.level)

    def set_xy(self, x, y):
        self.view_offset_x = x
        self.view_offset_y = y

    def paintEvent(self, e):
        """Draw the base map and drawlist on top."""

        # get widget size
        w = self.width()
        h = self.height()

        # figure out how to draw tiles
        if self.view_offset_x < 0:
            # View > Map in X - centre in X direction
            col_list = range(self.tile_src.num_tiles_x)
            x_pix_start = -self.view_offset_x
        else:
            # Map > View - determine layout in X direction
            start_x_tile = int(self.view_offset_x / self.tile_size_x)
            stop_x_tile = int((self.view_offset_x + w
                               + self.tile_size_x - 1) / self.tile_size_x)
            stop_x_tile = min(self.tile_src.num_tiles_x-1, stop_x_tile) + 1
            col_list = range(start_x_tile, stop_x_tile)
            x_pix_start = start_x_tile * self.tile_size_y - self.view_offset_x

        if self.view_offset_y < 0:
            # View > Map in Y - centre in Y direction
            row_list = range(self.tile_src.num_tiles_y)
            y_pix_start = -self.view_offset_y
        else:
            # Map > View - determine layout in Y direction
            start_y_tile = int(self.view_offset_y / self.tile_size_y)
            stop_y_tile = int((self.view_offset_y + h
                               + self.tile_size_y - 1) / self.tile_size_y)
            stop_y_tile = min(self.tile_src.num_tiles_y-1, stop_y_tile) + 1
            row_list = range(start_y_tile, stop_y_tile)
            y_pix_start = start_y_tile * self.tile_size_y - self.view_offset_y

        # start pasting tiles onto the view
        # use x_pix and y_pix to place tiles
        painter = QPainter()
        painter.begin(self)

        x_pix = x_pix_start
        for x in col_list:
            y_pix = y_pix_start
            for y in row_list:
                QPainter.drawPixmap(painter, x_pix, y_pix,
                                    self.tile_src.GetTile(x, y))
                y_pix += self.tile_size_y
            x_pix += self.tile_size_x

        painter.end()
