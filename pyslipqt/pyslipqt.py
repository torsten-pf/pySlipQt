"""
A "slip map" widget for PyQt5.

Some semantics:
    map   the whole map
    view  is the view of the map through the widget
          (view may be smaller than map, or larger)
"""

from math import floor
from PyQt5.QtCore import Qt, QTimer, QPoint, QPointF, QObject, pyqtSignal
from PyQt5.QtWidgets import QLabel, QSizePolicy, QWidget
from PyQt5.QtGui import QPainter, QColor, QPixmap, QPen, QFont, QFontMetrics
from PyQt5.QtGui import QPolygon, QBrush, QCursor

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
        return ('<pyslip Layer: id=%d, name=%s, map_rel=%s, visible=%s>'
                % (self.id, self.name, str(self.map_rel), str(self.visible)))


######
# The pySlipQt widget.
######


class PySlipQt(QWidget):

    # events the widget will emit
    class Events(QObject):
        EVT_PYSLIPQT_LEVEL = pyqtSignal(int, int)
        EVT_PYSLIPQT_POSITION = pyqtSignal(int, object, tuple)
        EVT_PYSLIPQT_SELECT = pyqtSignal(int, tuple, tuple, object, object, list, list)
        EVT_PYSLIPQT_BOXSELECT = pyqtSignal()
        EVT_PYSLIPQT_POLYSELECT = pyqtSignal()
        EVT_PYSLIPQT_POLYBOXSELECT = pyqtSignal()

    # event numbers
    (EVT_PYSLIPQT_LEVEL, EVT_PYSLIPQT_POSITION,
     EVT_PYSLIPQT_SELECT, EVT_PYSLIPQT_BOXSELECT,
     EVT_PYSLIPQT_POLYSELECT, EVT_PYSLIPQT_POLYBOXSELECT) = range(6)

    
    # list of valid placement values
    valid_placements = ['cc', 'nw', 'cn', 'ne', 'ce',
                        'se', 'cs', 'sw', 'cw', None, False, '']

    # default point attributes - map relative
    DefaultPointPlacement = 'cc'
    DefaultPointRadius = 3
    DefaultPointColour = 'red'
    DefaultPointOffsetX = 0
    DefaultPointOffsetY = 0
    DefaultPointData = None

    # default point attributes - view relative
    DefaultPointViewPlacement = 'cc'
    DefaultPointViewRadius = 3
    DefaultPointViewColour = 'red'
    DefaultPointViewOffsetX = 0
    DefaultPointViewOffsetY = 0
    DefaultPointViewData = None

    # default image attributes - map relative
    DefaultImagePlacement = 'nw'
    DefaultImageRadius = 0
    DefaultImageColour = 'black'
    DefaultImageOffsetX = 0
    DefaultImageOffsetY = 0
    DefaultImageData = None

    # default image attributes - view relative
    DefaultImageViewPlacement = 'nw'
    DefaultImageViewRadius = 0
    DefaultImageViewColour = 'black'
    DefaultImageViewOffsetX = 0
    DefaultImageViewOffsetY = 0
    DefaultImageViewData = None

    # default text attributes - map relative
    DefaultTextPlacement = 'nw'
    DefaultTextRadius = 2
    DefaultTextColour = 'black'
    DefaultTextTextColour = 'black'
    DefaultTextOffsetX = 5
    DefaultTextOffsetY = 1
    DefaultTextFontname = 'Helvetica'
    DefaultTextFontSize = 10
    DefaultTextData = None

    # default text attributes - view relative
    DefaultTextViewPlacement = 'nw'
    DefaultTextViewRadius = 0
    DefaultTextViewColour = 'black'
    DefaultTextViewTextColour = 'black'
    DefaultTextViewOffsetX = 0
    DefaultTextViewOffsetY = 0
    DefaultTextViewFontname = 'Helvetica'
    DefaultTextViewFontSize = 10
    DefaultTextViewData = None

    # default polygon attributes - map view
    DefaultPolygonPlacement = 'cc'
    DefaultPolygonWidth = 1
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
    DefaultPolylineColour = 'red'
    DefaultPolylineOffsetX = 0
    DefaultPolylineOffsetY = 0
    DefaultPolylineData = None

    # default polyline attributes - view relative
    DefaultPolylineViewPlacement = 'cc'
    DefaultPolylineViewWidth = 1
    DefaultPolylineViewColour = 'red'
    DefaultPolylineViewOffsetX = 0
    DefaultPolylineViewOffsetY = 0
    DefaultPolylineViewData = None

    # layer type values
    (TypePoint, TypeImage, TypeText, TypePolygon, TypePolyline) = range(5)

    # cursor types
    StandardCursor = Qt.ArrowCursor
    BoxSelectCursor = Qt.CrossCursor
    WaitCursor = Qt.WaitCursor
    DragCursor = Qt.OpenHandCursor

    def __init__(self, parent, tile_src, start_level, **kwargs):
        """Initialize the pySlipQt widget.

        parent       the GUI parent widget
        tile_src     a Tiles object, source of tiles
        start_level  level to initially display
        kwargs       keyword args passed through to the underlying QLabel
        """

        super().__init__(parent, **kwargs)    # inherit all parent object setup

        # remember the tile source object
        self.tile_src = tile_src

        # the tile coordinates
        self.level = start_level

        # view and map limits
        self.view_width = 0     # width/height of the view
        self.view_height = 0    # changes when the widget changes size

        # set tile and levels stuff
        self.max_level = max(tile_src.levels)   # max level displayed
        self.min_level = min(tile_src.levels)   # min level displayed
        self.tile_width = tile_src.tile_size_x  # width of tile in pixels
        self.tile_height = tile_src.tile_size_y # height of tile in pixels
        self.num_tiles_x = tile_src.num_tiles_x # number of map tiles in X direction
        self.num_tiles_y = tile_src.num_tiles_y # number of map tiles in Y direction
# TODO: implement map wrap-around
#        self.wrap_x = tile_src.wrap_x           # True if tiles wrap in X direction
#        self.wrap_y = tile_src.wrap_y           # True if tiles wrap in Y direction
        self.wrap_x = False                     # True if tiles wrap in X direction
        self.wrap_y = False                     # True if tiles wrap in Y direction

        self.map_width = self.num_tiles_x * self.tile_width     # virtual map width
        self.map_height = self.num_tiles_y * self.tile_height   # virtual map height

        self.next_layer_id = 1                  # source of unique layer IDs

        self.tiles_max_level = max(tile_src.levels) # maximum level in tile source
        self.tiles_min_level = min(tile_src.levels) # minimum level in tile source

        # define position and tile coords of the "key" tile
        self.key_tile_left = 0      # tile coordinates of key tile
        self.key_tile_top = 0
        self.key_tile_xoffset = 0   # view coordinates of key tile wrt view
        self.key_tile_yoffset = 0

        # state variables holding mouse buttons state
        self.left_mbutton_down = False
        self.mid_mbutton_down = False
        self.right_mbutton_down = False

        # keyboard state variables
        self.shift_down = False

        # when dragging, remember the initial start point
        self.start_drag_x = None
        self.start_drag_y = None

        # layer state variables
        self.layer_mapping = {}         # maps layer ID to layer data
        self.layer_z_order = []         # layer Z order, contains layer IDs

        # some cursors
        self.standard_cursor = QCursor(self.StandardCursor)
        self.box_select_cursor = QCursor(self.BoxSelectCursor)
        self.wait_cursor = QCursor(self.WaitCursor)
        self.drag_cursor = QCursor(self.DragCursor)

        # set up dispatch dictionaries for layer select handlers
        # for point select
        self.layerPSelHandler = {self.TypePoint: self.sel_point_in_layer,
                                 self.TypeImage: self.sel_image_in_layer,
                                 self.TypeText: self.sel_text_in_layer,
                                 self.TypePolygon: self.sel_polygon_in_layer,
                                 self.TypePolyline: self.sel_polyline_in_layer}

        # for box select
        self.layerBSelHandler = {self.TypePoint: self.sel_box_points_in_layer,
                                 self.TypeImage: self.sel_box_images_in_layer,
                                 self.TypeText: self.sel_box_texts_in_layer,
                                 self.TypePolygon: self.sel_box_polygons_in_layer,
                                 self.TypePolyline: self.sel_box_polylines_in_layer}

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(self.tile_width, self.tile_height)

        tile_src.setCallback(self.update)

        self.events = PySlipQt.Events()

        self.setMouseTracking(True)
#        self.setEnabled(True)

        self.default_cursor = self.standard_cursor
        self.setCursor(self.standard_cursor)

        # do a "resize" after this function
        QTimer.singleShot(10, self.resizeEvent)

    ######
    # Overide the mouse events
    ######

    def mousePressEvent(self, event):
        b = event.button()
        if b == Qt.NoButton:
            pass
        elif b == Qt.LeftButton:
            self.left_mbutton_down = True

        elif b == Qt.MidButton:
            self.mid_mbutton_down = True
        elif b == Qt.RightButton:
            self.right_mbutton_down = True
        else:
            log('mousePressEvent: unknown button')

    def mouseReleaseEvent(self, event):
        """Mouse button was released."""

        x = event.x()
        y = event.y()
        clickpt_v = (x, y)
        log(f'mouseReleaseEvent: entered, clickpt_v={clickpt_v}')

        # cursor back to normal
        self.setCursor(self.default_cursor)

        b = event.button()
        if b == Qt.NoButton:
            pass
        elif b == Qt.LeftButton:
            log(f'mouseReleaseEvent: left button released at clickpt_v={clickpt_v}')

            self.left_mbutton_down = False
            self.start_drag_x = self.start_drag_y = None    # end drag, if any

#            # if required, ignore this event
#            if self.ignore_next_up:
#                self.ignore_next_up = False
#                return
#            # we need a repaint to remove any selection box, but NOT YET!
#            delayed_paint = self.sbox_1_x       # True if box select active

            # possible point selection, get click point in view & global coords
            log(f'mouseReleaseEvent: clickpt_v={clickpt_v}')
            clickpt_g = self.view_to_geo(clickpt_v)
            log(f'mouseReleaseEvent: clickpt_g={clickpt_g}')
            if clickpt_g is None:
                log(f'mouseReleaseEvent: clicked off-map, returning')
                return          # we clicked off the map

            # check each layer for a point select handler
            # we work on a copy as user click-handler code could change order
            log(f'mouseReleaseEvent: checking layers')
            for id in self.layer_z_order[:]:
                log(f'mouseReleaseEvent: checking layer {id}')
                l = self.layer_mapping[id]
                # if layer visible and selectable
                if l.selectable and l.visible:
                    log(f'mouseReleaseEvent: layer is selectable and visible')
                    sel = self.layerPSelHandler[l.type](l, clickpt_v, clickpt_g)
                    log(f'mouseReleaseEvent: sel={sel} returned from handler')
                    self.events.EVT_PYSLIPQT_SELECT.emit(PySlipQt.EVT_PYSLIPQT_SELECT,
                                                         clickpt_g, clickpt_v,
                                                         id, sel, [], [])
#                    # user code possibly updated screen
#                    delayed_paint = True
            log(f'mouseReleaseEvent: end of layer selection code')

        elif b == Qt.MidButton:
            self.mid_mbutton_down = False
        elif b == Qt.RightButton:
            self.right_mbutton_down = False
        else:
            log('mouseReleaseEvent: unknown button')
 
    def mouseDoubleClickEvent(self, event):
        b = event.button()
        if b == Qt.NoButton:
            pass
        elif b == Qt.LeftButton:
            pass
        elif b == Qt.MidButton:
            pass
        elif b == Qt.RightButton:
            pass
        else:
            log('mouseDoubleClickEvent: unknown button')
 
    def mouseMoveEvent(self, event):
        """Handle a mouse move event."""

        x = event.x()
        y = event.y()
        mouse_view = (x, y)

        if self.left_mbutton_down:
            if self.start_drag_x:       # if we are already dragging
                # we don't move much - less than a tile width/height
                # drag the key tile in the X direction
                delta_x = self.start_drag_x - x
                self.key_tile_xoffset -= delta_x
                if self.key_tile_xoffset < -self.tile_width:    # too far left
                    self.key_tile_xoffset += self.tile_width
                    self.key_tile_left += 1
                if self.key_tile_xoffset > 0:                   # too far right
                    self.key_tile_xoffset -= self.tile_width
                    self.key_tile_left -= 1

                # drag the key tile in the Y direction
                delta_y = self.start_drag_y - y
                self.key_tile_yoffset -= delta_y
                if self.key_tile_yoffset < -self.tile_height:   # too far up
                    self.key_tile_yoffset += self.tile_height
                    self.key_tile_top += 1
                if self.key_tile_yoffset > 0:                   # too far down
                    self.key_tile_yoffset -= self.tile_height
                    self.key_tile_top -= 1

                self.rectify_key_tile()
                self.update()                                   # force a repaint

            self.start_drag_x = x
            self.start_drag_y = y

        # emit the event for mouse position
        mouse_map = self.view_to_geo(mouse_view)
        self.events.EVT_PYSLIPQT_POSITION.emit(PySlipQt.EVT_PYSLIPQT_POSITION, mouse_map, mouse_view)

    def keyPressEvent(self, event):
        """Capture a keyboard event."""

        log(f'keyPressEvent: key pressed={event.key()}')

    def keyReleaseEvent(self, event):

        log(f'keyReleaseEvent: key released={event.key()}')

    def wheelEvent(self, event):
        """Handle a mouse wheel rotation."""

        if event.angleDelta().y() < 0:
            new_level = self.level + 1
        else:
            new_level = self.level - 1

        self.zoom_level(new_level)

    def resizeEvent(self, event=None):
        """Widget resized, recompute some state."""

        # new widget size
        self.view_width = self.width()
        self.view_height = self.height()

        # recalculate the "key" tile stuff
#        self.recalc_wrap_limits()
#        self.normalize_key_after_drag(0, 0)
        self.rectify_key_tile()

    def enterEvent(self, event):
#        self.setFocus()
        pass

    def leaveEvent(self, event):
        pass

    def paintEvent(self, event):
        """Draw the base map and then the layers on top."""

        log(f'paintEvent: .key_tile_left={self.key_tile_left}, .key_tile_xoffset={self.key_tile_xoffset}')
        log(f'paintEvent: .key_tile_top={self.key_tile_top}, .key_tile_yoffset={self.key_tile_yoffset}')

        ######
        # The "key" tile position is maintained by other code, we just
        # assume it's set.  Figure out how to draw tiles, set up 'row_list' and
        # 'col_list' which are list of tile coords to draw (row and colums).
        ######

        col_list = []
        x_coord = self.key_tile_left
        x_pix_start = self.key_tile_xoffset
        while x_pix_start < self.view_width:
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
                painter.drawPixmap(x_pix, y_pix,
                                    self.tile_src.GetTile(x, y))
                y_pix += self.tile_height
            x_pix += self.tile_width

        # now draw the layers
        for id in self.layer_z_order:
            l = self.layer_mapping[id]
            if l.visible and self.level in l.show_levels:
                l.painter(painter, l.data, map_rel=l.map_rel)

        painter.end()

    ######
    #
    ######

    def normalize_key_after_drag(self, delta_x=None, delta_y=None):
        """After drag, set "key" tile correctly.

        delta_x  the X amount dragged (pixels), None if not dragged in X
        delta_y  the Y amount dragged (pixels), None if not dragged in Y

        The 'key' tile was corect, but we've moved the map in the X and Y
        directions.  Normalize the 'key' tile taking into account whether
        we are wrapping X or Y directions.

        Dragging left gets a positive delta_x, up gets a positive delta_y.
        We call this routine to initialize things after zoom (for instance),
        passing 0 drag deltas.
        """

        if self.wrap_x:
            # wrapping in X direction, move 'key' tile in X
            self.key_tile_xoffset -= delta_x

            # normalize .key_tile_left value
            while self.key_tile_xoffset > 0:
                # 'key' tile too far right, move one left
                self.key_tile_left -= 1
                self.key_tile_xoffset -= self.tile_width
    
            while self.key_tile_xoffset <= -self.tile_width:
                # 'key' tile too far left, move one right
                self.key_tile_left += 1
                self.key_tile_xoffset += self.tile_width
            self.key_tile_left = (self.key_tile_left + self.num_tiles_x) % self.num_tiles_x
        else:
            # not wrapping in X direction
            if self.map_width <= self.view_width:
                # if map <= view, don't drag, ensure centred
                self.key_tile_xoffset = (self.view_width - self.map_width) // 2
            else:
                # maybe drag, but don't expose background on left or right sides
                # remember old 'key' tile left value
                old_left = self.key_tile_left

                # move key tile by amount of X drag
                self.key_tile_xoffset -= delta_x

                while self.key_tile_xoffset > 0:
                    # 'key' tile too far right
                    self.key_tile_left -= 1
                    self.key_tile_xoffset -= self.tile_width
        
                while self.key_tile_xoffset <= -self.tile_width:
                    # 'key' tile too far left
                    self.key_tile_left += 1
                    self.key_tile_xoffset += self.tile_width
                self.key_tile_left = (self.key_tile_left + self.num_tiles_x) % self.num_tiles_x

                if delta_x < 0:
                    # was dragged to the right, don't allow left edge to show
                    if self.key_tile_left > old_left:
                        self.key_tile_left = 0
                        self.key_tile_xoffset = 0
                else:
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

            # normalize .key_tile_top value
            while self.key_tile_yoffset > 0:
                # 'key' tile too far right, move one left
                self.key_tile_top -= 1
                self.key_tile_yoffset -= self.tile_height
    
            while self.key_tile_yoffset <= -self.tile_height:
                # 'key' tile too far left, move one right
                self.key_tile_top += 1
                self.key_tile_yoffset += self.tile_height
            self.key_tile_top = (self.key_tile_top + self.num_tiles_y) % self.num_tiles_y
        else:
            # not wrapping in the Y direction
            if self.map_height <= self.view_height:
                # if map <= view, don't drag, ensure centred
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
                    # if dragged too far, reset key tile data
                    if self.key_tile_top > self.max_key_top:
                        self.key_tile_top = self.max_key_top
                        self.key_tile_yoffset = self.max_key_yoffset
                    elif self.key_tile_top == self.max_key_top:
                        if self.key_tile_yoffset < self.max_key_yoffset:
                            self.key_tile_yoffset = self.max_key_yoffset

    ######
    #
    ######

# UNUSED
    def use_level(self, level):
        """Use new map level.

        level  the new level to use

        This code will try to maintain the centre of the view at the same
        GEO coordinates, if possible.  The "key" tile is updated.

        Returns True if level change is OK, else False.
        """

        return self.zoom_level(level)

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

        # convert tile fractional coords to tile # + offset
        (tile_left, tile_xoff) = self.tile_frac_to_parts(x_frac, self.tile_width)
        (tile_top, tile_yoff) = self.tile_frac_to_parts(y_frac, self.tile_height)

        if scale > 1:
            # assume scale is 2
            # a simple doubling of fractional coordinates
            if tile_xoff < self.tile_width // 2:
                tile_left = tile_left * 2
                tile_xoff = tile_xoff * 2
            else:
                tile_left = tile_left*2 + 1
                tile_xoff = tile_xoff*2 - self.tile_width
    
            if tile_yoff < self.tile_height // 2:
                tile_top = tile_top * 2
                tile_yoff = tile_yoff * 2
            else:
                tile_top = tile_top*2 + 1
                tile_yoff = tile_yoff*2 % self.tile_height
        else:
            # assume scale is 0.5
            # a simple halving of fractional coordinates
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
    
        zx_frac = self.tile_parts_to_frac(tile_left, tile_xoff, self.tile_width)
        zy_frac = self.tile_parts_to_frac(tile_top, tile_yoff, self.tile_height)

        return (zx_frac, zy_frac)

# UNUSED
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

        (r_int, r_frac) = self.tile_frac_to_parts(top_coord, self.tile_height)
        key_tile_top = r_int
        key_tile_yoffset = -r_frac # * self.tile_height

        return (key_tile_left, key_tile_xoffset, key_tile_top, key_tile_yoffset)

# UNUSED
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

        # work out X tile coordinate
        dx = x - self.key_tile_xoffset     # pixels from key tile left to point
        (dx_whole, dx_off) = divmod(dx, self.tile_width)   # (a // b, a % b)
        tile_x = self.key_tile_left + dx_whole + dx_off/self.tile_width

        # work out Y tile coordinate
        d_y = y - self.key_tile_yoffset     # pixels from key tile top to point
        dy_whole = d_y // self.tile_height  # number of complete tiles to point
        dy_off = d_y % self.tile_height     # left over piyels
        tile_y = self.key_tile_top + dy_whole + dy_off/self.tile_height

        return (tile_x, tile_y)

    ######
    # Layer manipulation routines.
    ######

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

        # get unique layer ID
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

    def ShowLayer(self, id):
        """Show a layer.

        id  the layer id
        """

        self.layer_mapping[id].visible = True
        self.update()

    def HideLayer(self, id):
        """Hide a layer.

        id  the layer id
        """

        self.layer_mapping[id].visible = False
        self.update()

    def DeleteLayer(self, id):
        """Delete a layer.

        id  the layer id
        """

        # just in case we got None
        if id:
            # see if what we are about to remove might be visible
            layer = self.layer_mapping[id]
            visible = layer.visible

            del layer
            self.layer_z_order.remove(id)

            # if layer was visible, refresh display
            if visible:
                self.update()

    def SetLayerShowLevels(self, id, show_levels=None):
        """Update the show_levels list for a layer.

        id           ID of the layer we are going to update
        show_levels  new layer show list

        If 'show_levels' is None reset the displayable levels to
        all levels in the current tileset.
        """

        # if we actually got an 'id' change the .show_levels value
        if id:
            layer = self.layer_mapping[id]

            # if not given a 'show_levels' show all levels available
            if not show_levels:
                show_levels = range(self.tiles_min_level,
                                    self.tiles_max_level+1)[:]

            layer.show_levels = show_levels

            # always update the display, there may be a change
            self.update()

    def SetLayerSelectable(self, id, selectable=False):
        """Update the .selectable attribute for a layer.

        id          ID of the layer we are going to update
        selectable  new .selectable attribute value (True or False)
        """

        # just in case id is None
        if id:
            layer = self.layer_mapping[id]
            layer.selectable = selectable

    ######
    # Layer drawing routines
    ######

    def draw_point_layer(self, dc, data, map_rel):
        """Draw a points layer.

        dc       the active device context to draw on
        data     an iterable of point tuples:
                     (x, y, place, radius, colour, x_off, y_off, udata)
        map_rel  points relative to map if True, else relative to view
        """

        # get correct pex function - this handles map or view
        pex = self.pex_point_view
        if map_rel:
            pex = self.pex_point

        # speed up drawing mostly not changing colours
        cache_pcolour = None

        # draw points on map/view
        for (x, y, place, radius, pcolour, x_off, y_off, udata) in data:
            (pt, ex) = pex(place, (x,y), x_off, y_off, radius)
            if ex and radius:  # don't draw if not on screen or zero radius
                if cache_pcolour != pcolour:
                    qcolour = QColor(*pcolour)
                    pen = QPen(qcolour, radius, Qt.SolidLine)
                    dc.setPen(pen)
                    dc.setBrush(qcolour)
                    cache_pcolour = pcolour
                (pt_x, pt_y) = pt
                dc.drawEllipse(QPoint(pt_x, pt_y), radius, radius)

    def draw_image_layer(self, dc, images, map_rel):
        """Draw an image Layer on the view.

        dc       the active device context to draw on
        images   a sequence of image tuple sequences
                   (x,y,pmap,w,h,placement,offset_x,offset_y,idata)
        map_rel  points relative to map if True, else relative to view
        """

        # get correct pex function
        pex = self.pex_extent_view
        if map_rel:
            pex = self.pex_extent

        # speed up drawing by caching previous colour
        cache_colour = None

        # draw the images
        for (lon, lat, pmap, w, h, place,
                 x_off, y_off, pradius, pcolour, idata) in images:
            (pt, ex) = pex(place, (lon, lat), x_off, y_off, w, h)
            if ex:
                (ix, iy) = pt
                size = pmap.size()
                dc.drawPixmap(QPoint(ix, iy), pmap)

            if pradius:
                if cache_pcolour != pcolour:
                    pen = QPen(pcolour, pradius, Qt.SolidLine)
                    painter.setPen(pen)
                    paint.setBrush(pen)
                    cache_pcolour = pcolour
                (px, py) = pt
                dc.drawEllipse(QPoint(px, py), pradius, pradius)

    def draw_text_layer(self, dc, text, map_rel):
        """Draw a text Layer on the view.

        dc       the active device context to draw on
        text     a sequence of tuples:
                     (lon, lat, tdata, placement, radius, colour, fontname,
                      fontsize, offset_x, offset_y, tdata)
        map_rel  points relative to map if True, else relative to view
        """

        # get correct pex function for mode (map/view)
        pex = self.pex_extent_view
        if map_rel:
            pex = self.pex_extent

        # set some caching to speed up mostly unchanging data
        cache_textcolour = None
        cache_font = None
        cache_colour = None

        # draw text on map/view
        for (lon, lat, tdata, place, radius, colour,
                textcolour, fontname, fontsize, x_off, y_off, data) in text:

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

            # get point + extent information (each can be None if off-view)
            (pt, ex) = pex(place, (lon, lat), x_off, y_off, w, h)
            if ex:              # don't draw text if off screen
                (lx, _, ty, _) = ex
                dc.drawText(QPointF(lx, ty), tdata)

            if pt and radius:   # don't draw point if off screen or zero radius
                (x, y) = pt
                if cache_colour != colour:
                    qcolour = QColor(*colour)
                    pen = QPen(qcolour, radius, Qt.SolidLine)
                    dc.setPen(pen)
                    dc.setBrush(qcolour)
                    cache_colour = colour
                dc.drawEllipse(QPoint(x, y), radius, radius)

    def draw_polygon_layer(self, dc, data, map_rel):
        """Draw a polygon layer.

        dc       the active device context to draw on
        data     an iterable of polygon tuples:
                     (p, placement, width, colour, closed,
                      filled, fillcolour, offset_x, offset_y, udata)
                 where p is an iterable of points: (x, y)
        map_rel  points relative to map if True, else relative to view
        """

        # get the correct pex function for mode (map/view)
        pex = self.pex_polygon_view
        if map_rel:
            pex = self.pex_polygon

        # draw polygons
        cache_colour_width = None         # speed up mostly unchanging data
        cache_fillcolour = (0, 0, 0, 0)

        dc.setBrush(QBrush(QColor(*cache_fillcolour))) # initial brush is transparent

        for (p, place, width, colour, closed,
                 filled, fillcolour, x_off, y_off, udata) in data:
            (poly, extent) = pex(place, p, x_off, y_off)
            if poly:
                if (colour, width) != cache_colour_width:
                    dc.setPen(QPen(QColor(*colour), width, Qt.SolidLine))
                    cache_colour = (colour, width)

                if filled and (fillcolour != cache_fillcolour):
                    dc.setBrush(QBrush(QColor(*fillcolour), Qt.SolidPattern))
                    cache_fillcolour = fillcolour

                qpoly = [QPoint(*p) for p in poly]
                dc.drawPolygon(QPolygon(qpoly))

    def draw_polyline_layer(self, dc, data, map_rel):
        """Draw a polyline layer.

        dc       the active device context to draw on
        data     an iterable of polyline tuples:
                     (p, placement, width, colour, offset_x, offset_y, udata)
                 where p is an iterable of points: (x, y)
        map_rel  points relative to map if True, else relative to view
        """

        # get the correct pex function for mode (map/view)
        pex = self.pex_polygon_view
        if map_rel:
            pex = self.pex_polygon

        # brush is always transparent
        dc.setBrush(QBrush(QColor(0, 0, 0, 0)))

        # draw polyline(s)
        cache_colour_width = None       # speed up mostly unchanging data

        for (p, place, width, colour, x_off, y_off, udata) in data:
            (poly, extent) = pex(place, p, x_off, y_off)
            if poly:
                if cache_colour_width != (colour, width):
                    dc.setPen(QPen(QColor(*colour), width, Qt.SolidLine))
                    cache_colour_width = (colour, width)
                qpoly = [QPoint(*p) for p in poly]
                dc.drawPolyline(QPolygon(qpoly))

    def view_extent(self, place, view, w, h, x_off, y_off, dcw=0, dch=0):
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
        (left, top) = self.extent_placement(place, x, y, x_off, y_off, w, h, dcw, dch)

        # bottom right corner
        right = left + w
        bottom = top + h

        return (left, right, top, bottom)

######
# Convert between geo and view coordinates
######

    def geo_to_view(self, geo):
        """Convert a geo coord to view.

        geo  tuple (xgeo, ygeo)

        Return a tuple (xview, yview) in view coordinates.
        Assumes point is in view.
        """

        # convert the Geo position to tile coordinates
        (tx, ty) = self.tile_src.Geo2Tile(geo)

        # using the key_tile_* variables to convert to view coordinates
        xview = (tx - self.key_tile_left) * self.tile_width + self.key_tile_xoffset
        yview = (ty - self.key_tile_top) * self.tile_height + self.key_tile_yoffset

        return (xview, yview)

    def geo_to_view_masked(self, geo):
        """Convert a geo (lon+lat) position to view pixel coords.

        geo  tuple (xgeo, ygeo)

        Return a tuple (xview, yview) of point if on-view,or None
        if point is off-view.
        """

        (xgeo, ygeo) = geo

        if (self.view_llon <= xgeo <= self.view_rlon and
                self.view_blat <= ygeo <= self.view_tlat):
            return self.geo_to_view(geo)

        return None

    def view_to_geo(self, view):
        """Convert a view coords position to a geo coords position.

        view  tuple of view coords (xview, yview)

        Returns a tuple of geo coords (xgeo, ygeo) if the cursor is over map
        tiles, else returns None.
        """

        (xview, yview) = view
        (min_xgeo, max_xgeo, min_ygeo, max_ygeo) = self.tile_src.GetExtent()

        x_from_key = xview - self.key_tile_xoffset
        y_from_key = yview - self.key_tile_yoffset

        # get view point as tile coordinates
        xtile = self.key_tile_left + x_from_key/self.tile_width
        ytile = self.key_tile_top + y_from_key/self.tile_height

        result = (xgeo, ygeo) = self.tile_src.Tile2Geo((xtile, ytile))

        if self.wrap_x and self.wrap_y:
            return result
        if not self.wrap_x:
            if not (min_xgeo <= xgeo <= max_xgeo):
                return None
        if not self.wrap_y:
            if not (min_ygeo <= ygeo <= max_ygeo):
                return None

        return result

######
# PEX - Point & EXtension.
#
# These functions encapsulate the code that finds the extent of an object.
# They all return a tuple (point, extent) where 'point' is the placement
# point of an object (or list of points for a polygon) and an 'extent'
# tuple (lx, rx, ty, by) [left, right, top, bottom].
######

    def pex_point(self, place, geo, x_off, y_off, radius):
        """Given a point object (geo coords) get point/extent in view coords.

        place         placement string
        geo           point position tuple (xgeo, ygeo)
        x_off, y_off  X and Y offsets

        Return a tuple of point and extent origins (point, extent) where 'point'
        is (px, py) and extent is (elx, erx, ety, eby) (both in view coords).
        Return None for extent if extent is completely off-view.

        The 'extent' here is the extent of the point+radius.
        """

        # get point view coords
        (xview, yview) = self.geo_to_view(geo)
        point = self.point_placement(place, xview, yview, x_off, y_off)
        (px, py) = point

        # extent = (left, right, top, bottom) in view coords
        elx = px - radius
        erx = px + radius
        ety = py - radius
        eby = py + radius
        extent = (elx, erx, ety, eby)

        # decide if extent is off-view
        if erx < 0 or elx > self.view_width or eby < 0 or ety > self.view_height:
            # no extent if ALL of extent is off-view
            extent = None

        return (point, extent)

    def pex_point_view(self, place, view, x_off, y_off, radius):
        """Given a point object (view coords) get point/extent in view coords.

        place         placement string
        view          point position tuple (xview, yview)
        x_off, y_off  X and Y offsets

        Return a tuple of point and extent origins (point, extent) where 'point'
        is (px, py) and extent is (elx, erx, ety, eby) (both in view coords).
        Return None for extent if extent is completely off-view.

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

        # decide if extent is off-view
        if erx < 0 or elx > self.view_width or eby < 0 or ety > self.view_height:
            # no extent if ALL of extent is off-view
            extent = None

        return (point, extent)

    def pex_extent(self, place, geo, x_off, y_off, w, h):
        """Given an extent object convert point/extent coords to view coords.

        place         placement string
        geo           point position tuple (xgeo, ygeo)
        x_off, y_off  X and Y offsets
        w, h          width and height of extent in pixels

        Return a tuple ((px, py), (elx, erx, ety, eby)) of point and extent
        data where '(px, py)' is the point and '(elx, erx, ety, eby)' is the
        extent.  Both point and extent are in view coordinates.

        Return None for extent if extent is completely off-view.

        An extent object can be either an image object or a text object.
        """

        # get point view coords
        point = self.geo_to_view(geo)
        (px, py) = point

        # get extent limits
        elx = px
        erx = px + w
        ety = py
        eby = py + h

        # decide if extent is off-view
        if erx < 0 or elx > self.view_width or eby < 0 or ety > self.view_height:
            # no extent if ALL of extent is off-view
            extent = None

        return (point, (elx, erx, ety, eby))

    def pex_extent_view(self, place, view, x_off, y_off, w, h):
        """Given a view object convert point/extent coords to view coords.

        place         placement string
        view          point position tuple (xview, yview)
        x_off, y_off  X and Y offsets
        w, h          width and height of extent in pixels

        Return a tuple of point and extent origins (point, extent) where 'point'
        is (px, py) and extent is (elx, erx, ety, eby) (both in view coords).
        Return None for extent if extent is completely off-view.

        Takes size of extent object into consideration.
        """

        # get point view coords and perturb point to placement origin
        (xview, yview) = view
        point = self.extent_placement(place, xview, yview, x_off, y_off,
                                      w, h, self.view_width, self.view_height)

        # get point view coords (X and Y)
        (px, py) = point

        # extent = (left, right, top, bottom) in view coords
        elx = xview
        erx = xview + w
        ety = yview
        eby = yview + h

        if erx < 0 or elx > self.view_width or eby < 0 or ety > self.view_height:
            # no extent if ALL of extent is off-view
            extent = None

        return (point, (elx, erx, ety, eby))

    def pex_polygon(self, place, poly, x_off, y_off):
        """Given a polygon/line obj (geo coords) get points/extent in view coords.

        place         placement string
        poly          list of point position tuples (xgeo, ygeo)
        x_off, y_off  X and Y offsets

        Return a tuple of point and extent (point, extent) where 'point' is a
        list of (px, py) and extent is (elx, erx, ety, eby) (both in view coords).
        Return None for extent if extent is completely off-view.
        """

        # get polygon/line points in perturbed view coordinates
        view_points = []
        for geo in poly:
            (xview, yview) = self.geo_to_view(geo)
            point = self.point_placement(place, xview, yview, x_off, y_off)
            view_points.append(point)

        # get extent - max/min x and y
        # extent = (left, right, top, bottom) in view coords
        elx = min(view_points, key=lambda x: x[0])[0]
        erx = max(view_points, key=lambda x: x[0])[0]
        ety = min(view_points, key=lambda x: x[1])[1]
        eby = max(view_points, key=lambda x: x[1])[1]
        extent = (elx, erx, ety, eby)

        # decide if extent is off-view
        res_ex = None       # assume extent is off-view
        for (px, py) in view_points:
            if ((px >= 0 and px < self.view_width)
                    and (py >= 0 and py < self.view_height)):
                res_ex = extent # at least some of extent is on-view
                break

        return (view_points, res_ex)

    def pex_polygon_view(self, place, poly, x_off, y_off):
        """Given a polygon/line obj (view coords) get point/extent in view coords.

        place         placement string
        poly          list of point position tuples (xview, yview)
        x_off, y_off  X and Y offsets

        Return a tuple of point and extent origins (point, extent) where 'point'
        is a list of (px, py) and extent is (elx, erx, ety, eby) (both in view
        coords).  Return None for extent if extent is completely off-view.
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
        res_ex = None
        for (px, py) in view:
            if ((px >= 0 and px < self.view_width)
                    and (py >= 0 and py < self.view_height)):
                res_ex = extent
                break

        return (view, res_ex)

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
        dcw, dcw      width/height of the view draw context (zero if map-rel)

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

    ######
    # Play with layers Z order
    ######

    def PushLayerToBack(self, id):
        """Make layer specified be drawn at back of Z order.

        id  ID of the layer to push to the back
        """

        self.layer_z_order.remove(id)
        self.layer_z_order.insert(0, id)
        self.update()

    def PopLayerToFront(self, id):
        """Make layer specified be drawn at front of Z order.

        id  ID of the layer to pop to the front
        """

        self.layer_z_order.remove(id)
        self.layer_z_order.append(id)
        self.update()

    def PlaceLayerBelowLayer(self, id, top_id):
        """Place a layer so it will be drawn behind another layer.

        id      ID of layer to place underneath 'top_id'
        top_id  ID of layer to be drawn *above* 'id'
        """

        self.layer_z_order.remove(id)
        i = self.layer_z_order.index(top_id)
        self.layer_z_order.insert(i, id)
        self.update()

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

    def zoom_level(self, level):
        """Zoom to a map level.

        level  map level to zoom to

        Change the map zoom level to that given. Returns True if the zoom
        succeeded, else False. If False is returned the method call has no effect.
        """

        # get geo coords of view centre point
        x = self.view_width / 2
        y = self.view_height / 2
        geo = self.view_to_geo((x, y))

        # get tile source to use the new level
        result = self.tile_src.UseLevel(level)

        if result:
            # zoom worked, adjust state variables
            self.level = level

            # move to new level
            (self.num_tiles_x, self.num_tiles_y, _, _) = self.tile_src.GetInfo(level)
            self.map_width = self.num_tiles_x * self.tile_width
            self.map_height = self.num_tiles_y * self.tile_height

#            self.recalc_wrap_limits()
#            self.normalize_key_after_drag(0, 0)
###            self.rectify_key_tile()

            # finally, pan to original map centre (updates widget)
            self.pan_position(geo)
            self.events.EVT_PYSLIPQT_LEVEL.emit(PySlipQt.EVT_PYSLIPQT_LEVEL, level)

            # trigger an EVT_PYSLIPQT_POSITION event to update any user widget
            # TODO

        return result

    def pan_position(self, geo):
        """Pan to the given geo position in the current map zoom level.

        geo  a tuple (xgeo, ygeo)

        We just adjust the key tile to place the required geo pisition in the
        middle of the view.  If that is not possible, just centre in either
        the X or Y directions, or both.
        """

        # convert the geo posn to a tile position
        (tile_x, tile_y) = self.tile_src.Geo2Tile(geo)

        # determine what the new key tile should be
        # figure out number of tiles from centre point to edges
        tx = (self.view_width / 2) / self.tile_width
        ty = (self.view_height / 2) / self.tile_height
        
        # calculate tile coordinates of the top-left corner of the view
        key_tx = tile_x - tx
        key_ty = tile_y - ty

        (key_tile_left, x_offset) = divmod(key_tx, 1)
        self.key_tile_left = int(key_tile_left)
        self.key_tile_xoffset = -int(x_offset * self.tile_width)

        (key_tile_top, y_offset) = divmod(key_ty, 1)
        self.key_tile_top = int(key_tile_top)
        self.key_tile_yoffset = -int(y_offset * self.tile_height)

        # adjust key tile, if necessary
        self.rectify_key_tile()

        # redraw the widget
        self.update()

    def rectify_key_tile(self):
        """Adjust state variables to ensure map centred if map is smaller than
        view.  Otherwise don't allow edges to be exposed.
       
        Adjusts the "key" tile variables to ensure proper presentation.
        """

        # check map in X direction
        if self.map_width < self.view_width:
            # map < view, fits totally in view, centre in X
            self.key_tile_left = 0
            self.key_tile_xoffset = (self.view_width - self.map_width) // 2
        else:
            # if key tile out of map in X direction, rectify
            if self.key_tile_left < 0:
                self.key_tile_left = 0
                self.key_tile_xoffset = 0
            else:
                # if map left/right edges showing, cover them
                show_len = (self.num_tiles_x - self.key_tile_left)*self.tile_width + self.key_tile_xoffset
                if show_len < self.view_width:
                    # figure out key tile X to have right edge of map and view equal
                    tiles_showing = self.view_width / self.tile_width
                    int_tiles = int(tiles_showing)
                    self.key_tile_left = self.num_tiles_x - int_tiles - 1
                    self.key_tile_xoffset = -int((1.0 - (tiles_showing - int_tiles)) * self.tile_width)

        # now check map in Y direction
        if self.map_height < self.view_height:
            # map < view, fits totally in view, centre in Y
            self.key_tile_top = 0
            self.key_tile_yoffset = (self.view_height - self.map_height) // 2
        else:
            if self.key_tile_top < 0:
                # map top edge showing, cover
                self.key_tile_top = 0
                self.key_tile_yoffset = 0
            else:
                # if map bottom edge showing, cover
                show_len = (self.num_tiles_y - self.key_tile_top)*self.tile_height + self.key_tile_yoffset
                if show_len < self.view_height:
                    # figure out key tile Y to have bottom edge of map and view equal
                    tiles_showing = self.view_height / self.tile_height
                    int_tiles = int(tiles_showing)
                    self.key_tile_top = self.num_tiles_y - int_tiles - 1
                    self.key_tile_yoffset = -int((1.0 - (tiles_showing - int_tiles)) * self.tile_height)

    def zoom_level_position(self, level, posn):
        """Zoom to a map level and pan to the given position in the map.

        level  map level to zoom to
        posn  a tuple (xgeo, ygeo)
        """

        if self.zoom_level(level):
            self.pan_position(posn)

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

# UNUSED
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

# UNUSED
    def warn(self, msg):
        """Display a warning message, in the log and graphically."""

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

        return self.add_layer(self.draw_point_layer, draw_data, map_rel,
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
        pmap_cache = None
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
                pmap = pmap_cache
                w = w_cache
                h = h_cache
            else:
                fname_cache = fname
                pmap_cache = pmap = QPixmap(fname)
                size = pmap.size()
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

            draw_data.append((float(lon), float(lat), pmap, w, h, placement,
                              offset_x, offset_y, radius, colour, udata))

        return self.add_layer(self.draw_image_layer, draw_data, map_rel,
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
            textcolour = self.colour_to_internal(textcolour)

            draw_data.append((float(lon), float(lat), tdata, placement.lower(),
                              radius, colour, textcolour, fontname, fontsize,
                              offset_x, offset_y, udata))

        return self.add_layer(self.draw_text_layer, draw_data, map_rel,
                             visible=visible, show_levels=show_levels,
                             selectable=selectable, name=name,
                             type=self.TypeText)

    def AddPolygonLayer(self, data, map_rel=True, visible=True,
                        show_levels=None, selectable=False,
                        name='<polygon_layer>', **kwargs):
        """Add a layer of polygon data to the map.

        data         iterable of polygon tuples:
                         (points[, attributes])
                     where points is another iterable of (x, y) tuples and
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
                       '(points, [attributes])\n'
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

            # append this polygon to the layer data
            draw_data.append((p, placement, width, colour, close,
                              filled, fillcolour, offset_x, offset_y, udata))

        return self.add_layer(self.draw_polygon_layer, draw_data, map_rel,
                             visible=visible, show_levels=show_levels,
                             selectable=selectable, name=name,
                             type=self.TypePolygon)

    def AddPolylineLayer(self, data, map_rel=True, visible=True,
                        show_levels=None, selectable=False,
                        name='<polyline>', **kwargs):
        """Add a layer of polyline data to the map.

        data         iterable of polyline tuples:
                         (points[, attributes])
                     where points is another iterable of (x, y) tuples and
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

        return self.add_layer(self.draw_polyline_layer, draw_data, map_rel,
                             visible=visible, show_levels=show_levels,
                             selectable=selectable, name=name,
                             type=self.TypePolyline)

######
# Positioning methods
######

    def GotoLevel(self, level):
        """Use a new tile level.

        level  the new tile level to use.

        Returns True if all went well.
        """

        if not self.tile_src.UseLevel(level):
            return False        # couldn't change level

        self.level = level
        self.map_width = self.tile_src.num_tiles_x * self.tile_width
        self.map_height = self.tile_src.num_tiles_y * self.tile_height
        (self.map_llon, self.map_rlon,
         self.map_blat, self.map_tlat) = self.tile_src.extent

        # to set some state variables
        self.resizeEvent()

        # raise level change event
        self.events.EVT_PYSLIPQT_LEVEL.emit(PySlipQt.EVT_PYSLIPQT_LEVEL, level)

        return True

    def GotoPosition(self, geo):
        """Set view to centre on a geo position in the current level.

        geo  a tuple (xgeo,ygeo) to centre view on

        Sets self.view_offset_x and self.view_offset_y and then calls
        RecalcViewLimits(), redraws widget.
        """

        # get fractional tile coords of required centre of view
        (xtile, ytile) = self.tile_src.Geo2Tile(geo)

        # now calculate view offsets, top, left, bottom and right
        half_width = self.view_width / 2
        centre_pixels_from_map_left = int(xtile * self.tile_width)
        self.view_offset_x = centre_pixels_from_map_left - half_width

        half_height = self.view_height / 2
        centre_pixels_from_map_top = int(ytile * self.tile_height)
        self.view_offset_y = centre_pixels_from_map_top - half_height

        # set the left/right/top/bottom lon/lat extents and redraw view
#        self.RecalcViewLimits()
# TODO: update routine to set 'key' tile stuff.
        self.update()

    def GotoLevelAndPosition(self, level, geo):
        """Goto a map level and set view to centre on a position.

        level  the map level to use
        geo    a tuple (xgeo,ygeo) to centre view on

        Does nothing if we can't use desired level.
        """

        if self.GotoLevel(level):
            self.GotoPosition(geo)

    def ZoomToArea(self, geo, size):
        """Set view to level and position to view an area.

        geo   a tuple (xgeo,ygeo) to centre view on
        size  a tuple (width,height) of area in degrees

        Centre an area and zoom to view such that the area will fill
        approximately 50% of width or height, whichever is greater.

        Use the ppd_x and ppd_y values in the level 'tiles' file.
        """

        # unpack area width/height (degrees)
        (awidth, aheight) = size

        # step through levels (smallest first) and check view size (degrees)
        for l in self.tile_src.levels:
            level = l
            (_, _, ppd_x, ppd_y) = self.tile_src.getInfo(l)
            view_deg_width = self.view_width / ppd_x
            view_deg_height = self.view_height / ppd_y

            # if area >= 50% of view, finished
            if awidth >= view_deg_width / 2 or aheight >= view_deg_height / 2:
                break

        self.GotoLevelAndPosition(level, geo)

######
#
######

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
                c = QColor(colour)      # TODO catch bad colour names
                result = (c.red(), c.blue(), c.green(), c.alpha())
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

    def sel_box_canonical(self):
        """'Canonicalize' a selection box limits.

        Uses instance variables (all in view coordinates):
            self.sbox_1_x    X position of box select start
            self.sbox_1_y    Y position of box select start
            self.sbox_w      width of selection box (start to finish)
            self.sbox_h      height of selection box (start to finish)

        Four ways to draw the selection box (starting in each of the four
        corners), so four cases.

        The sign of the width/height values are decided with respect to the
        origin at view top-left corner.  That is, a negative width means
        the box was started at the right and swept to the left.  A negative
        height means the selection started low and swept high in the view.

        Returns a tuple (llx, llr, urx, ury) where llx is lower left X, ury is
        upper right corner Y, etc.  All returned values in view coordinates.
        """

        if self.sbox_h >= 0:
            if self.sbox_w >= 0:
                # 2
                ll_corner_vx = self.sbox_1_x
                ll_corner_vy = self.sbox_1_y + self.sbox_h
                tr_corner_vx = self.sbox_1_x + self.sbox_w
                tr_corner_vy = self.sbox_1_y
            else:
                # 1
                ll_corner_vx = self.sbox_1_x + self.sbox_w
                ll_corner_vy = self.sbox_1_y + self.sbox_h
                tr_corner_vx = self.sbox_1_x
                tr_corner_vy = self.sbox_1_y
        else:
            if self.sbox_w >= 0:
                # 3
                ll_corner_vx = self.sbox_1_x
                ll_corner_vy = self.sbox_1_y
                tr_corner_vx = self.sbox_1_x + self.sbox_w
                tr_corner_vy = self.sbox_1_y + self.sbox_h
            else:
                # 4
                ll_corner_vx = self.sbox_1_x + self.sbox_w
                ll_corner_vy = self.sbox_1_y
                tr_corner_vx = self.sbox_1_x
                tr_corner_vy = self.sbox_1_y + self.sbox_h

        return (ll_corner_vx, ll_corner_vy, tr_corner_vx, tr_corner_vy)

######
# Select helpers - get objects that were selected
######

    def sel_point_in_layer(self, layer, view_pt, map_pt):
        """Determine if clicked location selects a point in layer data.

        layer    layer object we are looking in
        view_pt  click location tuple (view coords)
        map_pt   click location tuple (geo coords)

        We must look for the nearest point to the selection point.

        Return None (no selection) or (point, data, None) of selected point
        where point is [(x,y,attrib)] where X and Y are map or view relative
        depending on layer.map_rel.  'data' is the data object associated with
        each selected point.  The None is a placeholder for the relative
        selection point, which is meaningless for point selection.
        """

        # TODO: speed this up?  Do we need to??
        # http://en.wikipedia.org/wiki/Kd-tree
        # would need to create kd-tree in AddLayer()

        result = None
        delta = layer.delta
        dist = 9999999.0        # more than possible

        # get correct pex function (map-rel or view-rel)
        pex = self.pex_point_view
        if layer.map_rel:
            pex = self.pex_point

        # find selected point on map/view
        (map_x, map_y) = map_pt
        (view_x, view_y) = view_pt
        for (x, y, place, radius, colour, x_off, y_off, udata) in layer.data:
            (vp, _) = pex(place, (x,y), x_off, y_off, radius)
            if vp:
                (vx, vy) = vp
                d = (vx - view_x)*(vx - view_x) + (vy - view_y)*(vy - view_y)
                if d < dist:
                    rpt = (x, y, {'placement': place,
                                  'radius': radius,
                                  'colour': colour,
                                  'offset_x': x_off,
                                  'offset_y': y_off})
                    result = ([rpt], udata, None)
                    dist = d

        if dist <= layer.delta:
            return result
        return None

    def sel_box_points_in_layer(self, layer, ll, ur):
        """Get list of points inside box.

        layer  reference to layer object we are working on
        ll     lower-left corner point of selection box (geo or view)
        ur     upper-right corner point of selection box (geo or view)

        Return a tuple (selection, data) where 'selection' is a list of
        selected point positions (xgeo,ygeo) and 'data' is a list of userdata
        objects associated withe selected points.

        If nothing is selected return None.
        """

        # get a list of points inside the selection box
        selection = []
        data = []

        # get correct pex function and box limits in view coords
        pex = self.pex_point_view
        (blx, bby) = ll
        (brx, bty) = ur
        if layer.map_rel:
            pex = self.pex_point
            (blx, bby) = self.geo_to_view(ll)
            (brx, bty) = self.geo_to_view(ur)

        # get points selection
        for (x, y, place, radius, colour, x_off, y_off, udata) in layer.data:
            (vp, _) = pex(place, (x,y), x_off, y_off, radius)
            if vp:
                (vpx, vpy) = vp
                if blx <= vpx <= brx and bby >= vpy >= bty:
                    selection.append((x, y, {'placement': place,
                                             'radius': radius,
                                             'colour': colour,
                                             'offset_x': x_off,
                                             'offset_y': y_off}))
                    data.append(udata)

        if selection:
            return (selection, data, None)
        return None

    def sel_image_in_layer(self, layer, point):
        """Decide if click location selects image object(s) in layer data.

        layer  layer object we are looking in
        point  click location tuple (geo or view)

        Returns either None if no selection or a tuple (selection, data, relsel)
        where 'selection' is a tuple (xgeo,ygeo) or (xview,yview) of the object
        placement point, 'data' is the data object associated with the selected
        object and 'relsel' is the relative position within the selected object
        of the mouse click.

        Note that there could conceivably be more than one image selectable in
        the layer at the mouse click position but only the first is selected.
        """

        (ptx, pty) = point
        result = None

        # get correct pex function and click point into view coords
        clickpt = point
        pex = self.pex_extent_view
        if layer.map_rel:
            clickpt = self.geo_to_view(point)
            pex = self.pex_extent
        (xclick, yclick) = clickpt

        # select image
        for (x, y, bmp, w, h, place,
                x_off, y_off, radius, colour, udata) in layer.data:
            (_, e) = pex(place, (x,y), x_off, y_off, w, h)
            if e:
                (lx, rx, ty, by) = e
                if lx <= xclick <= rx and ty <= yclick <= by:
                    selection = [(x, y, bmp, {'placement': place,
                                              'radius': radius,
                                              'colour': colour,
                                              'offset_x': x_off,
                                              'offset_y': y_off})]
                    relsel = (int(xclick - lx), int(yclick - ty))
                    result = (selection, udata, relsel)
                    break

        return result

    def sel_box_images_in_layer(self, layer, ll, ur):
        """Get list of images inside selection box.

        layer  reference to layer object we are working on
        ll     lower-left corner point of selection box (geo or view coords)
        ur     upper-right corner point of selection box (geo or view coords)

        Return a tuple (selection, data) where 'selection' is a list of
        selected point positions (xgeo,ygeo) and 'data' is a list of userdata
        objects associated withe selected points.

        If nothing is selected return None.
        """

        # get correct pex function and box limits in view coords
        pex = self.pex_extent_view
        if layer.map_rel:
            pex = self.pex_extent
            ll = self.geo_to_view(ll)
            ur = self.geo_to_view(ur)
        (vboxlx, vboxby) = ll
        (vboxrx, vboxty) = ur

        # select images in map/view
        selection = []
        data = []
        for (x, y, bmp, w, h, place,
                x_off, y_off, radius, colour, udata) in layer.data:
            (_, e) = pex(place, (x,y), x_off, y_off, w, h)
            if e:
                (li, ri, ti, bi) = e    # image extents (view coords)
                if (vboxlx <= li and ri <= vboxrx
                        and vboxty <= ti and bi <= vboxby):
                    selection.append((x, y, bmp, {'placement': place,
                                                  'radius': radius,
                                                  'colour': colour,
                                                  'offset_x': x_off,
                                                  'offset_y': y_off}))
                    data.append(udata)

        if not selection:
            return None
        return (selection, data, None)

    def sel_text_in_layer(self, layer, point):
        """Determine if clicked location selects a text object in layer data.

        layer  layer object we are looking in
        point  click location tuple (view or geo coordinates)

        Return ((x,y), data, None) for the selected text object, or None if
        no selection.  The x and y coordinates are view/geo depending on
        the layer.map_rel value.

        ONLY SELECTS ON POINT, NOT EXTENT.
        """

        result = None
        delta = layer.delta
        dist = 9999999.0

        # get correct pex function and mouse click in view coords
        pex = self.pex_point_view
        clickpt = point
        if layer.map_rel:
            pex = self.pex_point
            clickpt = self.geo_to_view(point)
        (xclick, yclick) = clickpt

        # select text in map/view layer
        for (x, y, text, place, radius, colour,
                 tcolour, fname, fsize, x_off, y_off, data) in layer.data:
            (vp, ex) = pex(place, (x,y), 0, 0, radius)
            if vp:
                (px, py) = vp
                d = (px - xclick)**2 + (py - yclick)**2
                if d < dist:
                    selection = (x, y, text, {'placement': place,
                                              'radius': radius,
                                              'colour': colour,
                                              'textcolour': tcolour,
                                              'fontname': fname,
                                              'fontsize': fsize,
                                              'offset_x': x_off,
                                              'offset_y': y_off})
                    result = ([selection], data, None)
                    dist = d

        if dist <= delta:
            return result
        return None

    def sel_box_texts_in_layer(self, layer, ll, ur):
        """Get list of text objects inside box ll-ur.

        layer  reference to layer object we are working on
        ll     lower-left corner point of selection box (geo or view)
        ur     upper-right corner point of selection box (geo or view)

        The 'll' and 'ur' points are in view or geo coords, depending on
        the layer.map_rel value.

        Returns (selection, data, None) where 'selection' is a list of text
        positions (geo or view, depending on layer.map_rel) and 'data' is a list
        of userdata objects associated with the selected text objects.

        Returns None if no selection.

        ONLY SELECTS ON POINT, NOT EXTENT.
        """

        selection = []
        data = []

        # get correct pex function and box limits in view coords
        pex = self.pex_point_view
        if layer.map_rel:
            pex = self.pex_point
            ll = self.geo_to_view(ll)
            ur = self.geo_to_view(ur)
        (lx, by) = ll
        (rx, ty) = ur

        # get texts inside box
        for (x, y, text, place, radius, colour,
                tcolour, fname, fsize, x_off, y_off, udata) in layer.data:
            (vp, ex) = pex(place, (x,y), x_off, y_off, radius)
            if vp:
                (px, py) = vp
                if lx <= px <= rx and ty <= py <= by:
                    sel = (x, y, text, {'placement': place,
                                        'radius': radius,
                                        'colour': colour,
                                        'textcolour': tcolour,
                                        'fontname': fname,
                                        'fontsize': fsize,
                                        'offset_x': x_off,
                                        'offset_y': y_off})
                    selection.append(sel)
                    data.append(udata)

        if selection:
            return (selection, data, None)
        return None

    def sel_polygon_in_layer(self, layer, point):
        """Get first polygon object clicked in layer data.

        layer  layer object we are looking in
        point  tuple of click position (xgeo,ygeo) or (xview,yview)

        Returns an iterable: ((x,y), udata) of the first polygon selected.
        Returns None if no polygon selected.
        """

        result = None

        # get correct 'point in polygon' routine
        pip = self.point_in_polygon_view
        if layer.map_rel:
            pip = self.point_in_polygon_geo

        # check polyons in layer, choose first point is inside
        for (poly, place, width, colour, close,
                 filled, fcolour, x_off, y_off, udata) in layer.data:
            if pip(poly, point, place, x_off, y_off):
                sel = (poly, {'placement': place,
                              'offset_x': x_off,
                              'offset_y': y_off})
                result = ([sel], udata, None)
                break

        return result

    def sel_box_polygons_in_layer(self, layer, p1, p2):
        """Get list of polygons inside box p1-p2 in given layer.

        layer  reference to layer object we are working on
        p1     bottom-left corner point of selection box (geo or view)
        p2     top-right corner point of selection box (geo or view)

        Return a tuple (selection, data, None) where 'selection' is a list of
        iterables of vertex positions and 'data' is a list of data objects
        associated with each polygon selected.
        """

        selection = []
        data = []

        # get correct pex function and box limits in view coords
        pex = self.pex_polygon_view
        if layer.map_rel:
            pex = self.pex_polygon
            p1 = self.geo_to_view(p1)
            p2 = self.geo_to_view(p2)
        (lx, by) = p1
        (rx, ty) = p2

        # check polygons in layer
        for (poly, place, width, colour, close,
                filled, fcolour, x_off, y_off, udata) in layer.data:
            (pt, ex) = pex(place, poly, x_off, y_off)
            if ex:
                (plx, prx, pty, pby) = ex
                if lx <= plx and prx <= rx and ty <= pty and pby <= by:
                    sel = (poly, {'placement': place,
                                  'offset_x': x_off,
                                  'offset_y': y_off})
                    selection.append(sel)
                    data.append(udata)

        if not selection:
            return None
        return (selection, data, None)

    def sel_polyline_in_layer(self, layer, point):
        """Get first polyline object clicked in layer data.

        layer  layer object we are looking in
        point  tuple of click position (xgeo,ygeo) or (xview,yview)

        Returns a tuple (sel, udata, seg) if a polyline was selected.  'sel'
        is the tuple (poly, attrib), 'udata' is userdata attached to the
        selected polyline and 'seg' is a tuple (pt1, pt2) of nearest segment
        endpoints.  Returns None if no polyline selected.
        """

        result = None
        delta = layer.delta

        # get correct 'point in polyline' routine
        pip = self.point_near_polyline_view
        if layer.map_rel:
            pip = self.point_near_polyline_geo

        # check polyons in layer, choose first where point is close enough
        for (polyline, place, width, colour, x_off, y_off, udata) in layer.data:
            seg = pip(point, polyline, place, x_off, y_off, delta=delta)
            if seg:
                sel = (polyline, {'placement': place,
                                  'offset_x': x_off,
                                  'offset_y': y_off})
                result = ([sel], udata, seg)
                break

        return result

    def sel_box_polylines_in_layer(self, layer, p1, p2):
        """Get list of polylines inside box p1-p2 in given layer.

        layer  reference to layer object we are working on
        p1     bottom-left corner point of selection box (geo or view)
        p2     top-right corner point of selection box (geo or view)

        Return a tuple (selection, data, None) where 'selection' is a list of
        iterables of vertex positions and 'data' is a list of data objects
        associated with each polyline selected.
        """

        selection = []
        data = []

        # get correct pex function and box limits in view coords
        pex = self.pex_polygon_view
        if layer.map_rel:
            pex = self.pex_polygon
            p1 = self.geo_to_view(p1)
            p2 = self.geo_to_view(p2)
        (lx, by) = p1
        (rx, ty) = p2

        # check polygons in layer
        for (poly, place, width, colour, x_off, y_off, udata) in layer.data:
            (pt, ex) = pex(place, poly, x_off, y_off)
            if ex:
                (plx, prx, pty, pby) = ex
                if lx <= plx and prx <= rx and ty <= pty and pby <= by:
                    sel = (poly, {'placement': place,
                                  'offset_x': x_off,
                                  'offset_y': y_off})
                    selection.append(sel)
                    data.append(udata)

        if not selection:
            return None
        return (selection, data, None)
