"""
A "slip map" widget for PyQt5.

Some semantics:
    map   the whole map
    view  is the view of the map through the widget
          (view may be smaller than map, or larger)
"""

from PyQt5.QtCore import Qt, QTimer, QPoint, QPointF
from PyQt5.QtWidgets import QLabel, QSizePolicy, QWidget
from PyQt5.QtGui import QPainter, QColor, QPixmap, QPen, QFont, QFontMetrics

# if we don't have log.py, don't crash
try:
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


######
# A layer class - encapsulates all layer data.
######

class _Layer(object):
    """A Layer object."""

    DefaultDelta = 50      # default selection delta

    def __init__(self, id=0, painter=None, data=None, map_rel=True,
                 visible=False, show_levels=None, selectable=False,
                 name="<no name given>", type=None):
        """Initialise the Layer object.

        id           unique layer ID
        painter      render function
        data         the layer data
        map_rel      True if layer is map-relative, else layer-relative
        visible      layer visibility
        show_levels  list of levels at which to auto-show the level
        selectable   True if select operates on this layer, else False
        name         the name of the layer (for debug)
        type         a layer 'type' flag
        """

        self.painter = painter          # routine to draw layer
        self.data = data                # data that defines the layer
        self.map_rel = map_rel          # True if layer is map relative
        self.visible = visible          # True if layer visible
        self.show_levels = show_levels  # None or list of levels to auto-show
        self.selectable = selectable    # True if we can select on this layer
        self.delta = self.DefaultDelta  # minimum distance for selection
        self.name = name                # name of this layer
        self.type = type                # type of layer
        self.id = id                    # ID of this layer

    def __str__(self):
        return ('<pyslip Layer: id=%d, name=%s, map_rel=%s, visible=%s'
                % (self.id, self.name, str(self.map_rel), str(self.visible)))


######
# The pySlipQt widget.
######

#class PySlipQt(QLabel):
class PySlipQt(QWidget):

    # widget default background colour
    Background_R = 192
    Background_G = 192
    Background_B = 192
    Background = f'rgb({Background_R}, {Background_G}, {Background_B})'

    # list of valid placement values
    valid_placements = ['cc', 'nw', 'cn', 'ne', 'ce',
                        'se', 'cs', 'sw', 'cw', None, False, '']

    # panel background colour
    BackgroundColour = '#808080'

    # default point attributes - map relative
    DefaultPointPlacement = 'cc'
    DefaultPointRadius = 3
#    DefaultPointColour = Qt.red
    DefaultPointColour = 'red'
    DefaultPointOffsetX = 0
    DefaultPointOffsetY = 0
    DefaultPointData = None

    # default point attributes - view relative
    DefaultPointViewPlacement = 'cc'
    DefaultPointViewRadius = 3
#    DefaultPointViewColour = Qt.red
    DefaultPointViewColour = 'red'
    DefaultPointViewOffsetX = 0
    DefaultPointViewOffsetY = 0
    DefaultPointViewData = None

    # default image attributes - map relative
    DefaultImagePlacement = 'nw'
    DefaultImageRadius = 0
#    DefaultImageColour = Qt.black
    DefaultImageColour = 'black'
    DefaultImageOffsetX = 0
    DefaultImageOffsetY = 0
    DefaultImageData = None

    # default image attributes - view relative
    DefaultImageViewPlacement = 'nw'
    DefaultImageViewRadius = 0
#    DefaultImageViewColour = Qt.black
    DefaultImageViewColour = 'black'
    DefaultImageViewOffsetX = 0
    DefaultImageViewOffsetY = 0
    DefaultImageViewData = None

    # default text attributes - map relative
    DefaultTextPlacement = 'nw'
    DefaultTextRadius = 2
#    DefaultTextColour = Qt.black
    DefaultTextColour = 'black'
#    DefaultTextTextColour = Qt.black
    DefaultTextTextColour = 'black'
    DefaultTextOffsetX = 5
    DefaultTextOffsetY = 1
    DefaultTextFontname = 'Helvetica'
    DefaultTextFontSize = 10
    DefaultTextData = None

    # default text attributes - view relative
    DefaultTextViewPlacement = 'nw'
    DefaultTextViewRadius = 0
#    DefaultTextViewColour = Qt.black
    DefaultTextViewColour = 'black'
#    DefaultTextViewTextColour = Qt.black
    DefaultTextViewTextColour = 'black'
    DefaultTextViewOffsetX = 0
    DefaultTextViewOffsetY = 0
    DefaultTextViewFontname = 'Helvetica'
    DefaultTextViewFontSize = 10
    DefaultTextViewData = None

    # default polygon attributes - map view
    DefaultPolygonPlacement = 'cc'
    DefaultPolygonWidth = 1
#    DefaultPolygonColour = Qt.red
    DefaultPolygonColour = 'red'
    DefaultPolygonClose = False
    DefaultPolygonFilled = False
    DefaultPolygonFillcolour = 'blue'
    DefaultPolygonOffsetX = 0
    DefaultPolygonOffsetY = 0
    DefaultPolygonData = None

    # default polygon attributes - view relative
    DefaultPolygonViewPlacement = 'nw'
    DefaultPolygonViewWidth = 1
#    DefaultPolygonViewColour = Qt.red
    DefaultPolygonViewColour = 'red'
    DefaultPolygonViewClose = False
    DefaultPolygonViewFilled = False
    DefaultPolygonViewFillcolour = 'blue'
    DefaultPolygonViewOffsetX = 0
    DefaultPolygonViewOffsetY = 0
    DefaultPolygonViewData = None

    # default polyline attributes - map view
    DefaultPolylinePlacement = 'cc'
    DefaultPolylineWidth = 1
#    DefaultPolylineColour = Qt.red
    DefaultPolylineColour = 'red'
    DefaultPolylineOffsetX = 0
    DefaultPolylineOffsetY = 0
    DefaultPolylineData = None

    # default polyline attributes - view relative
    DefaultPolylineViewPlacement = 'cc'
    DefaultPolylineViewWidth = 1
#    DefaultPolylineViewColour = Qt.red
    DefaultPolylineViewColour = 'red'
    DefaultPolylineViewOffsetX = 0
    DefaultPolylineViewOffsetY = 0
    DefaultPolylineViewData = None

    # layer type values
    (TypePoint, TypeImage, TypeText, TypePolygon, TypePolyline) = range(5)


    def __init__(self, parent, tile_src, start_level, **kwargs):
        """Initialize the pySlipQt widget.

        parent       the GUI parent widget
        tile_src     a Tiles object, source of tiles
        start_level  level to initially display
        kwargs       keyword args passed through to the underlying QLabel
        """

        super().__init__(parent, **kwargs)    # inherit all parent object setup

        # set default widget background colour
        self.setStyleSheet(f'background-color: {PySlipQt.Background};')

        # remember the tile source object
        self.tile_src = tile_src

        # the tile coordinates
        self.level = start_level

        # view and map limits
        self.view_width = 0     # width/height of the view
        self.view_height = 0    # changes when the widget changes size

        self.map_width = 0      # width/height of the virtual map (not wrapped)
        self.map_height = 0     # in pixels (changes when zoom level changes)

        # set tile and levels stuff
        self.max_level = max(tile_src.levels)   # max level displayed
        self.min_level = min(tile_src.levels)   # min level displayed
        self.tile_width = tile_src.tile_size_x  # width of tile in pixels
        self.tile_height = tile_src.tile_size_y # height of tile in pixels
        self.num_tiles_x = tile_src.num_tiles_x # number of unwrapped tiles in X direction
        self.num_tiles_y = tile_src.num_tiles_y # number of unwrapped tiles in Y direction
        self.wrap_x = tile_src.wrap_x           # True if tiles wrap in X direction
        self.wrap_y = tile_src.wrap_y           # True if tiles wrap in Y direction

        self.next_layer_id = 1                  # source of unique layer IDs
        self.tiles_max_level = max(tile_src.levels) # maximum level in current tile source
        self.tiles_min_level = min(tile_src.levels) # minimum level in current tile source

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

        # layer state cariables
        self.layer_mapping = {}                 # maps layer ID to layer data
        self.layer_z_order = []                 # layer Z order, contains layer IDs

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(self.tile_width, self.tile_height)

        tile_src.setCallback(self.update)

        # do a "resize" after this function, does recalc_wrap_limits()
        QTimer.singleShot(10, self.resizeEvent)

#        # set background colour of widget
#        self.setAutoFillBackground(True)
#        p = self.palette()
#        p.setColor(self.backgroundRole(), PySlipQt.Background)
#        self.setPalette(p)

#        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        b = event.button()
        if b == Qt.NoButton:
            log('mousePressEvent: button=Qt.NoButton')
        elif b == Qt.LeftButton:
            log('mousePressEvent: button=Qt.LeftButton')
            self.left_mbutton_down = True
        elif b == Qt.MidButton:
            log('mousePressEvent: button=Qt.MidButton')
            self.mid_mbutton_down = True
        elif b == Qt.RightButton:
            log('mousePressEvent: button=Qt.RightButton')
            self.right_mbutton_down = True
        else:
            log('mousePressEvent: unknown button')
         
    def mouseReleaseEvent(self, event):
        b = event.button()
        if b == Qt.NoButton:
            log('mouseReleaseEvent: button=Qt.NoButton')
        elif b == Qt.LeftButton:
            log('mouseReleaseEvent: button=Qt.LeftButton')
            self.left_mbutton_down = False
            self.start_drag_x = None    # end drag, if any
            self.start_drag_y = None
        elif b == Qt.MidButton:
            log('mouseReleaseEvent: button=Qt.MidButton')
            self.mid_mbutton_down = False
        elif b == Qt.RightButton:
            log('mouseReleaseEvent: button=Qt.RightButton')
            self.right_mbutton_down = False
        else:
            log('mouseReleaseEvent: unknown button')
 
    def mouseDoubleClickEvent(self, event):
        b = event.button()
        if b == Qt.NoButton:
            log('mouseDoubleClickEvent: button=Qt.NoButton')
        elif b == Qt.LeftButton:
            log('mouseDoubleClickEvent: button=Qt.LeftButton')
        elif b == Qt.MidButton:
            log('mouseDoubleClickEvent: button=Qt.MidButton')
        elif b == Qt.RightButton:
            log('mouseDoubleClickEvent: button=Qt.RightButton')
        else:
            log('mouseDoubleClickEvent: unknown button')
 
    def mouseMoveEvent(self, event):
        """Handle a mouse move event."""

        x = event.x()
        y = event.y()

        if self.left_mbutton_down:
            if self.start_drag_x:       # if we are already dragging
                delta_x = self.start_drag_x - x
                delta_y = self.start_drag_y - y
                log(f'mouseMoveEvent: delta_x={delta_x}, delta_y={delta_y}')
                self.normalize_view_drag(delta_x, delta_y)  # normalize the "key" tile
                self.update()                               # force a repaint

            self.start_drag_x = x
            self.start_drag_y = y

    def normalize_view_drag(self, delta_x=None, delta_y=None):
        """After drag, set "key" tile correctly.

        delta_x  the X amount dragged (pixels), None if not dragged in X
        delta_y  the Y amount dragged (pixels), None if not dragged in Y
        """

        if self.wrap_x:
            # wrapping in X direction, move 'key' tile
            self.key_tile_xoffset -= delta_x
            while self.key_tile_xoffset > 0:
                # 'key' tile too far right
                self.key_tile_left -= 1
                self.key_tile_xoffset -= self.tile_width
            self.key_tile_left %= self.num_tiles_x
    
            while self.key_tile_xoffset <= -self.tile_width:
                # 'key' tile too far left
                self.key_tile_left += 1
                self.key_tile_xoffset += self.tile_width
            self.key_tile_left = (self.key_tile_left + self.num_tiles_x) % self.num_tiles_x
        else:
            log(f'DRAG: before, self.key_tile_left={self.key_tile_left}, self.key_tile_xoffset={self.key_tile_xoffset}')
            # if view > map, don't drag, ensure centred
            if self.map_width < self.view_width:
                self.key_tile_xoffset = (self.view_width - self.map_width) // 2
            else:
                # remember old 'key' tile left value
                old_left = self.key_tile_left

                # map > view, allow drag, but don't go past the edge
                self.key_tile_xoffset -= delta_x

                while self.key_tile_xoffset > 0:
                    # 'key' tile too far right
                    self.key_tile_left -= 1
                    self.key_tile_xoffset -= self.tile_width
                self.key_tile_left %= self.num_tiles_x
        
                while self.key_tile_xoffset <= -self.tile_width:
                    # 'key' tile too far left
                    self.key_tile_left += 1
                    self.key_tile_xoffset += self.tile_width
                self.key_tile_left = (self.key_tile_left + self.num_tiles_x) % self.num_tiles_x

                if delta_x < 0:
                    # was dragged to the right, don't allow left edge to show
                    log(f'DRAG RIGHT: self.key_tile_left={self.key_tile_left}, self.key_tile_xoffset={self.key_tile_xoffset}')
                    if self.key_tile_left > old_left:
                        self.key_tile_left = 0
                        self.key_tile_xoffset = 0
                    log(f'AFTER RIGHT: self.key_tile_left={self.key_tile_left}, self.key_tile_xoffset={self.key_tile_xoffset}')
                else:
                    log(f'DRAG LR: .key_tile_left={self.key_tile_left}, .key_tile_xoffset={self.key_tile_xoffset}')
                    # if dragged too far, reset key tile data
                    if self.key_tile_left > self.max_key_left:
                        self.key_tile_left = self.max_key_left
                        self.key_tile_xoffset = self.max_key_xoffset
                    elif self.key_tile_left == self.max_key_left:
                        if self.key_tile_xoffset < self.max_key_xoffset:
                            self.key_tile_xoffset = self.max_key_xoffset

        if self.wrap_y:
            # wrapping in Y direction, move 'key' tile
            self.key_tile_yoffset -= delta_y
        else:
            # if view > map, don't drag, ensure centred
            if self.map_height < self.view_height:
                self.key_tile_yoffset = (self.view_height - self.map_height) // 2
            else:
                # remember old 'key' tile left value
                old_top = self.key_tile_top

                # map > view, allow drag, but don't go past the edge
                self.key_tile_yoffset -= delta_y

                while self.key_tile_yoffset > 0:
                    # 'key' tile too far right
                    self.key_tile_top -= 1
                    self.key_tile_yoffset -= self.tile_height
                self.key_tile_top %= self.num_tiles_y
        
                while self.key_tile_yoffset <= -self.tile_height:
                    # 'key' tile too far left
                    self.key_tile_top += 1
                    self.key_tile_yoffset += self.tile_height
                self.key_tile_top = (self.key_tile_top + self.num_tiles_y) % self.num_tiles_y

                if delta_y < 0:
                    # was dragged to the top, don't allow bottom edge to show
                    if self.key_tile_top > old_top:
                        self.key_tile_top = 0
                        self.key_tile_yoffset = 0
                else:
                    log(f'DRAG UD: .key_tile_top={self.key_tile_top}, .key_tile_yoffset={self.key_tile_yoffset}')
                    # if dragged too far, reset key tile data
                    if self.key_tile_top > self.max_key_top:
                        self.key_tile_top = self.max_key_top
                        self.key_tile_yoffset = self.max_key_yoffset
                    elif self.key_tile_top == self.max_key_top:
                        if self.key_tile_yoffset < self.max_key_yoffset:
                            self.key_tile_yoffset = self.max_key_yoffset

    def keyPressEvent(self, event):
        """Capture a keyboard event."""

        log(f'key press event={event.key()}')

    def keyReleaseEvent(self, event):

        log(f'key release event={event.key()}')

    def wheelEvent(self, event):
        """Handle a mouse wheel rotation."""

        log(f"wheelEvent: {'UP' if event.angleDelta().y() < 0 else 'DOWN'}")

        if event.angleDelta().y() < 0:
            new_level = self.level + 1
        else:
            new_level = self.level - 1
        self.use_level(new_level)

    def use_level(self, level):
        """Use new map level.

        level  the new level to use

        This code will try to maintain the centre of the view at the same
        GEO coordinates, if possible.  The "key" tile is updated.

        Returns True if level change is OK, else False.
        """

        return self.zoom_level(level)

    def resizeEvent(self, event=None):
        """Widget resized, recompute some state."""

        # new widget size
        self.view_width = self.width()
        self.view_height = self.height()

        log(f'resizeEvent: event={event}, width={self.view_width}, height={self.view_height}')

        # recalculate the "top left" tile stuff
        self.recalc_wrap_limits()

        self.normalize_view_drag(0, 0)

    def recalc_wrap_limits(self):
        """Recalculate the maximum "key" tile information.
        
        Called if widget changes level or resized.
        .map_width, .map_height, .view_width and .view_height have been set.
        """

        # figure out the maximum 'key' tile coordinates
        tiles_in_view = self.view_width // self.tile_width
        left_margin = self.view_width - tiles_in_view*self.tile_width
        self.max_key_xoffset = -(self.tile_width - left_margin)
        self.max_key_left = self.num_tiles_x - tiles_in_view - 1

        tiles_in_view = self.view_height // self.tile_height
        margin = self.view_height - tiles_in_view*self.tile_height
        self.max_key_yoffset = -(self.tile_height - margin)
        self.max_key_top = self.num_tiles_y - tiles_in_view - 1

    def paintEvent(self, event):
        """Draw the base map and then the layers on top."""

        log(f'paintEvent: self.key_tile_left={self.key_tile_left}, self.key_tile_xoffset={self.key_tile_xoffset}')
        log(f'self.view_width={self.view_width}, self.view_height={self.view_height}')
        log(f'tile_width={self.tile_width}, tile_height={self.tile_height}')

        ######
        # The "key" tile position is maintained by other code, we just
        # assume it's set.  Figure out how to draw tiles, set up 'row_list' and
        # 'col_list' which are list of tile coords to draw (row and colums).
        ######

        col_list = []
        x_coord = self.key_tile_left
        x_pix_start = self.key_tile_xoffset
        while x_pix_start < self.view_width:
            log(f'loop: x_pix_start={x_pix_start}, self.view_width={self.view_width}')
            col_list.append(x_coord)
            if not self.wrap_x and x_coord >= self.num_tiles_x-1:
                break
            x_coord = (x_coord + 1) % self.num_tiles_x
            x_pix_start += self.tile_height

        row_list = []
        y_coord = self.key_tile_top
        y_pix_start = self.key_tile_yoffset
        while y_pix_start < self.view_height:
            row_list.append(y_coord)
            if not self.wrap_y and y_coord >= self.num_tiles_y-1:
                break
            y_coord = (y_coord + 1) % self.num_tiles_y
            y_pix_start += self.tile_height

        log(f'col_list={col_list}, row_list={row_list}')

        ######
        # Ready to update the view
        ######

        # prepare the canvas
        painter = QPainter()
        painter.begin(self)

        # paste all background tiles onto the view
        x_pix = self.key_tile_xoffset
        for x in col_list:
            y_pix = self.key_tile_yoffset
            for y in row_list:
#                QPainter.drawPixmap(painter, x_pix, y_pix,
#                                    self.tile_src.GetTile(x, y))
                painter.drawPixmap(x_pix, y_pix,
                                    self.tile_src.GetTile(x, y))
                log(f'drawing tile ({x}, {y}) at {x_pix}, {y_pix}')
                log(f'tile extends right to {x_pix+self.tile_width}')
                log(f'tile extends down to {y_pix+self.tile_height}')

                y_pix += self.tile_height
            x_pix += self.tile_width

        # now draw the layers
        for id in self.layer_z_order:
            l = self.layer_mapping[id]
            if l.visible and self.level in l.show_levels:
                l.painter(painter, l.data, map_rel=l.map_rel)


        log('paintEvent: end')
        painter.end()

    def tile_frac_to_parts(self, t_frac, length):
        """Split a tile coordinate into integer and fractional parts.

        frac  a fractional tile coordinate
        length  size of tile width or height

        Return (int, frac) parts of 't_frac'.
        """

        int_part = int(t_frac)
        frac_part = int((t_frac - int_part) * length)

        return (int_part, frac_part)

    def tile_parts_to_frac(self, t_coord, t_offset, length):
        """Convert a tile coord plus offset to a fractional tile value.

        t_coord   the tile integer coordinate
        t_offset  the pixel further offset
        length    the width orr height of the tile

        Returns a fractional tile coordinate.
        """

        log(f'tile_parts_to_frac: t_coord={t_coord}, t_offset={t_offset}, length={length}')
        log(f'tile_parts_to_frac: returning t_coord + t_offset/length={t_coord + t_offset/length}')
        return t_coord + t_offset/length

    def zoom_tile(self, c_tile, scale):
        """Zoom into centre tile at given scale.

        c_tile  tuple (x_frac, y_frac) of fractional tile coords for point
        scale   2.0 if zooming in, 0.5 if zooming out

        Returns a tuple (zx_frac, zy_frac) of fractional coordinates of the
        point after the zoom.
        """

        # unpack the centre tile coords
        (x_frac, y_frac) = c_tile
        log(f'zoom_tile: x_frac={x_frac}, y_frac={y_frac}')

        # convert tile fractional coords to tile # + offset
        (tile_left, tile_xoff) = self.tile_frac_to_parts(x_frac, self.tile_width)
        (tile_top, tile_yoff) = self.tile_frac_to_parts(y_frac, self.tile_height)
        log(f'zoom_tile: tile_left={tile_left}, tile_xoff={tile_xoff}')

        if scale > 1:
            # assume scale is 2
            # a simple doubling of fractional coordinates
            if tile_xoff < self.tile_width // 2:
                tile_left = tile_left * 2
                tile_xoff = tile_xoff * 2
                log(f'zoom_tile: left half double, tile_left={tile_left}, tile_xoff={tile_xoff}')
            else:
                tile_left = tile_left*2 + 1
                tile_xoff = tile_xoff*2 - self.tile_width
                log(f'zoom_tile: right half double, tile_left={tile_left}, tile_xoff={tile_xoff}')
    
            if tile_yoff < self.tile_height // 2:
                tile_top = tile_top * 2
                tile_yoff = tile_yoff * 2
            else:
                tile_top = tile_top*2 + 1
                tile_yoff = tile_yoff*2 % self.tile_height
        else:
            # assume scale is 0.5
            # a simple halving of fractional coordinates
            log(f'BEFORE: tile_left={tile_left}, tile_xoff={tile_xoff}')
            tile_left = tile_left // 2
            if tile_left % 2 == 0:
                # point in left half of 2x2
                tile_xoff = tile_xoff // 2
            else:
                # point in right half of 2x2
                tile_xoff = (tile_xoff + self.tile_width) // 2

            tile_top = tile_top // 2
            if tile_top % 2 == 0:
                # point in top half of 2x2
                tile_yoff = tile_yoff // 2
            else:
                # point in bottom half of 2x2
                tile_yoff = (tile_yoff + self.tile_height) // 2
            log(f'AFTER: tile_left={tile_left}, tile_xoff={tile_xoff}')
    
        zx_frac = self.tile_parts_to_frac(tile_left, tile_xoff, self.tile_width)
        zy_frac = self.tile_parts_to_frac(tile_top, tile_yoff, self.tile_height)

        log(f'zoom_tile: returning ({zx_frac}, {zy_frac})')

        return (zx_frac, zy_frac)

    def tile_to_key(self, z_point, x, y):
        """Get new 'key' tile data given a zoom point and a view point.

        z_point  the tile coordinates of the zoom point (zx_tile, zy_tile)
        x, y     the view coordinates of the zoom point

        Returns (key_tile_left, key_tile_xoffset, key_tile.top, key_tile_yoffset)
        which define the new 'key' tile values after a zoom.
        """

        # split out X and Y fractional coordinates
        (zx_tile, zy_tile) = z_point

        # get tile fractions from the view point to the view edges
        x_off = x / self.tile_width
        y_off = y / self.tile_height

        # get the fractional coordinates of the left and top edges
        left_coord = zx_tile - x_off/self.tile_width
        top_coord = zy_tile - y_off/self.tile_height

        # get 'key' tile coordinates
        (l_int, l_frac) = self.tile_frac_to_parts(left_coord, self.tile_width)
        key_tile_left = l_int
        key_tile_xoffset = -l_frac # * self.tile_width
        log(f'tile_to_key: l_int={l_int}, l_frac={l_frac}, key_tile_left={key_tile_left}, key_tile_xoffset={key_tile_xoffset}')

        (r_int, r_frac) = self.tile_frac_to_parts(top_coord, self.tile_height)
        key_tile_top = r_int
        key_tile_yoffset = -r_frac # * self.tile_height

        return (key_tile_left, key_tile_xoffset, key_tile_top, key_tile_yoffset)

    def view_to_tile(self, x=None, y=None):
        """Convert view coordinates to the fractional tile coordinates.

        x, y  view point coordinates in pixels (view centre is default)

        Returns a tuple (tile_x, tile_y) of fraction tile coordinates of
        the given point in the view.

            map bounds
           +---------------------------------
           |    view bounds     |
           |   +----------------+--------
           |   |     centre tile|
           |   |     +------------------+
           |   |     |          |       |
           |   |     |          | tile_y|
           |   |     |          v       |
           |---+-----+--------->o       |
           |   |     | tile_x    \      |
           |   |     |         position |
           |         |                  |
                     |                  |
                     +------------------+

        This method is the reverse of self.tile_to_view().
        """

        # handle the default - centre of the view
        if x is None:
            x = self.view_width // 2
        if y is None:
            y = self.view_height // 2

        log(f'view_to_tile: .view_width={self.view_width}, .key_tile_left={self.key_tile_left}, .key_tile_xoffset={self.key_tile_xoffset}')
        log(f'view_to_tile: .view_height={self.view_height}, .key_tile_top={self.key_tile_top}, .key_tile_yoffset={self.key_tile_yoffset}')
        log(f'view_to_tile: x={x}, y={y}')

        # work out X tile coordinate
        dx = x - self.key_tile_xoffset     # pixels from key tile left to point
        log(f'view_to_tile: dx={dx} - self.key_tile_xoffset={self.key_tile_xoffset}')
        (dx_whole, dx_off) = divmod(dx, self.tile_width)   # (a // b, a % b)
        log(f'view_to_tile: dx_whole=dx // self.tile_width={dx_whole}')
        log(f'view_to_tile: dx_off=dx % self.tile_width={dx_off}')
        tile_x = self.key_tile_left + dx_whole + dx_off/self.tile_width
        log(f'view_to_tile: tile_x=self.key_tile_left + dx_whole + dx_off/self.tile_width={tile_x}')

        # work out Y tile coordinate
        d_y = y - self.key_tile_yoffset     # pixels from key tile top to point
        dy_whole = d_y // self.tile_height  # number of complete tiles to point
        dy_off = d_y % self.tile_height     # left over piyels
        tile_y = self.key_tile_top + dy_whole + dy_off/self.tile_height

        log(f'view_to_tile: returning {(tile_x, tile_y)}')

        return (tile_x, tile_y)

    def add_layer(self, painter, data, map_rel, visible, show_levels,
                  selectable, name, type):
        """Add a generic layer to the system.

        painter      the function used to paint the layer
        data         actual layer data (depends on layer type)
        map_rel      True if points are map relative, else view relative
        visible      True if layer is to be immediately shown, else False
        show_levels  list of levels at which to auto-show the layer
        selectable   True if select operates on this layer
        name         name for this layer
        type         flag for layer 'type'

        Returns unique ID of the new layer.
        """

        # get layer ID
        id = self.next_layer_id
        self.next_layer_id += 1

        # prepare the show_level value
        if show_levels is None:
            show_levels = range(self.tiles_min_level, self.tiles_max_level+1)[:]

        # create layer, add unique ID to Z order list
        l = _Layer(id=id, painter=painter, data=data, map_rel=map_rel,
                   visible=visible, show_levels=show_levels,
                   selectable=selectable, name=name, type=type)

        self.layer_mapping[id] = l
        self.layer_z_order.append(id)

        # force display of new layer if it's visible
        if visible:
            self.update()

        return id

    def AddLayer(self, painter, data, map_rel, visible, show_levels,
                 selectable, name, type):
        """Add a generic layer to the system.

        painter      the function used to paint the layer
        data         actual layer data (depends on layer type)
        map_rel      True if points are map relative, else view relative
        visible      True if layer is to be immediately shown, else False
        show_levels  list of levels at which to auto-show the layer
        selectable   True if select operates on this layer
        name         name for this layer
        type         flag for layer 'type'

        Returns unique ID of the new layer.
        """

        # get layer ID
        id = self.next_layer_id
        self.next_layer_id += 1

        # prepare the show_level value
        if show_levels is None:
            show_levels = range(self.tiles_min_level, self.tiles_max_level+1)[:]

        # create layer, add unique ID to Z order list
        l = _Layer(id=id, painter=painter, data=data, map_rel=map_rel,
                   visible=visible, show_levels=show_levels,
                   selectable=selectable, name=name, type=type)

        self.layer_mapping[id] = l
        self.layer_z_order.append(id)

        # force display of new layer if it's visible
        if visible:
            self.update()

        return id

    ######
    # Layer drawing routines
    ######

    def DrawPointLayer(self, dc, data, map_rel):
        """Draw a points layer.

        dc       the active device context to draw on
        data     an iterable of point tuples:
                     (x, y, place, radius, colour, x_off, y_off, udata)
        map_rel  points relative to map if True, else relative to view
        """

        # get correct pex function - this handles map or view
        pex = self.PexPointView
        if map_rel:
            pex = self.PexPoint

        # draw points on map/view
        cache_colour = None     # speed up drawing mostly not changing colours

        for (x, y, place, radius, colour, x_off, y_off, udata) in data:
            (pt, ex) = pex(place, (x,y), x_off, y_off, radius)
            if ex and radius:  # don't draw if not on screen or zero radius
                if cache_colour != colour:
                    qcolour = QColor(*colour)
                    pen = QPen(qcolour, radius, Qt.SolidLine)
                    dc.setPen(pen)
                    dc.setBrush(qcolour)
                    cache_colour = colour
                (x, _, y, _) = ex
                dc.drawEllipse(QPoint(x, y), radius, radius)

    def DrawImageLayer(self, dc, images, map_rel):
        """Draw an image Layer on the view.

        dc       the active device context to draw on
        images   a sequence of image tuple sequences
                   (x,y,bmap,w,h,placement,offset_x,offset_y,idata)
        map_rel  points relative to map if True, else relative to view
        """

        # get correct pex function
        pex = self.PexExtentView
        if map_rel:
            pex = self.PexExtent

        # draw the images - speed up drawing mostly unchanging colours
        cache_colour = None

        for (lon, lat, bmap, w, h, place,
                 x_off, y_off, radius, colour, idata) in images:
            log(f'DrawImageLayer: lon={lon}, lat={lat}, w={w}, h={h}, radius={radius}, colour={colour}')
            (pt, ex) = pex(place, (lon, lat), x_off, y_off, w, h)
            log(f'DrawImageLayer: pt={pt}, ex={ex}')
            if ex:
                (ix, _, iy, _) = ex
                ix = int(ix)
                iy = int(iy)
                log(f'DrawImageLayer: drawing image at ix={ix}, iy={iy}, bmap={bmap}')
                log(f'DrawImageLayer: self.view_width={self.view_width}, self.view_height={self.view_height}')
                dc.drawPixmap(QPoint(ix, iy), bmap)

            if pt and radius:
                if cache_colour != colour:
                    log(f'DrawImageLayer: colour={colour}')
                    pen = QPen(colour, radius, Qt.SolidLine)
                    painter.setPen(pen)
                    paint.setBrush(pen)
                    cache_colour = colour
                (px, py) = pt
                log(f'DrawImageLayer: drawing circle at px={px}, py={py}')
                dc.drawEllipse(QPoint(px, py), radius, radius)

    def DrawTextLayer(self, dc, text, map_rel):
        """Draw a text Layer on the view.

        dc       the active device context to draw on
        text     a sequence of tuples:
                     (lon, lat, tdata, placement, radius, colour, fontname,
                      fontsize, offset_x, offset_y, tdata)
        map_rel  points relative to map if True, else relative to view
        """

        # get correct pex function for mode (map/view)
        pex = self.PexExtentView
        if map_rel:
            pex = self.PexExtent

        # set some caching to speed up mostly unchanging data
        cache_textcolour = None
        cache_font = None
        cache_colour = None

        # draw text on map/view
        for (lon, lat, tdata, place, radius, colour,
                textcolour, fontname, fontsize, x_off, y_off, data) in text:

            log(f'DrawTextLayer: xyzzy: lon={lon}, lat={lat}, tdata={tdata}, radius={radius}')

            # set font characteristics so we calculate text width/height
            if cache_textcolour != textcolour:
                qcolour = QColor(*textcolour)
                pen = QPen(qcolour, radius, Qt.SolidLine)
                dc.setPen(pen)
                cache_textcolour = textcolour

            if cache_font != (fontname, fontsize):
                font = QFont(fontname, fontsize)
                dc.setFont(font)
                cache_font = (fontname, fontsize)
                font_metrics = QFontMetrics(font)

            qrect = font_metrics.boundingRect(tdata)
            w = qrect.width()
            h = qrect.height()
            log(f'DrawTextLayer: tdata={tdata}, w={w}, h={h}')

            # get point + extent information (each can be None if off-view)
            (pt, ex) = pex(place, (lon, lat), x_off, y_off, w, h)
            log(f'DrawTextLayer: lon={lon}, lat={lat} -> pt={pt}, ex={ex}')
            if ex:              # don't draw text if off screen
                (lx, _, ty, _) = ex
                dc.drawText(QPointF(lx, ty), tdata)
                log(f'DrawTextLayer: drawing "{tdata}" at view ({lx},{ty})')

            if pt and radius:   # don't draw point if off screen or zero radius
                (x, y) = pt
                if cache_colour != colour:
                    qcolour = QColor(*colour)
                    pen = QPen(qcolour, radius, Qt.SolidLine)
                    dc.setPen(pen)
                    dc.setBrush(qcolour)
                    cache_colour = colour
                dc.drawEllipse(QPoint(x, y), radius, radius)
                log(f'DrawTextLayer: drawing point at view ({x},{y}), radius {radius}')

    def DrawPolygonLayer(self, dc, data, map_rel):
        """Draw a polygon layer.

        dc       the active device context to draw on
        data     an iterable of polygon tuples:
                     (p, placement, width, colour, closed,
                      filled, fillcolour, offset_x, offset_y, udata)
                 where p is an iterable of points: (x, y)
        map_rel  points relative to map if True, else relative to view
        """

        # get the correct pex function for mode (map/view)
        pex = self.PexPolygonView
        if map_rel:
            pex = self.PexPolygon

        # draw polygons
        cache_colour_width = None     # speed up mostly unchanging data
        cache_fillcolour = None

        for (p, place, width, colour, closed,
                 filled, fillcolour, x_off, y_off, udata) in data:
            (poly, extent) = pex(place, p, x_off, y_off)
            if poly:
                if cache_colour_width != (colour, width):
                    dc.SetPen(wx.Pen(colour, width=width))
                    cache_colour = (colour, width)

                if filled:
                    if cache_fillcolour != fillcolour:
                        dc.SetBrush(wx.Brush(fillcolour))
                        cache_fillcolour = fillcolour
                else:
                    dc.SetBrush(wx.TRANSPARENT_BRUSH)

                if closed:
                    dc.DrawPolygon(poly)
                else:
                    dc.DrawLines(poly)

    def DrawPolylineLayer(self, dc, data, map_rel):
        """Draw a polyline layer.

        dc       the active device context to draw on
        data     an iterable of polyline tuples:
                     (p, placement, width, colour, offset_x, offset_y, udata)
                 where p is an iterable of points: (x, y)
        map_rel  points relative to map if True, else relative to view
        """

        # get the correct pex function for mode (map/view)
        pex = self.PexPolygonView
        if map_rel:
            pex = self.PexPolygon

        # draw polyline(s)
        cache_colour_width = None       # speed up mostly unchanging data

        for (p, place, width, colour, x_off, y_off, udata) in data:
            (poly, extent) = pex(place, p, x_off, y_off)
            if poly:
                if cache_colour_width != (colour, width):
                    dc.SetPen(wx.Pen(colour, width=width))
                    cache_colour_width = (colour, width)
                dc.SetBrush(wx.TRANSPARENT_BRUSH)
                dc.DrawLines(poly)

    def ViewExtent(self, place, view, w, h, x_off, y_off, dcw=0, dch=0):
        """Get view extent of area.

        place         placement string ('cc', 'se', etc)
        view          tuple (xview,yview) of view coordinates of object point
        w, h          area width and height (pixels)
        x_off, y_off  x and y offset (pixels)

        Return the view extent of the area: (left, right, top, bottom)
        where:
            left    pixel coords of left side of area
            right   pixel coords of right side of area
            top     pixel coords of top of area
            bottom  pixel coords of bottom of area

        Return a tuple (left, right, top, bottom) of the view coordinates of
        the extent rectangle.
        """

        # top left corner
        (x, y) = view
        (left, top) = self.extent_placement(place, x, y, x_off, y_off,
                                            w, h, dcw, dch)

        # bottom right corner
        right = left + w
        bottom = top + h

        return (left, right, top, bottom)

######
# Convert between geo and view coordinates
######

    def Geo2View(self, geo):
        """Convert a geo coord to view.

        geo  tuple (xgeo, ygeo)

        Return a tuple (xview, yview) in view coordinates.
        Assumes point is in view.
        """

        log(f'Geo2View: input geo={geo}')

        # convert the Geo position to tile coordinates
        (tx, ty) = self.tile_src.Geo2Tile(geo)
        log(f'Geo2View: after .Geo2Tile(geo), tx={tx}, ty={ty}')
        log(f'Geo2View: .tile_size_x={self.tile_src.tile_size_x}, .key_tile_xoffset={self.key_tile_xoffset}, .key_tile_left={self.key_tile_left}')

        # using the key_tile_* variables convert to view coordinates
        xview = ((tx - self.key_tile_left) * self.tile_src.tile_size_x) - self.key_tile_xoffset
        yview = ((ty - self.key_tile_top) * self.tile_src.tile_size_y) - self.key_tile_yoffset

        log(f'Geo2View: returning xview={xview}')
        return (xview, yview)
#        return ((tx * self.tile_src.tile_size_x) - self.view_offset_x,
#                (ty * self.tile_src.tile_size_y) - self.view_offset_y)

    def Geo2ViewMasked(self, geo):
        """Convert a geo (lon+lat) position to view pixel coords.

        geo  tuple (xgeo, ygeo)

        Return a tuple (xview, yview) of point if on-view,or None
        if point is off-view.
        """

        (xgeo, ygeo) = geo

        if (self.view_llon <= xgeo <= self.view_rlon and
                self.view_blat <= ygeo <= self.view_tlat):
            return self.Geo2View(geo)

        return None

######
# PEX - Point & EXtension.
#
# These functions encapsulate the code that finds the extent of an object.
# They all return a tuple (point, extent) where 'point' is the placement
# point of an object (or list of points for a polygon) and an 'extent'
# tuple (lx, rx, ty, by) [left, right, top, bottom].
######

    def PexPoint(self, place, geo, x_off, y_off, radius):
        """Given a point object (geo coords) get point/extent in view coords.

        place         placement string
        geo           point position tuple (xgeo, ygeo)
        x_off, y_off  X and Y offsets

        Return a tuple of point and extent origins (point, extent) where 'point'
        is (px, py) and extent is (elx, erx, ety, eby) (both in view coords).
        Return None for either or both if off-view.

        The 'extent' here is the extent of the point+radius.
        """

        # get point view coords
        (xview, yview) = self.Geo2View(geo)
        point = self.point_placement(place, xview, yview, x_off, y_off)
        (px, py) = point

        # extent = (left, right, top, bottom) in view coords
        elx = px - radius
        erx = px + radius
        ety = py - radius
        eby = py + radius
        extent = (elx, erx, ety, eby)

        # decide if point and extent are off-view
        if px < 0 or px > self.view_width or py < 0 or py > self.view_height:
            point = None

        if erx < 0 or elx > self.view_width or eby < 0 or ety > self.view_height:
            # no extent if ALL of extent is off-view
            extent = None

        return (point, extent)

    def PexPointView(self, place, view, x_off, y_off, radius):
        """Given a point object (view coords) get point/extent in view coords.

        place         placement string
        view          point position tuple (xview, yview)
        x_off, y_off  X and Y offsets

        Return a tuple of point and extent origins (point, extent) where 'point'
        is (px, py) and extent is (elx, erx, ety, eby) (both in view coords).
        Return None for either or both if off-view.

        The 'extent' here is the extent of the point+radius.
        """

        # get point view coords and perturb point to placement
        (xview, yview) = view
        point = self.point_placement(place, xview, yview, x_off, y_off,
                                     self.view_width, self.view_height)
        (px, py) = point

        # extent = (left, right, top, bottom) in view coords
        elx = px - radius
        erx = px + radius
        ety = py - radius
        eby = py + radius
        extent = (elx, erx, ety, eby)

        # decide if point and extent are off-view
        if (px < 0 or px > self.view_width
                or py < 0 or py > self.view_height):
            view = None

        if erx < 0 or elx > self.view_width or eby < 0 or ety > self.view_height:
            # no extent if ALL of extent is off-view
            extent = None

        return (point, extent)

    def PexExtent(self, place, geo, x_off, y_off, w, h):
        """Given an extent object convert point/extent coords to view coords.

        place         placement string
        geo           point position tuple (xgeo, ygeo)
        x_off, y_off  X and Y offsets
        w, h          width and height of extent in pixels

        Return a tuple of point and extent origins (point, extent) where 'point'
        is (px, py) and extent is (elx, erx, ety, eby) (both in view coords).
        Return None if point is off-view.

        An extent object can be either an image object or a text object.
        """

        log(f'PexExtent: place={place}, geo={geo}, x_off={x_off}, y_off={y_off}, w={w}, h={h}')

        # get point view coords
        point = self.Geo2View(geo)
        (px, py) = point

        log(f'PexExtent: Geo2View({geo}) -> point={point}')

        # extent = (left, right, top, bottom) in view coords
        extent = self.ViewExtent(place, point, w, h, x_off, y_off)
        (elx, erx, ety, eby) = extent

        log(f'PexExtent: ViewExtent({place}, {point}, {w}, {h}, {x_off}, {y_off}) -> extent={extent}')

        # decide if point and extent are off-view
        if px < 0 or px > self.view_width or py < 0 or py > self.view_height:
            point = None

        if erx < 0 or elx > self.view_width or eby < 0 or ety > self.view_height:
            # no extent if ALL of extent is off-view
            extent = None

        log(f'PexExtent: returning ({point}, {extent})')
        return (point, extent)

    def PexExtentView(self, place, view, x_off, y_off, w, h):
        """Given a view object convert point/extent coords to view coords.

        place         placement string
        view          point position tuple (xview, yview)
        x_off, y_off  X and Y offsets
        w, h          width and height of extent in pixels

        Return a tuple of point and extent origins (point, extent) where 'point'
        is (px, py) and extent is (elx, erx, ety, eby) (both in view coords).
        Either point or extent is None if object off-view.

        Takes size of extent object into consideration.
        """

        # get point view coords and perturb point to placement origin
        (xview, yview) = view
        point = self.point_placement(place, xview, yview, 0, 0,
                                     self.view_width, self.view_height)

        # get point view coords (X and Y)
        (px, py) = view

        # extent = (left, right, top, bottom) in view coords
        extent = self.ViewExtent(place, view, w, h, x_off, y_off,
                                 self.view_width, self.view_height)
        (elx, erx, ety, eby) = extent

        # decide if point and extent are off-view
        if px < 0 or px > self.view_width or py < 0 or py > self.view_height:
            view = None

        if erx < 0 or elx > self.view_width or eby < 0 or ety > self.view_height:
            # no extent if ALL of extent is off-view
            extent = None

        return (point, extent)

    def PexPolygon(self, place, poly, x_off, y_off):
        """Given a polygon/line obj (geo coords) get point/extent in view coords.

        place         placement string
        poly          list of point position tuples (xgeo, ygeo)
        x_off, y_off  X and Y offsets

        Return a tuple of point and extent origins (point, extent) where 'point'
        is a list of (px, py) and extent is (elx, erx, ety, eby) (both in view
        coords).  Return None for either or both if off-view.
        """

        # get polygon/line points in perturbed view coordinates
        view = []
        for geo in poly:
            (xview, yview) = self.Geo2View(geo)
            point = self.point_placement(place, xview, yview, x_off, y_off)
            view.append(point)

        # get extent - max/min x and y
        # extent = (left, right, top, bottom) in view coords
        elx = min(view, key=lambda x: x[0])[0]
        erx = max(view, key=lambda x: x[0])[0]
        ety = min(view, key=lambda x: x[1])[1]
        eby = max(view, key=lambda x: x[1])[1]
        extent = (elx, erx, ety, eby)

        # decide if polygon or extent are off-view
        res_pt = None
        res_ex = None
        for (px, py) in view:
            if ((px >= 0 and px < self.view_width)
                    and (py >= 0 and py < self.view_height)):
                res_pt = view
                res_ex = extent
                break

        return (res_pt, res_ex)

    def PexPolygonView(self, place, poly, x_off, y_off):
        """Given a polygon/line obj (view coords) get point/extent in view coords.

        place         placement string
        poly          list of point position tuples (xview, yview)
        x_off, y_off  X and Y offsets

        Return a tuple of point and extent origins (point, extent) where 'point'
        is a list of (px, py) and extent is (elx, erx, ety, eby) (both in view
        coords).  Return None for either or both if off-view.
        """

        # get polygon/line points in view coordinates
        view = []
        for (xview, yview) in poly:
            point = self.point_placement(place, xview, yview, x_off, y_off,
                                         self.view_width, self.view_height)
            view.append(point)

        # get extent - max/min x and y
        # extent = (left, right, top, bottom) in view coords
        elx = min(view, key=lambda x: x[0])[0]
        erx = max(view, key=lambda x: x[0])[0]
        ety = min(view, key=lambda x: x[1])[1]
        eby = max(view, key=lambda x: x[1])[1]
        extent = (elx, erx, ety, eby)

        # decide if polygon/line or extent are off-view
        res_pt = None
        res_ex = None
        for (px, py) in view:
            if ((px >= 0 and px < self.view_width)
                    and (py >= 0 and py < self.view_height)):
                res_pt = view
                res_ex = extent
                break

        return (res_pt, res_ex)

######
# Placement routines instead of original 'exec' code.
# Code in test_assumptions.py shows this is faster.
######

    @staticmethod
    def point_placement(place, x, y, x_off, y_off, dcw=0, dch=0):
        """Perform map- or view-relative placement for a single point.

        place         placement key string
        x, y          point relative to placement origin
        x_off, y_off  offset from point
        dcw, dch      width, height of the view draw context (0 if map-rel)

        Returns a tuple (x, y) in view coordinates.
        """

        dcw2 = dcw/2
        dch2 = dch/2

        if place == 'cc':   x+=dcw2;       y+=dch2
        elif place == 'nw': x+=x_off;      y+=y_off
        elif place == 'cn': x+=dcw2;       y+=y_off
        elif place == 'ne': x+=dcw-x_off;  y+=y_off
        elif place == 'ce': x+=dcw-x_off;  y+=dch2
        elif place == 'se': x+=dcw-x_off;  y+=dch-y_off
        elif place == 'cs': x+=dcw2;       y+=dch-y_off
        elif place == 'sw': x+=x_off;      y+=dch-y_off
        elif place == 'cw': x+=x_off;      y+=dch2

        return (x, y)

    @staticmethod
    def extent_placement(place, x, y, x_off, y_off, w, h, dcw=0, dch=0):
        """Perform map- and view-relative placement for an extent object.

        place         placement key string
        x, y          point relative to placement origin
        x_off, y_off  offset from point
        w, h          width, height of the image
        dcw, dcw      width/height of the view draw context

        Returns a tuple (x, y).
        """

        w2 = w/2
        h2 = h/2

        dcw2 = dcw/2
        dch2 = dch/2

        if place == 'cc':   x+=dcw2-w2;       y+=dch2-h2
        elif place == 'nw': x+=x_off;         y+=y_off
        elif place == 'cn': x+=dcw2-w2;       y+=y_off
        elif place == 'ne': x+=dcw-w-x_off;   y+=y_off
        elif place == 'ce': x+=dcw-w-x_off;   y+=dch2-h2
        elif place == 'se': x+=dcw-w-x_off;   y+=dch-h-y_off
        elif place == 'cs': x+=dcw2-w2;       y+=dch-h-y_off
        elif place == 'sw': x+=x_off;         y+=dch-h-y_off
        elif place == 'cw': x+=x_off;         y+=dch2-h2

        return (x, y)

################################################################################
# Below are the "external" API methods.
################################################################################

    def dump_key_data(self):
        """Debug function to return string describing 'key' tile data."""

        return (f'\t.key_tile_left={self.key_tile_left}\n'
                f'\t.key_tile_top={self.key_tile_top}\n'
                f'\t.key_tile_xoffset={self.key_tile_xoffset}\n'
                f'\t.key_tile_yoffset={self.key_tile_yoffset}\n'
                f'\t.view_width={self.view_width}\n'
                f'\t.view_height={self.view_height}\n'
                f'\t.map_width={self.map_width}\n'
                f'\t.map_height={self.map_height}\n'
               )

    def zoom_level(self, level, x=None, y=None):
        """Zoom to a map level.

        level  map level to zoom to
        x, y   view coordinates of point around which we zoom

        Change the map zoom level to that given. Returns True if the zoom
        succeeded, else False. If False is returned the method call has no effect.
        """

        # if x,y not given, use view centre
        if x is None:
            x = self.view_width // 2
        if y is None:
            y = self.view_height // 2

        log(f'zoom_level: level={level}, x={x}, y={y}')
        log(f'zoom_level: before, key tile data:\n{self.dump_key_data()}')

        # get tile source to use the new level
        result = self.tile_src.UseLevel(level)

        # if tile-source changed, calculate new centre tile
        if result:
            # calculate zoom point tile coordinates before zoom
            z_point = self.view_to_tile()
            log(f'zoom_level: z_point={z_point}')

            # figure out the scale of the zoom (2 or 0.5)
            log(f'level={level}, self.level={self.level}')
            scale = (self.level + 1) / (level + 1)
            scale = 2**(level - self.level)
            log(f'zoom_level: scale={scale}')

            new_z_point = self.zoom_tile(z_point, scale)
            log(f'zoom_level: new_z_point={new_z_point}')

            new_key = self.tile_to_key(new_z_point, x, y)
            log(f'zoom_level: new_key={new_key}')

            (self.key_tile_left, self.key_tile_xoffset,
                    self.key_tile_top, self.key_tile_yoffset) = new_key

#            # get centre tile details and move to key
##            xtile = self.key_tile_left
#            xoffset = self.key_tile_xoffset
#            while xoffset > 0:
#                log(f'canon X: xoffset={xoffset}, xtile={xtile}')
#                if xtile == 0:
#                    break
#                xtile -= 1
#                xoffset -= self.tile_width
#
#            ytile = self.key_tile_top
#            yoffset = self.key_tile_yoffset
#            while yoffset > 0:
#                log(f'canon Y: yoffset={yoffset}, ytile={ytile}')
#                if ytile == 0:
#                    break
#                ytile -= 1
#                yoffset -= self.tile_height

            # move to new level
            self.level = level
            (self.num_tiles_x, self.num_tiles_y, _, _) = self.tile_src.GetInfo(level)
            self.map_width = self.num_tiles_x * self.tile_width
            self.map_height = self.num_tiles_y * self.tile_height
            log(f'self.map_width={self.map_width}, self.map_height={self.map_height}')

#        self.key_tile_left = 0      # tile coordinates of key tile
#        self.key_tile_top = 0
#        self.key_tile_xoffset = 0   # view coordinates of key tile wrt view
#        self.key_tile_yoffset = 0

#            # calculate the key tile data
#            while xtile > 0:
#                xtile -= self.tile_width
#                xoffset -= 1
#            log(f'X normalized to xtile={xtile}, xoffset={xoffset}')
#            while ytile > 0:
#                ytile -= self.tile_height
#                yoffset -= 1
#            log(f'Y normalized to ytile={ytile}, yoffset={yoffset}')
#
#            self.key_tile_left = xtile
#            self.key_tile_top = ytile
#            self.key_tile_xoffset = xoffset
#            self.key_tile_yoffset = yoffset

            self.recalc_wrap_limits()

            self.update()       # redraw the map

        log(f'zoom_level:  after, key tile data:\n{self.dump_key_data()}')

        return result

    def pan_position(self, posn):
        """Pan to the given position in the current map zoom level.

        posn  a tuple (xgeo, ygeo)
        """

        pass

    def zoom_level_position(self, level, posn):
        """Zoom to a map level and pan to the given position in the map.

        level  map level to zoom to
        posn  a tuple (xgeo, ygeo)
        """

        pass

    def zoom_area(self, posn, size):
        """Zoom to a map level and area.

        posn  a tuple (xgeo, ygeo) of the centre of the area to show
        size  a tuple (width, height) of area in geo coordinate units

        Zooms to a map level and pans to a position such that the specified area
        is completely within the view. Provides a simple way to ensure an
        extended feature is wholly within the centre of the view.
        """

        pass

    def get_i18n_kw(self, kwargs, kws, default):
        """Get alternate international keyword value.

        kwargs   dictionary to look for keyword value
        kws      iterable of keyword spelling strings
        default  default value if no keyword found

        Returns the keyword value.
        """

        result = None
        for kw_str in kws[:-1]:
            result = kwargs.get(kw_str, None)
            if result:
                break
        else:
            result = kwargs.get(kws[-1], default)

        return result

    def info(self, msg):
        """Display an information message, log and graphically."""

        log_msg = '# ' + msg
        length = len(log_msg)
        prefix = '#### Information '
        banner = prefix + '#'*(80 - len(log_msg) - len(prefix))
        log(banner)
        log(log_msg)
        log(banner)

        wx.MessageBox(msg, 'Warning', wx.OK | wx.ICON_INFORMATION)

    def warn(self, msg):
        """Display a warning message, log and graphically."""

        log_msg = '# ' + msg
        length = len(log_msg)
        prefix = '#### Warning '
        banner = prefix + '#'*(80 - len(log_msg) - len(prefix))
        log(banner)
        log(log_msg)
        log(banner)

        wx.MessageBox(msg, 'Warning', wx.OK | wx.ICON_ERROR)

######
# "add a layer" routines
######

    def AddPointLayer(self, points, map_rel=True, visible=True,
                      show_levels=None, selectable=False,
                      name='<points_layer>', **kwargs):
        """Add a layer of points, map or view relative.

        points       iterable of point data:
                         (x, y[, attributes])
                     where x & y are either lon&lat (map) or x&y (view) coords
                     and attributes is an optional dictionary of attributes for
                     _each point_ with keys like:
                         'placement'  a placement string
                         'radius'     radius of point in pixels
                         'colour'     colour of point
                         'offset_x'   X offset
                         'offset_y'   Y offset
                         'data'       point user data object
        map_rel      points are map relative if True, else view relative
        visible      True if the layer is visible
        show_levels  list of levels at which layer is auto-shown (or None==all)
        selectable   True if select operates on this layer
        name         the 'name' of the layer - mainly for debug
        kwargs       a layer-specific attributes dictionary, has keys:
                         'placement'  a placement string
                         'radius'     radius of point in pixels
                         'colour'     colour of point
                         'offset_x'   X offset
                         'offset_y'   Y offset
                         'data'       point user data object
        """

        # merge global and layer defaults
        if map_rel:
            default_placement = kwargs.get('placement', self.DefaultPointPlacement)
            default_radius = kwargs.get('radius', self.DefaultPointRadius)
            default_colour = self.get_i18n_kw(kwargs, ('colour', 'color'),
                                              self.DefaultPointColour)
            default_offset_x = kwargs.get('offset_x', self.DefaultPointOffsetX)
            default_offset_y = kwargs.get('offset_y', self.DefaultPointOffsetY)
            default_data = kwargs.get('data', self.DefaultPointData)
        else:
            default_placement = kwargs.get('placement', self.DefaultPointViewPlacement)
            default_radius = kwargs.get('radius', self.DefaultPointViewRadius)
            default_colour = self.get_i18n_kw(kwargs, ('colour', 'color'),
                                              self.DefaultPointViewColour)
            default_offset_x = kwargs.get('offset_x', self.DefaultPointViewOffsetX)
            default_offset_y = kwargs.get('offset_y', self.DefaultPointViewOffsetY)
            default_data = kwargs.get('data', self.DefaultPointData)

        # create draw data iterable for draw method
        draw_data = []              # list to hold draw data

        for pt in points:
            if len(pt) == 3:
                (x, y, attributes) = pt
            elif len(pt) == 2:
                (x, y) = pt
                attributes = {}
            else:
                msg = ('Point data must be iterable of tuples: '
                       '(x, y[, dict])\n'
                       'Got: %s' % str(pt))
                raise Exception(msg)

            # plug in any required polygon values (override globals+layer)
            placement = attributes.get('placement', default_placement)
            radius = attributes.get('radius', default_radius)
            colour = self.get_i18n_kw(attributes, ('colour', 'color'),
                                      default_colour)
            offset_x = attributes.get('offset_x', default_offset_x)
            offset_y = attributes.get('offset_y', default_offset_y)
            udata = attributes.get('data', default_data)

            # check values that can be wrong
            placement = placement.lower()
            if placement not in self.valid_placements:
                msg = ("Point placement value is invalid, got '%s'"
                       % str(placement))
                raise Exception(msg)

            # convert various colour formats to internal (r, g, b, a)
            colour = self.colour_to_internal(colour)

            # append another point to draw data list
            draw_data.append((float(x), float(y), placement,
                              radius, colour, offset_x, offset_y, udata))

        return self.add_layer(self.DrawPointLayer, draw_data, map_rel,
                              visible=visible, show_levels=show_levels,
                              selectable=selectable, name=name,
                              type=self.TypePoint)

    def AddImageLayer(self, data, map_rel=True, visible=True,
                      show_levels=None, selectable=False,
                      name='<image_layer>', **kwargs):
        """Add a layer of images, map or view relative.

        data         list of (lon, lat, fname[, attributes]) (map_rel)
                     or list of (x, y, fname[, attributes]) (view relative)
                     attributes is a dictionary of attributes:
                         placement  a placement string
                         radius     object point radius
                         colour     object point colour
                         offset_x   X offset
                         offset_y   Y offset
                         data       image user data
        map_rel      points drawn relative to map if True, else view relative
        visible      True if the layer is to be immediately visible
        show_levels  list of levels at which layer is auto-shown (or None)
        selectable   True if select operates on this layer
        name         name of this layer
        kwargs       dictionary of extra params:
                         placement  string describing placement wrt hotspot
                         radius     object point radius
                         colour     object point colour
                         offset_x   hotspot X offset in pixels
                         offset_y   hotspot Y offset in pixels
                         data       image user data

        The hotspot is placed at (lon, lat) or (x, y).  'placement' controls
        where the image is displayed relative to the hotspot.
        """

        # merge global and layer defaults
        if map_rel:
            default_placement = kwargs.get('placement', self.DefaultImagePlacement)
            default_radius = kwargs.get('radius', self.DefaultImageRadius)
            default_colour = kwargs.get('colour', self.DefaultImageColour)
            default_offset_x = kwargs.get('offset_x', self.DefaultImageOffsetX)
            default_offset_y = kwargs.get('offset_y', self.DefaultImageOffsetY)
            default_data = kwargs.get('data', self.DefaultImageData)
        else:
            default_placement = kwargs.get('placement', self.DefaultImageViewPlacement)
            default_radius = kwargs.get('radius', self.DefaultImageViewRadius)
            default_colour = kwargs.get('colour', self.DefaultImageViewColour)
            default_offset_x = kwargs.get('offset_x', self.DefaultImageViewOffsetX)
            default_offset_y = kwargs.get('offset_y', self.DefaultImageViewOffsetY)
            default_data = kwargs.get('data', self.DefaultImageViewData)

        # define cache variables for the image informtion
        # used to minimise file access - just caches previous file informtion
        fname_cache = None
        bmp_cache = None
        w_cache = None
        h_cache = None

        # load all image files, convert to bitmaps, create draw_data iterable
        draw_data = []
        for d in data:
            if len(d) == 4:
                (lon, lat, fname, attributes) = d
            elif len(d) == 3:
                (lon, lat, fname) = d
                attributes = {}
            else:
                msg = ('Image data must be iterable of tuples: '
                       '(x, y, fname[, dict])\nGot: %s' % str(d))
                raise Exception(msg)

            # get image specific values, if any
            placement = attributes.get('placement', default_placement)
            radius = attributes.get('radius', default_radius)
            colour = attributes.get('colour', default_colour)
            offset_x = attributes.get('offset_x', default_offset_x)
            offset_y = attributes.get('offset_y', default_offset_y)
            udata = attributes.get('data', None)

            if fname == fname_cache:
                bmap = bmp_cache
                w = w_cache
                h = h_cache
            else:
                fname_cache = fname
#                img = QPixmap(fname)
                bmp_cache = bmap = img = QPixmap(fname)
#                bmp_cache = bmap = img.ConvertToBitmap()
                size = img.size()
                h = h_cache = size.height()
                w = w_cache = size.width()

            # check values that can be wrong
            placement = placement.lower()
            if placement not in self.valid_placements:
                msg = ("Image placement value is invalid, got '%s'"
                       % str(placement))
                raise Exception(msg)

            # convert various colour formats to internal (r, g, b, a)
            colour = self.colour_to_internal(colour)
            log(f'AddImageLayer: colour={colour}')

            draw_data.append((float(lon), float(lat), bmap, w, h, placement,
                              offset_x, offset_y, radius, colour, udata))

        return self.AddLayer(self.DrawImageLayer, draw_data, map_rel,
                             visible=visible, show_levels=show_levels,
                             selectable=selectable, name=name,
                             type=self.TypeImage)

    def AddTextLayer(self, text, map_rel=True, visible=True, show_levels=None,
                     selectable=False, name='<text_layer>', **kwargs):
        """Add a text layer to the map or view.

        text         list of sequence of (lon, lat, text[, dict]) coordinates
                     (optional 'dict' contains point-specific attributes)
        map_rel      points drawn relative to map if True, else view relative
        visible      True if the layer is to be immediately visible
        show_levels  list of levels at which layer is auto-shown
        selectable   True if select operates on this layer
        name         name of this layer
        kwargs       a dictionary of changeable text attributes
                         (placement, radius, fontname, fontsize, colour, data)
                     these supply any data missing in 'data'
        """

        # merge global and layer defaults
        if map_rel:
            default_placement = kwargs.get('placement', self.DefaultTextPlacement)
            default_radius = kwargs.get('radius', self.DefaultTextRadius)
            default_fontname = kwargs.get('fontname', self.DefaultTextFontname)
            default_fontsize = kwargs.get('fontsize', self.DefaultTextFontSize)
            default_colour = self.get_i18n_kw(kwargs, ('colour', 'color'),
                                              self.DefaultTextColour)
            default_textcolour = self.get_i18n_kw(kwargs,
                                                  ('textcolour', 'textcolor'),
                                                  self.DefaultTextTextColour)
            default_offset_x = kwargs.get('offset_x', self.DefaultTextOffsetX)
            default_offset_y = kwargs.get('offset_y', self.DefaultTextOffsetY)
            default_data = kwargs.get('data', self.DefaultTextData)
        else:
            default_placement = kwargs.get('placement', self.DefaultTextViewPlacement)
            default_radius = kwargs.get('radius', self.DefaultTextViewRadius)
            default_fontname = kwargs.get('fontname', self.DefaultTextViewFontname)
            default_fontsize = kwargs.get('fontsize', self.DefaultTextViewFontSize)
            default_colour = self.get_i18n_kw(kwargs, ('colour', 'color'),
                                              self.DefaultTextViewColour)
            default_textcolour = self.get_i18n_kw(kwargs,
                                                  ('textcolour', 'textcolor'),
                                                  self.DefaultTextViewTextColour)
            default_offset_x = kwargs.get('offset_x', self.DefaultTextViewOffsetX)
            default_offset_y = kwargs.get('offset_y', self.DefaultTextViewOffsetY)
            default_data = kwargs.get('data', self.DefaultTextData)

        # create data iterable ready for drawing
        draw_data = []
        for t in text:
            if len(t) == 4:
                (lon, lat, tdata, attributes) = t
            elif len(t) == 3:
                (lon, lat, tdata) = t
                attributes = {}
            else:
                msg = ('Text data must be iterable of tuples: '
                       '(lon, lat, text, [dict])\n'
                       'Got: %s' % str(t))
                raise Exception(msg)

            # plug in any required defaults
            placement = attributes.get('placement', default_placement)
            radius = attributes.get('radius', default_radius)
            fontname = attributes.get('fontname', default_fontname)
            fontsize = attributes.get('fontsize', default_fontsize)
            colour = self.get_i18n_kw(attributes, ('colour', 'color'),
                                      default_colour)
            textcolour = self.get_i18n_kw(attributes,
                                          ('textcolour', 'textcolor'),
                                          default_textcolour)
            offset_x = attributes.get('offset_x', default_offset_x)
            offset_y = attributes.get('offset_y', default_offset_y)
            udata = attributes.get('data', default_data)

            # check values that can be wrong
            placement = placement.lower()
            if placement not in self.valid_placements:
                msg = ("Text placement value is invalid, got '%s'"
                       % str(placement))
                raise Exception(msg)

            # convert various colour formats to internal (r, g, b, a)
            colour = self.colour_to_internal(colour)
            log(f'AddTextLayer: colour={colour}')
            textcolour = self.colour_to_internal(textcolour)
            log(f'AddTextLayer: textcolour={textcolour}')

            draw_data.append((float(lon), float(lat), tdata, placement.lower(),
                              radius, colour, textcolour, fontname, fontsize,
                              offset_x, offset_y, udata))

        return self.AddLayer(self.DrawTextLayer, draw_data, map_rel,
                             visible=visible, show_levels=show_levels,
                             selectable=selectable, name=name,
                             type=self.TypeText)

    def AddPolygonLayer(self, data, map_rel=True, visible=True,
                        show_levels=None, selectable=False,
                        name='<polygon_layer>', **kwargs):
        """Add a layer of polygon data to the map.

        data         iterable of polygon tuples:
                         (<iter>[, attributes])
                     where <iter> is another iterable of (x, y) tuples and
                     attributes is a dictionary of polygon attributes:
                         placement   a placement string (view-relative only)
                         width       width of polygon edge lines
                         colour      colour of edge lines
                         close       if True closes polygon
                         filled      polygon is filled (implies closed)
                         fillcolour  fill colour
                         offset_x    X offset
                         offset_y    Y offset
                         data        polygon user data object
        map_rel      points drawn relative to map if True, else view relative
        visible      True if the layer is to be immediately visible
        show_levels  list of levels at which layer is auto-shown (or None)
        selectable   True if select operates on this layer
        name         name of this layer
        kwargs       extra keyword args, layer-specific:
                         placement   placement string (view-rel only)
                         width       width of polygons in pixels
                         colour      colour of polygon edge lines
                         close       True if polygon is to be closed
                         filled      if True, fills polygon
                         fillcolour  fill colour
                         offset_x    X offset
                         offset_y    Y offset
                         data        polygon user data object
        """

        # merge global and layer defaults
        if map_rel:
            default_placement = kwargs.get('placement',
                                           self.DefaultPolygonPlacement)
            default_width = kwargs.get('width', self.DefaultPolygonWidth)
            default_colour = self.get_i18n_kw(kwargs, ('colour', 'color'),
                                              self.DefaultPolygonColour)
            default_close = kwargs.get('closed', self.DefaultPolygonClose)
            default_filled = kwargs.get('filled', self.DefaultPolygonFilled)
            default_fillcolour = self.get_i18n_kw(kwargs,
                                                  ('fillcolour', 'fillcolor'),
                                                  self.DefaultPolygonFillcolour)
            default_offset_x = kwargs.get('offset_x', self.DefaultPolygonOffsetX)
            default_offset_y = kwargs.get('offset_y', self.DefaultPolygonOffsetY)
            default_data = kwargs.get('data', self.DefaultPolygonData)
        else:
            default_placement = kwargs.get('placement',
                                           self.DefaultPolygonViewPlacement)
            default_width = kwargs.get('width', self.DefaultPolygonViewWidth)
            default_colour = self.get_i18n_kw(kwargs, ('colour', 'color'),
                                              self.DefaultPolygonViewColour)
            default_close = kwargs.get('closed', self.DefaultPolygonViewClose)
            default_filled = kwargs.get('filled', self.DefaultPolygonViewFilled)
            default_fillcolour = self.get_i18n_kw(kwargs,
                                                  ('fillcolour', 'fillcolor'),
                                                  self.DefaultPolygonViewFillcolour)
            default_offset_x = kwargs.get('offset_x', self.DefaultPolygonViewOffsetX)
            default_offset_y = kwargs.get('offset_y', self.DefaultPolygonViewOffsetY)
            default_data = kwargs.get('data', self.DefaultPolygonViewData)

        # create draw_data iterable
        draw_data = []
        for d in data:
            if len(d) == 2:
                (p, attributes) = d
            elif len(d) == 1:
                p = d
                attributes = {}
            else:
                msg = ('Polygon data must be iterable of tuples: '
                       '(polygon, [attributes])\n'
                       'Got: %s' % str(d))
                raise Exception(msg)

            # get polygon attributes
            placement = attributes.get('placement', default_placement)
            width = attributes.get('width', default_width)
            colour = self.get_i18n_kw(attributes, ('colour', 'color'),
                                      default_colour)
            close = attributes.get('closed', default_close)
            filled = attributes.get('filled', default_filled)
            if filled:
                close = True
            fillcolour = self.get_i18n_kw(attributes,
                                          ('fillcolour', 'fillcolor'),
                                          default_fillcolour)
            offset_x = attributes.get('offset_x', default_offset_x)
            offset_y = attributes.get('offset_y', default_offset_y)
            udata = attributes.get('data', default_data)

            # if polygon is to be filled, ensure closed
            if close:
                p = list(p)     # must get a *copy*
                p.append(p[0])

            # check values that can be wrong
            placement = placement.lower()
            if placement not in self.valid_placements:
                msg = ("Polygon placement value is invalid, got '%s'"
                       % str(placement))
                raise Exception(msg)

            # convert various colour formats to internal (r, g, b, a)
            colour = self.colour_to_internal(colour)
            fillcolour = self.colour_to_internal(fillcolour)

            draw_data.append((p, placement, width, colour, close,
                              filled, fillcolour, offset_x, offset_y, udata))

        return self.AddLayer(self.DrawPolygonLayer, draw_data, map_rel,
                             visible=visible, show_levels=show_levels,
                             selectable=selectable, name=name,
                             type=self.TypePolygon)

    def AddPolylineLayer(self, data, map_rel=True, visible=True,
                        show_levels=None, selectable=False,
                        name='<polyline>', **kwargs):
        """Add a layer of polyline data to the map.

        data         iterable of polyline tuples:
                         (<iter>[, attributes])
                     where <iter> is another iterable of (x, y) tuples and
                     attributes is a dictionary of polyline attributes:
                         placement   a placement string (view-relative only)
                         width       width of polyline edge lines
                         colour      colour of edge lines
                         offset_x    X offset
                         offset_y    Y offset
                         data        polyline user data object
        map_rel      points drawn relative to map if True, else view relative
        visible      True if the layer is to be immediately visible
        show_levels  list of levels at which layer is auto-shown (or None)
        selectable   True if select operates on this layer
        name         name of this layer
        kwargs       extra keyword args, layer-specific:
                         placement   placement string (view-rel only)
                         width       width of polyline in pixels
                         colour      colour of polyline edge lines
                         offset_x    X offset
                         offset_y    Y offset
                         data        polygon user data object
        """

        # merge global and layer defaults
        if map_rel:
            default_placement = kwargs.get('placement',
                                           self.DefaultPolygonPlacement)
            default_width = kwargs.get('width', self.DefaultPolygonWidth)
            default_colour = self.get_i18n_kw(kwargs, ('colour', 'color'),
                                              self.DefaultPolygonColour)
            default_offset_x = kwargs.get('offset_x', self.DefaultPolygonOffsetX)
            default_offset_y = kwargs.get('offset_y', self.DefaultPolygonOffsetY)
            default_data = kwargs.get('data', self.DefaultPolygonData)
        else:
            default_placement = kwargs.get('placement',
                                           self.DefaultPolygonViewPlacement)
            default_width = kwargs.get('width', self.DefaultPolygonViewWidth)
            default_colour = self.get_i18n_kw(kwargs, ('colour', 'color'),
                                              self.DefaultPolygonViewColour)
            default_offset_x = kwargs.get('offset_x', self.DefaultPolygonViewOffsetX)
            default_offset_y = kwargs.get('offset_y', self.DefaultPolygonViewOffsetY)
            default_data = kwargs.get('data', self.DefaultPolygonViewData)

        # create draw_data iterable
        draw_data = []
        for d in data:
            if len(d) == 2:
                (p, attributes) = d
            elif len(d) == 1:
                p = d
                attributes = {}
            else:
                msg = ('Polyline data must be iterable of tuples: '
                       '(polyline, [attributes])\n'
                       'Got: %s' % str(d))
                raise Exception(msg)

            # get polygon attributes
            placement = attributes.get('placement', default_placement)
            width = attributes.get('width', default_width)
            colour = self.get_i18n_kw(attributes, ('colour', 'color'),
                                      default_colour)
            offset_x = attributes.get('offset_x', default_offset_x)
            offset_y = attributes.get('offset_y', default_offset_y)
            udata = attributes.get('data', default_data)

            # check values that can be wrong
            placement = placement.lower()
            if placement not in self.valid_placements:
                msg = ("Polyline placement value is invalid, got '%s'"
                       % str(placement))
                raise Exception(msg)

            # convert various colour formats to internal (r, g, b, a)
            colour = self.colour_to_internal(colour)

            draw_data.append((p, placement, width, colour,
                              offset_x, offset_y, udata))

        return self.AddLayer(self.DrawPolylineLayer, draw_data, map_rel,
                             visible=visible, show_levels=show_levels,
                             selectable=selectable, name=name,
                             type=self.TypePolyline)

    def colour_to_internal(self, colour):
        """Convert a colour in one of various forms to an internal format.

        colour  either a HEX string ('#RRGGBBAA')
                or a tuple (r, g, b, a)
                or a colour name ('red')

        Returns internal form:  (r, g, b, a)
        """

        if isinstance(colour, str):
            # expect '#RRGGBBAA' form
            if len(colour) != 9 or colour[0] != '#':
                # assume it's a colour *name*
                c = QColor(colour)
                result = (c.red(), c.blue(), c.green(), c.alpha())
#                raise Exception(msg)
            else:
                # we try for a colour like '#RRGGBBAA'
                r = int(colour[1:3], 16)
                g = int(colour[3:5], 16)
                b = int(colour[5:7], 16)
                a = int(colour[7:9], 16)
                result = (r, g, b, a)
        else:
            # we assume a list or tuple
            try:
                len_colour = len(colour)
            except TypeError:
                msg = f"Colour value '{colour}' is not in the form '(r, g, b, a)'"
                raise Exception(msg)

            if len_colour != 4:
                msg = f"Colour value '{colour}' is not in the form '(r, g, b, a)'"
                raise Exception(msg)
            result = []
            for v in colour:
                try:
                    v = int(v)
                except ValueError:
                    msg = f"Colour value '{colour}' is not in the form '(r, g, b, a)'"
                    raise Exception(msg)
                if v < 0 or v > 255:
                    msg = f"Colour value '{colour}' is not in the form '(r, g, b, a)'"
                    raise Exception(msg)
                result.append(v)
            result = tuple(result)

        return result
