"""
Program to test text map-relative and view-relative placement.
Select which to show and experiment with placement parameters.

Usage: test_text_placement.py [-h|--help] [-d] [(-t|--tiles) (GMT|OSM)]
"""


import os
import sys
import getopt
import traceback

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget,
                             QGridLayout, QVBoxLayout, QHBoxLayout)

# initialize the logging system
import pySlipQt.log as log
log = log.Log('pyslipqt.log')

import pySlipQt.pySlipQt as pySlipQt
from display_text import DisplayText
from layer_control import LayerControl
from text_placement import TextPlacementControl

######
# Various demo constants
######

# demo name/version
DemoVersion = '1.0'
DemoName = 'Test text placement %s (pySlipQt %s)' % (DemoVersion, pySlipQt.__version__)

DemoHeight = 800
DemoWidth = 1000

# initial values
#InitialViewLevel = 4
InitialViewLevel = 0
InitialViewPosition = (145.0, -20.0)

# tiles info
TileDirectory = 'test_tiles'
MinTileLevel = 0

# the number of decimal places in a lon/lat display
LonLatPrecision = 2

# startup size of the application
DefaultAppSize = (1000, 700)

################################################################################
# The main application window.
################################################################################

class TestTextPlacement(QMainWindow):

    def __init__(self, tile_dir=TileDirectory):
        super().__init__()

        self.tile_directory = tile_dir
        self.tile_source = Tiles.Tiles()

        # variables for layer IDs
        self.text_map_layer = None
        self.text_view_layer = None

        # build the GUI
        grid = QGridLayout()
        grid.setColumnStretch(0, 1)
        grid.setContentsMargins(2, 2, 2, 2)

        qwidget = QWidget(self)
        qwidget.setLayout(grid)
        self.setCentralWidget(qwidget)

        # build the 'controls' part of GUI
        num_rows = self.make_gui_controls(grid)

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
        self.map_text.remove.connect(self.remove_text_map)
        self.map_text.change.connect(self.change_text_map)

        self.view_text.remove.connect(self.remove_text_view)
        self.view_text.change.connect(self.change_text_view)

        self.pyslipqt.events.EVT_PYSLIPQT_LEVEL.connect(self.handle_level_change)
        self.pyslipqt.events.EVT_PYSLIPQT_POSITION.connect(self.handle_position_event)

        # set initial view position
#        QTimer.singleShot(1, self.final_setup)
        self.map_level.set_text('0')

        self.show()

    def make_gui_controls(self, grid):
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

        # now add the two text control widgets to right part of grid
        self.map_text = TextPlacementControl('Map-relative Text')
        self.map_text.setToolTip('Position text on the map')
        grid.addWidget(self.map_text, grid_row, 1, 1, 2)
        grid_row += 1

        self.view_text = TextPlacementControl('View-relative Text')
        self.view_text.setToolTip('Position text on the view')
        grid.addWidget(self.view_text, grid_row, 1, 1, 2)
        grid_row += 1

        return grid_row

    def final_setup(self):
        """Perform final setup.

        We do this in a OneShot() function for those operations that
        must not be done while the GUI is "fluid".
        """

        pass
#        self.pyslipqt.GotoLevelAndPosition(InitViewLevel, InitViewPosition)


    ######
    # event handlers
    ######

##### map-relative text layer

    def change_text_map(self, text, textcolour, placement, radius, colour,
                           x, y, off_x, off_y):
        """Display updated text."""

        # remove any previous layer
        if self.text_map_layer:
            self.remove_text_map()

        # create the new layer
        attribs = {'radius': radius,
                   'colour': colour,
                   'textcolour': textcolour,
                   'offset_x': off_x,
                   'offset_y': off_y}
        if placement != 'none':
            attribs['placement'] = placement
        text_data = [(x, y, text, attribs)]
        self.text_map_layer = self.pyslipqt.AddTextLayer(text_data,
                                                         map_rel=True,
                                                         visible=True,
                                                         name='<map_text>')

    def remove_text_map(self):
        """Delete the text map-relative layer."""

        if self.text_map_layer:
            self.pyslipqt.DeleteLayer(self.text_map_layer)
        self.text_map_layer = None

##### view-relative text layer

    def change_text_view(self, text, textcolour, placement, radius, colour,
                           x, y, off_x, off_y):
        """Display updated text."""

        if self.text_view_layer:
            self.remove_text_view()

        print(f"change_text_view: placement='{placement}'")

        # create a new text layer
        attribs = {'radius': radius,
                   'colour': colour,
                   'textcolour': textcolour,
                   'offset_x': off_x,
                   'offset_y': off_y}
        if placement != 'none':
            attribs['placement'] = placement
        print(f"change_text_view: attribs={attribs}")
        text_data = [(x, y, text, attribs)]
        self.text_view_layer = self.pyslipqt.AddTextLayer(text_data,
                                                          map_rel=False,
                                                          visible=True,
                                                          name='<view_text>')

    def remove_text_view(self):
        """Delete the text view-relative layer."""

        if self.text_view_layer:
            self.pyslipqt.DeleteLayer(self.text_view_layer)
        self.text_view_layer = None

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
    log(msg)
    print(msg)
#    tkinter_error.tkinter_error(msg)
    sys.exit(1)

def usage(msg=None):
    if msg:
        print(('*'*80 + '\n%s\n' + '*'*80) % msg)
    print(__doc__)


# plug our handler into the python system
sys.excepthook = excepthook

# analyse the command line args
argv = sys.argv[1:]

try:
    (opts, args) = getopt.getopt(argv, 'dht:', ['debug', 'help', 'tiles='])
except getopt.error:
    usage()
    sys.exit(1)

tile_dir = 'test_tiles'
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

import pySlipQt.gmt_local as Tiles
## set up the appropriate tile source
#if tile_source == 'gmt':
#    print('importing pySlipQt.gmt_local')
#    import pySlipQt.gmt_local as Tiles
#elif tile_source == 'osm':
#    print('importing pySlipQt.open_street_map')
#    import pySlipQt.open_street_map as Tiles
#else:
#    usage('Bad tile source: %s' % tile_source)
#    sys.exit(3)

# start the app
log(DemoName)
app = QApplication(args)
ex = TestTextPlacement(tile_dir)
sys.exit(app.exec_())
