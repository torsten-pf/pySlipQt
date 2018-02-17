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
        self.x = None
        self.y = None

        # set tile levels stuff - allowed levels, etc
        self.max_level = max(tile_src.levels)
        self.min_level = min(tile_src.levels)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(self.TileWidth, self.TileHeight)

        tile_src.setCallback(self.available_callback)

        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.lightGray)
        self.setPalette(p)

    def use_level(self, level):
        self.level = level
        self.tile_src.UseLevel(level)
        (self.num_tiles_x, self.num_tiles_y, _, _) = self.tile_src.GetInfo(self.level)

    def set_xy(self, x, y):
        self.x = x
        self.y = y

    def available_callback(self):
        self.update()

    def paintEvent(self, e):
        """Draw the base map and drawlist on top."""

        # get canvas width and height
        w = self.width()
        h = self.height()

        # figure out the maximum w+h tile extents
        num_x = min(self.num_tiles_x, int((w + self.TileWidth - 1) / self.TileWidth))
        num_y = min(self.num_tiles_y, int((h + self.TileHeight - 1) / self.TileHeight))

        # put image(s) into canvas
        painter = QPainter()
        painter.begin(self)
        pixmap = self.pixmap()
        for y in range(num_y):
            for x in range(num_x):
                QPainter.drawPixmap(painter, x*self.TileWidth, y*self.TileHeight, self.tile_src.GetTile(x, y))
        painter.end()
