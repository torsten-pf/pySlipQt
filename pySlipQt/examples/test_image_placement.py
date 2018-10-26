"""
Program to test image map-relative and view-relative placement.
Select which to show and experiment with placement parameters.

Usage: test_image_placement.py [-h|--help] [-d] [(-t|--tiles) (GMT|OSM)]
"""


import os
import sys
import getopt
import traceback

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QAction, QGridLayout, QErrorMessage, QGroupBox)

import pySlipQt.pySlipQt as pySlipQt
import pySlipQt.log as log

from display_text import DisplayText
from layer_control import LayerControl
from image_placement_control import ImagePlacementControl

#from tkinter_error import tkinter_error

# initialize the logging system
log = log.Log("pyslipqt.log")

######
# Various demo constants
######

# demo name/version
DemoName = 'Test image placement, pySlipQt %s' % pySlipQt.__version__
DemoVersion = '1.0'

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
LonLatPrecision = 3

# startup size of the application
DefaultAppSize = (1000, 700)

# initial values in map-relative LayerControl
DefaultFilename = 'graphics/shipwreck.png'
DefaultPlacement = 'ne'
DefaultPointColour = 'red'
DefaultPointRadius = 3
DefaultX = 145.0
DefaultY = -20.0
DefaultOffsetX = 0
DefaultOffsetY = 0

# initial values in view-relative LayerControl
DefaultViewFilename = 'graphics/compass_rose.png'
DefaultViewPlacement = 'ne'
DefaultPointColour = 'red'
DefaultPointRadius = 0
DefaultViewX = 0
DefaultViewY = 0
DefaultViewOffsetX = 0
DefaultViewOffsetY = 0



import os
import sys
import platform

from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QLabel, QComboBox, QPushButton, QLineEdit
from PyQt5.QtWidgets import QGridLayout, QFileDialog, QColorDialog
from PyQt5.QtGui import QColor

from image_placement_control import ImagePlacementControl


################################################################################
# The main application window.
################################################################################

class TestImagePlacement(QMainWindow):

    def __init__(self, tile_dir=TileDirectory):
        super().__init__()

        print('Start of __init__()')

        self.tile_directory = tile_dir
        self.tile_source = Tiles.Tiles()

        # variables for layer IDs
        self.image_map_layer = None
        self.image_view_layer = None
        print('point 1')

        # build the GUI
        grid = QGridLayout()
        grid.setColumnStretch(0, 1)
        grid.setContentsMargins(2, 2, 2, 2)
        print('point 2')

        qwidget = QWidget(self)
        qwidget.setLayout(grid)
        self.setCentralWidget(qwidget)
        print('point 3')

        # build the 'controls' part of GUI
        num_rows = self.make_gui_controls(grid)
        print('point 4')

        self.pyslipqt = pySlipQt.PySlipQt(self, tile_src=self.tile_source,
                                          start_level=MinTileLevel)
        grid.addWidget(self.pyslipqt, 0, 0, num_rows, 1)
        print('point 5')

        # set the size of the demo window, etc
        self.setGeometry(100, 100, DemoWidth, DemoHeight)
        self.setWindowTitle('%s %s' % (DemoName, DemoVersion))
        print('point 6')

        # set initial view position
#        self.map_level.set_text('%d' % InitViewLevel)
        print('point 7')

        # tie events from controls to handlers
        self.map_image.remove.connect(self.remove_image_map)
        self.map_image.change.connect(self.change_image_map)

        self.view_image.remove.connect(self.remove_image_view)
        self.view_image.change.connect(self.change_image_view)
        print('point 8')

        # set initial view position
        QTimer.singleShot(1, self.final_setup)
        print('point 9')

        self.show()
        print('point 10')

    def make_gui_controls(self, grid):
        """Build the 'controls' part of the GUI

        grid  reference to grid that we populate

        Returns the number of rows added to the 'grid' layout.
        """

        # the 'grid_row' variable is row to add into
        grid_row = 0

        # put level and position into grid at top right
        self.map_level = DisplayText(title='Map level', label='Level:',
                                     tooltip=None)
        grid.addWidget(self.map_level, grid_row, 1, 1, 1)
        self.mouse_position = DisplayText(title='Cursor position',
                                          label='Lon/Lat:', text_width=100,
                                          tooltip='Shows the mouse longitude and latitude on the map',)
        grid.addWidget(self.mouse_position, grid_row, 2, 1, 1)
        grid_row += 1


        # conrol for map-relative placement
        self.map_image = ImagePlacementControl('Map-relative image placement')
        grid.addWidget(self.map_image, grid_row, 1, 1, 3)
        grid_row += 1

        # controls for view-relative placement
        self.view_image = ImagePlacementControl('View-relative image placement')
        grid.addWidget(self.view_image, grid_row, 1, 1, 3)
        grid_row += 1

        return grid_row

    def final_setup(self):
        """Perform final setup.

        We do this in a OneShot() function for those operations that
        must not be done while the GUI is "fluid".
        """

        self.pyslipqt.GotoLevelAndPosition(InitViewLevel, InitViewPosition)


    ######
    # event handlers
    ######

##### map-relative image layer

    def change_image_map(self, filepath, placement, radius, colour,
                           x, y, offset_x, offset_y):
        print(f'change_image: filepath={filepath}, placement={placement}, '
              f'radius={radius}, colour={colour}, x={x}, y={y}, '
              f'offset_x={offset_x}, offset_y={offset_y}')

    def change_image_mapX(self, image, placement, radius, colour,
                           x, y, off_x, off_y):
        """Display updated image."""

        # remove any previous layer
        if self.image_map_layer:
            self.pyslipqt.DeleteLayer(self.image_map_layer)

        # create the new layer
        image_data = [(x, y, image, {'placement': placement,
                                     'radius': radius,
                                     'colour': colour,
                                     'offset_x': off_x,
                                     'offset_y': off_y})]
        self.image_map_layer = self.pyslipqt.AddImageLayer(image_data,
                                                           map_rel=True,
                                                           visible=True,
                                                           name='<image_layer>')

    def remove_image_map(self):
        """Delete the image map-relative layer."""

        if self.image_map_layer:
            self.pyslipqt.DeleteLayer(self.image_map_layer)
        self.image_layer = None

##### view-relative image layer

    def change_image_view(self, image, placement, radius, colour,
                           x, y, off_x, off_y):
        """Display updated image."""

        if self.image_view_layer:
            self.pyslip.DeleteLayer(self.image_view_layer)

        # create a new image layer
        image_data = [(x, y, image, {'placement': placement,
                                     'radius': radius,
                                     'colour': colour,
                                     'offset_x': off_x,
                                     'offset_y': off_y})]
        self.image_view_layer = self.pyslipqt.AddImageLayer(image_data,
                                                            map_rel=False,
                                                            visible=True,
                                                            name='<image_layer>')

    def remove_image_view(self):
        """Delete the image view-relative layer."""

        if self.image_view_layer:
            self.pyslipqt.DeleteLayer(self.image_view_layer)
        self.image_view_layer = None

    def final_setup(self, level, position):
        """Perform final setup.

        level     zoom level required
        position  position to be in centre of view

        We do this in a CallAfter() function for those operations that
        must not be done while the GUI is "fluid".
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

        self.mouse_position.SetValue(posn_str)

    def handle_level_change(self, event):
        """Handle a pySlipQt LEVEL event."""

        self.map_level.SetLabel('%d' % event.level)

###############################################################################

# our own handler for uncaught exceptions
def excepthook(type, value, tb):
    msg = '\n' + '=' * 80
    msg += '\nUncaught exception:\n'
    msg += ''.join(traceback.format_exception(type, value, tb))
    msg += '=' * 80 + '\n'
    log(msg)
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

# set up the appropriate tile source
if tile_source == 'gmt':
    import pySlipQt.gmt_local as Tiles
elif tile_source == 'osm':
    import pySlipQt.open_street_map as Tiles
else:
    usage('Bad tile source: %s' % tile_source)
    sys.exit(3)

# start the app
app = QApplication(args)
ex = TestImagePlacement(tile_dir)
sys.exit(app.exec_())
