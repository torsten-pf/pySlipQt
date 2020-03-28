"""
Program to test polyline map-relative and view-relative placement.
Select what to show and experiment with placement parameters.

Usage: test_polyline_placement.py [-h|--help] [-d] [(-t|--tiles) (GMT|OSM)]
"""


import sys
import getopt
import traceback

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget,
                             QComboBox, QPushButton, QCheckBox, QLabel,
                             QGroupBox, QGridLayout, QHBoxLayout,
                             QSizePolicy, QColorDialog)

# initialize the logging system
import pySlipQt.log as log
log = log.Log('pyslipqt.log')

import pySlipQt.pySlipQt as pySlipQt
from display_text import DisplayText
from layer_control import LayerControl

######
# Various demo constants
######

# demo name/version
DemoVersion = '1.0'
DemoName = f'Test polyline placement {DemoVersion} (pySlipQt {pySlipQt.__version__})'

DemoHeight = 800
DemoWidth = 1000

# initial values
InitialViewLevel = 4
InitialViewPosition = (145.0, -20.0)

# tiles info
TileDirectory = 'test_polygon_placement_tiles'
MinTileLevel = 0

# the number of decimal places in a lon/lat display
LonLatPrecision = 2

# startup size of the application
DefaultAppSize = (1000, 700)

# general defaults
DefaultWidth = 5
DefaultColour = 'red'

# initial values in map-relative LayerControl
DefaultPlacement = 'ne'
DefaultX = 145.0
DefaultY = -20.0
DefaultOffsetX = 0
DefaultOffsetY = 0

# initial values in view-relative LayerControl
DefaultViewPlacement = 'ne'
DefaultViewX = 0
DefaultViewY = 0
DefaultViewOffsetX = 0
DefaultViewOffsetY = 0

# polyline map- and view-relative data
PolyPoints = [(140.0,-17.5), (144.0,-19.0), (142.5,-15.0), (147.5,-15.0),
              (146.0,-19.0), (150.0,-17.5), (150.0,-22.5), (146.0,-21.0),
              (147.5,-25.0), (142.5,-25.0), (144.0,-21.0), (140.0,-22.5)]

PolyViewPoints = [(-100,-50), (-20,-20), (-50,-100), (50,-100),
                  (20,-20), (100,-50), (100,50), (20,20),
                  (50,100), (-50,100), (-20,20), (-100,50)]

##################################
# Custom LayerControl widget.
#
# Constructor:
#
#     ppc = LayerControl('test title')
#
# Events:
#
#     .change   the contents were changed
#     .remove   the image should be removed
#
# The '.change' event has attached attributes holding the values from the
# widget, all checked so they are 'sane'.
##################################

class LayerControl(QWidget):
    """
    Custom LayerControl widget.

    Constructor:

        ipc = LayerControl('test title')

    Events:

        .change   the contents were changed
        .remove   the image should be removed

    The '.change' event has attached attributes holding the values from the
    widget, all checked so they are 'sane'.
    """

    # various sizes
    ButtonWidth = 40
    ButtonHeight = 40
    ComboboxWidth = 70

    # signals raised by this widget
    change = pyqtSignal(str, int, QColor, int, int)
    remove = pyqtSignal()

    # some stylesheets
    LabelStyle = 'QLabel { background-color : #f0f0f0; border: 1px solid gray; border-radius: 3px; }'
    GroupStyle = ('QGroupBox { background-color: rgb(230, 230, 230); }'
                  'QGroupBox::title { subcontrol-origin: margin; '
                                     'background-color: rgb(215, 215, 215); '
                                     'border-radius: 3px; '
                                     'padding: 2 2px; '
                                     'color: black; }')
    ButtonStyle = ('QPushButton {'
                                 'margin: 1px;'
                                 'border-color: #0c457e;'
                                 'border-style: outset;'
                                 'border-radius: 3px;'
                                 'border-width: 1px;'
                                 'color: black;'
                                 'background-color: white;'
                               '}')
    ButtonColourStyle = ('QPushButton {'
                                       'margin: 1px;'
                                       'border-color: #0c457e;'
                                       'border-style: outset;'
                                       'border-radius: 3px;'
                                       'border-width: 1px;'
                                       'color: black;'
                                       'background-color: %s;'
                                     '}')

    def __init__(self, title,
                 placement=DefaultPlacement, width=DefaultWidth,
                 colour=DefaultColour, offset_x=0, offset_y=0):
        """Initialise a LayerControl instance.

        title        text to show in static box outline around control
        placement    placement string for object
        width        width in pixels of the drawn polygon
        colour       sets the colour of the polygon outline
        offset_x     X offset of object
        offset_y     Y offset of object
        """

        super().__init__()

        # save parameters
        self.v_placement = placement
        self.v_width = width
        self.v_colour = colour
        self.v_offset_x = offset_x
        self.v_offset_y = offset_y

        # create subwidgets used in this custom widget
        self.placement = QComboBox()
        for p in ['none', 'nw', 'cn', 'ne', 'ce', 'se', 'cs', 'sw', 'cw', 'cc']:
            self.placement.addItem(p)
        self.placement.setCurrentIndex(9)

        self.line_width = QComboBox()
        for p in range(21):
            self.line_width.addItem(str(p))
        self.line_width.setCurrentIndex(3)
        self.line_width.setFixedWidth(LayerControl.ComboboxWidth)

        self.line_colour = QPushButton('')
        self.line_colour.setFixedWidth(LayerControl.ButtonWidth)
        self.line_colour.setStyleSheet(LayerControl.ButtonStyle)
        self.line_colour.setToolTip('Click here to change the point colour')

        self.x_offset = QComboBox()
        for p in range(0, 121, 10):
            self.x_offset.addItem(str(p - 60))
        self.x_offset.setCurrentIndex(6)
        self.x_offset.setFixedWidth(LayerControl.ComboboxWidth)

        self.y_offset = QComboBox()
        for p in range(0, 121, 10):
            self.y_offset.addItem(str(p - 60))
        self.y_offset.setCurrentIndex(6)
        self.y_offset.setFixedWidth(LayerControl.ComboboxWidth)

        btn_remove = QPushButton('Remove')
        btn_remove.resize(btn_remove.sizeHint())

        btn_update = QPushButton('Update')
        btn_update.resize(btn_update.sizeHint())

        # start the layout
        option_box = QGroupBox(title)
        option_box.setStyleSheet(LayerControl.GroupStyle)

        box_layout = QGridLayout()
        box_layout.setContentsMargins(2, 2, 2, 2)
        box_layout.setHorizontalSpacing(1)
        box_layout.setColumnStretch(0, 1)

        # start layout
        row = 1
        label = QLabel('placement: ')
        label.setAlignment(Qt.AlignRight)
        box_layout.addWidget(label, row, 0)
        box_layout.addWidget(self.placement, row, 1)
        label = QLabel('width: ')
        label.setAlignment(Qt.AlignRight)
        box_layout.addWidget(label, row, 2)
        box_layout.addWidget(self.line_width, row, 3)

        row += 1
        label = QLabel('colour: ')
        label.setAlignment(Qt.AlignRight)
        box_layout.addWidget(label, row, 0)
        box_layout.addWidget(self.line_colour, row, 1)

        row += 1
        label = QLabel('offset X: ')
        label.setAlignment(Qt.AlignRight)
        box_layout.addWidget(label, row, 0)
        box_layout.addWidget(self.x_offset, row, 1)
        label = QLabel('Y: ')
        label.setAlignment(Qt.AlignRight)
        box_layout.addWidget(label, row, 2)
        box_layout.addWidget(self.y_offset, row, 3)

        row += 1
        box_layout.addWidget(btn_remove, row, 1)
        box_layout.addWidget(btn_update, row, 3)

        option_box.setLayout(box_layout)

        layout = QHBoxLayout()
        layout.setContentsMargins(1, 1, 1, 1)
        layout.addWidget(option_box)

        self.setLayout(layout)

        # set size hints
        self.setMinimumSize(300, 200)
        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setSizePolicy(size_policy)

        # connect internal widget events to handlers
        self.line_colour.clicked.connect(self.changeLineColour)
        btn_remove.clicked.connect(self.removeImage)
        btn_update.clicked.connect(self.updateData)

    def changeLineColour(self, event):
        color = QColorDialog.getColor()
        if color.isValid():
            colour = color.name()
            # set colour button background
            self.line_colour.setStyleSheet(LayerControl.ButtonColourStyle % colour);
 
    def removeImage(self, event):
        self.remove.emit()

    def updateData(self, event):
        # get data from the widgets
        placement = str(self.placement.currentText())
        if placement == 'none':
            placement = None
        line_width = int(self.line_width.currentText())
        line_colour = self.line_colour.palette().color(1)
        x_offset = int(self.x_offset.currentText())
        y_offset = int(self.y_offset.currentText())

        print(f'updateData: placement={placement}, line_width={line_width}, x_offset={x_offset}, y_offset={y_offset}')
        
        self.change.emit(placement, line_width, line_colour, x_offset, y_offset)

################################################################################
# The main application frame
################################################################################

class TestPolyPlacement(QMainWindow):

    def __init__(self, tile_dir=TileDirectory):
        super().__init__()

        self.tile_directory = tile_dir
        self.tile_source = Tiles.Tiles()

        # variables for layer IDs
        self.poly_map_layer = None
        self.poly_view_layer = None

        # build the GUI
        grid = QGridLayout()
        grid.setColumnStretch(0, 1)
        grid.setContentsMargins(2, 2, 2, 2)

        qwidget = QWidget(self)
        qwidget.setLayout(grid)
        self.setCentralWidget(qwidget)

        # build the 'controls' part of GUI
        num_rows = self.make_gui(grid)

        self.pyslipqt = pySlipQt.PySlipQt(self, tile_src=self.tile_source,
                                          start_level=MinTileLevel)
        grid.addWidget(self.pyslipqt, 0, 0, num_rows + 1, 1)
        grid.setRowStretch(num_rows, 1)

        # set the size of the demo window, etc
        self.setGeometry(100, 100, DemoWidth, DemoHeight)
        self.setWindowTitle(DemoName)

        # set initial view position
#        self.map_level.set_text('%d' % InitViewLevel)

        # tie events from controls to handlers
        self.map_poly.remove.connect(self.remove_poly_map)
        self.map_poly.change.connect(self.change_poly_map)

        self.view_poly.remove.connect(self.remove_poly_view)
        self.view_poly.change.connect(self.change_poly_view)

        self.pyslipqt.events.EVT_PYSLIPQT_LEVEL.connect(self.handle_level_change)
        self.pyslipqt.events.EVT_PYSLIPQT_POSITION.connect(self.handle_position_event)

        self.map_level.set_text('0')

        self.show()

#####
# Build the GUI
#####

    def make_gui(self, grid):
        """Create application GUI."""

        """Build the controls in the right side of the grid."""

        # the 'grid_row' variable is row to add into
        grid_row = 0

        # put level and position into grid at top right
        self.map_level = DisplayText(title='', label='Level:',
                                     tooltip=None)
        grid.addWidget(self.map_level, grid_row, 1, 1, 1)
        self.mouse_position = DisplayText(title='',
                                          label='Lon/Lat:', text_width=100,
                                          tooltip='Shows the mouse longitude and latitude on the map',)
        grid.addWidget(self.mouse_position, grid_row, 2, 1, 1)
        grid_row += 1

        # now add the two point control widgets to right part of grid
        self.map_poly = LayerControl('Map-relative Polygon')
        grid.addWidget(self.map_poly, grid_row, 1, 1, 2)
        grid_row += 1

        self.view_poly = LayerControl('View-relative Polygon')
        grid.addWidget(self.view_poly, grid_row, 1, 1, 2)
        grid_row += 1

        return grid_row

    ######
    # event handlers
    ######

##### map-relative polygon layer

    def change_poly_map(self, placement, line_width, line_colour, x_off, y_off):
        """Display updated polygon."""

        print(f'change_poly_map: placement={placement}, line_width={line_width}, line_colour={line_colour}, x_off={x_off}, y_off={y_off}')

        if self.poly_map_layer:
            self.pyslipqt.DeleteLayer(self.poly_map_layer)

        poly_data = [(PolyPoints, {'placement': placement,
                                   'width': line_width,
                                   'colour': line_colour,
                                   'offset_x': x_off,
                                   'offset_y': y_off})]
        self.poly_map_layer = self.pyslipqt.AddPolylineLayer(poly_data, map_rel=True,
                                                             visible=True,
                                                             name='<poly_map_layer>')

    def remove_poly_map(self):
        """Delete the polygon map-relative layer."""

        if self.poly_map_layer:
            self.pyslipqt.DeleteLayer(self.poly_map_layer)
        self.poly_map_layer = None

##### view-relative polygon layer

    def change_poly_view(self, placement, line_width, line_colour, x_off, y_off):
        """Display updated view-relative polygon layer."""

        if self.poly_view_layer:
            self.pyslipqt.DeleteLayer(self.poly_view_layer)

        # create a new polygon layer
        poly_data = [(PolyViewPoints, {'placement': placement,
                                       'width': line_width,
                                       'colour': line_colour,
                                       'offset_x': x_off,
                                       'offset_y': y_off})]
        self.poly_view_layer = self.pyslipqt.AddPolylineLayer(poly_data,
                                                              map_rel=False,
                                                              visible=True,
                                                              name='<poly_view_layer>')

    def remove_poly_view(self):
        """Delete the polygon view-relative layer."""

        if self.poly_view_layer:
            self.pyslipqt.DeleteLayer(self.poly_view_layer)
        self.poly_view_layer = None

    def final_setup(self, level, position):
        """Perform final setup.

        level     zoom level required
        position  position to be in centre of view
        """

        self.pyslipqt.GotoLevelAndPosition(level, position)

    ######
    # Exception handlers
    ######

    def handle_position_event(self, event):
        """Handle a pySlipQt POSITION event."""

        posn_str = ''
        if event.mposn:
            (lon, lat) = event.mposn
            posn_str = ('%.*f / %.*f' % (LonLatPrecision, lon,
                                         LonLatPrecision, lat))

        self.mouse_position.set_text(posn_str)

    def handle_level_change(self, event):
        """Handle a pySlipQt LEVEL event."""

        self.map_level.set_text('%d' % event.level)

###############################################################################

# our own handler for uncaught exceptions
def excepthook(type, value, tb):
    msg = '\n' + '=' * 80
    msg += '\nUncaught exception:\n'
    msg += ''.join(traceback.format_exception(type, value, tb))
    msg += '=' * 80 + '\n'
    print(msg)
    log(msg)
    sys.exit(1)

# plug our handler into the python system
sys.excepthook = excepthook

def usage(msg=None):
    if msg:
        print(('*'*80 + '\n%s\n' + '*'*80) % msg)
    print(__doc__)

# decide which tiles to use, default is GMT
argv = sys.argv[1:]

try:
    (opts, args) = getopt.getopt(argv, 'dht:', ['debug', 'help', 'tiles='])
except getopt.error:
    usage()
    sys.exit(1)

tile_source = 'GMT'
debug = False
for (opt, param) in opts:
    if opt in ['-h', '--help']:
        usage()
        sys.exit(0)
    elif opt in ['-d', '--debug']:
        debug = True
    elif opt in ('-t', '--tiles'):
        tile_source = param
tile_source = tile_source.lower()

# set up the appropriate tile source
if tile_source == 'gmt':
    import pySlipQt.gmt_local as Tiles
elif tile_source == 'osm':
    import pySlipQt.open_street_map as Tiles
else:
    usage('Bad tile source: %s' % tile_source)
    sys.exit(3)

# start the PyQt5 app
log(DemoName)
tile_dir = 'test_polygon_placement'
app = QApplication(args)
ex = TestPolyPlacement(tile_dir)
sys.exit(app.exec_())

