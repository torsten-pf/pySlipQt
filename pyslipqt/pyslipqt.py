"""
A "slip map" widget for PyQt5.

Some semantics:
    map   the whole map
    view  is the view of the map through the widget
          (view may be smaller than map, or larger)
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

        # view and map limits
        self.view_offset_x = 0
        self.view_offset_y = 0
        self.view_width = 0     
        self.view_height = 0

        # set tile levels stuff - allowed levels, etc
        self.max_level = max(tile_src.levels)
        self.min_level = min(tile_src.levels)

        self.tile_size_x = tile_src.tile_size_x
        self.tile_size_y = tile_src.tile_size_y

        # define position and tile coords of the "key" tile
        self.key_tile_left = 0      # tile coordinates of key tile
        self.key_tile_top = 0
        self.key_tile_xoffset = 0   # view coordinates of key tile wrt view
        self.key_tile_yoffset = 0

        self.left_mbutton_down = False
        self.mid_mbutton_down = False
        self.right_mbutton_down = False

        self.start_drag_x = None
        self.start_drag_y = None

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(self.TileWidth, self.TileHeight)

        tile_src.setCallback(self.update)

        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.lightGray)
        self.setPalette(p)

#        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        b = event.button()
        if b == Qt.NoButton:
            print('mousePressEvent: button=Qt.NoButton')
        elif b == Qt.LeftButton:
            print('mousePressEvent: button=Qt.LeftButton')
            self.left_mbutton_down = True
        elif b == Qt.MidButton:
            print('mousePressEvent: button=Qt.MidButton')
            self.mid_mbutton_down = True
        elif b == Qt.RightButton:
            print('mousePressEvent: button=Qt.RightButton')
            self.right_mbutton_down = True
        else:
            print('mousePressEvent: unknown button')
         
    def mouseReleaseEvent(self, event):
        b = event.button()
        if b == Qt.NoButton:
            print('mouseReleaseEvent: button=Qt.NoButton')
        elif b == Qt.LeftButton:
            print('mouseReleaseEvent: button=Qt.LeftButton')
            self.left_mbutton_down = False
            self.start_drag_x = None    # end drag, if any
            self.start_drag_y = None
        elif b == Qt.MidButton:
            print('mouseReleaseEvent: button=Qt.MidButton')
            self.mid_mbutton_down = False
        elif b == Qt.RightButton:
            print('mouseReleaseEvent: button=Qt.RightButton')
            self.right_mbutton_down = False
        else:
            print('mouseReleaseEvent: unknown button')
 
    def mouseDoubleClickEvent(self, event):
        b = event.button()
        if b == Qt.NoButton:
            print('mouseDoubleClickEvent: button=Qt.NoButton')
        elif b == Qt.LeftButton:
            print('mouseDoubleClickEvent: button=Qt.LeftButton')
        elif b == Qt.MidButton:
            print('mouseDoubleClickEvent: button=Qt.MidButton')
        elif b == Qt.RightButton:
            print('mouseDoubleClickEvent: button=Qt.RightButton')
        else:
            print('mouseDoubleClickEvent: unknown button')
 
    def mouseMoveEvent(self, event):
        """Handle a mouse move event."""

        x = event.x()
        y = event.y()

        if self.left_mbutton_down:
            if self.start_drag_x:       # if we are already dragging
                delta_x = self.start_drag_x - x
                delta_y = self.start_drag_y - y

                if self.tile_src.wrap_x:
                    # wrapping in X direction, move 'key' tile
                    self.key_tile_xoffset -= delta_x
                    # normalize the 'key' tile coordinates
                    while self.key_tile_xoffset > 0:
                        self.key_tile_xoffset -= self.tile_size_x
                        self.key_tile_left += 1
                        self.key_tile_left %= self.num_tiles_x
                    while self.key_tile_xoffset <= -self.tile_size_x:
                        self.key_tile_xoffset += self.tile_size_x
                        self.key_tile_left -= 1
                        self.key_tile_left = (self.key_tile_left + self.num_tiles_x) % self.num_tiles_x
                else:
                    # if view > map, don't drag
                    # map > view, allow drag
#                    self.view_offset_x += self.start_drag_x - x
                    pass

                if self.tile_src.wrap_y:
                    # wrapping in Y direction, move 'key' tile
                    self.key_tile_yoffset -= delta_y
                    # normalize the 'key' tile coordinates
                    while self.key_tile_yoffset > 0:
                        self.key_tile_yoffset -= self.tile_size_y
                        self.key_tile_top += 1
                        self.key_tile_top %= self.num_tiles_y
                    while self.key_tile_yoffset <= -self.tile_size_y:
                        self.key_tile_yoffset += self.tile_size_y
                        self.key_tile_top -= 1
                        self.key_tile_top = (self.key_tile_top + self.num_tiles_y) % self.num_tiles_y
                else:
                    # if view > map, don't drag
                    # map > view, allow drag
#                    self.view_offset_y += self.start_drag_y - y
                    pass

                self.update()

            self.start_drag_x = x
            self.start_drag_y = y

    def keyPressEvent(self, event):
        """Capture a keyboard event."""

        print(f'key press event={event.key()}')

    def keyReleaseEvent(self, event):

        print(f'key release event={event.key()}')

    def wheelEvent(self, event):
        """Handle a mouse wheel rotation."""

        if event.angleDelta().y() < 0:
            new_level = self.level + 1
        else:
            new_level = self.level - 1
        self.use_level(new_level)

    def use_level(self, level):
        """Try to use new map level.

        level  the new level to use

        Returns True if level change is OK, else False.
        """

        result = self.tile_src.UseLevel(level)
        if result:
            self.level = level
            (self.num_tiles_x, self.num_tiles_y, _, _) = self.tile_src.GetInfo(level)
            self.update()
        return result

    def resizeEvent(self, event):
        """Widget resized, recompute some state."""

        # new widget size
        self.view_width = self.width()
        self.view_height = self.height()

        # recalculate the "top left" tile stuff
        self.recalc_wrap()

    def recalc_wrap(self):
        """Recalculate the "top left" tile information."""

        pass

    def paintEvent(self, event):
        """Draw the base map and drawlist on top."""

        print(f'paintEvent: self.key_tile_left={self.key_tile_left}, self.key_tile_xoffset={self.key_tile_xoffset}')

        # figure out how to draw tiles, set up 'row_list' and 'col_list' which
        # are list of tile coords to draw (row and colums)
        col_list = []
        x_coord = self.key_tile_left
        x_pix_start = self.key_tile_xoffset
        while x_pix_start < self.view_width:
            col_list.append(x_coord)
            if not self.tile_src.wrap_x and x_coord >= self.num_tiles_x-1:
                break
            x_coord = (x_coord + 1) % self.num_tiles_x
            x_pix_start += self.tile_src.tile_size_x

        row_list = []
        y_coord = self.key_tile_top
        y_pix_start = self.key_tile_yoffset
        while y_pix_start < self.view_height:
            row_list.append(y_coord)
            if not self.tile_src.wrap_y and y_coord >= self.num_tiles_y-1:
                break
            y_coord = (y_coord + 1) % self.num_tiles_y
            y_pix_start += self.tile_src.tile_size_y

#        # figure out how to draw tiles
#        if self.view_offset_x < 0:
#            if self.wrap_x:
#                # View > Map in X - wrap in X direction
#                pass
#            else:
#                # View > Map in X - centre in X direction
#                col_list = range(self.tile_src.num_tiles_x)
#                x_pix_start = -self.view_offset_x
#        else:
#            # Map > View - determine layout in X direction
#            start_x_tile = int(self.view_offset_x / self.tile_size_x)
#            stop_x_tile = int((self.view_offset_x + self.view_width
#                               + self.tile_size_x - 1) / self.tile_size_x)
#            stop_x_tile = min(self.tile_src.num_tiles_x-1, stop_x_tile) + 1
#            col_list = range(start_x_tile, stop_x_tile)
#            x_pix_start = start_x_tile * self.tile_size_y - self.view_offset_x
#
#        if self.view_offset_y < 0:
#            # View > Map in Y - centre in Y direction
#            row_list = range(self.tile_src.num_tiles_y)
#            y_pix_start = -self.view_offset_y
#        else:
#            # Map > View - determine layout in Y direction
#            start_y_tile = int(self.view_offset_y / self.tile_size_y)
#            stop_y_tile = int((self.view_offset_y + self.view_height
#                               + self.tile_size_y - 1) / self.tile_size_y)
#            stop_y_tile = min(self.tile_src.num_tiles_y-1, stop_y_tile) + 1
#            row_list = range(start_y_tile, stop_y_tile)
#            y_pix_start = start_y_tile * self.tile_size_y - self.view_offset_y

        # start pasting tiles onto the view
        painter = QPainter()
        painter.begin(self)

        x_pix = self.key_tile_xoffset
        for x in col_list:
            y_pix = self.key_tile_yoffset
            for y in row_list:
                QPainter.drawPixmap(painter, x_pix, y_pix,
                                    self.tile_src.GetTile(x, y))
                y_pix += self.tile_size_y
            x_pix += self.tile_size_x

        painter.end()
