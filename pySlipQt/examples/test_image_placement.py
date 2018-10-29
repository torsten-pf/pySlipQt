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
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget,
                             QVBoxLayout, QHBoxLayout)

import pySlipQt.pySlipQt as pySlipQt
import pySlipQt.log as log

from display_text import DisplayText
from layer_control import LayerControl
from image_placement import ImagePlacementControl

#from tkinter_error import tkinter_error

# initialize the logging system
log = log.Log('test_image_placement.log')

######
# Various demo constants
######

# demo name/version
DemoVersion = '1.0'
DemoName = 'Test image placement %s (pySlipQt %s)' % (DemoVersion, pySlipQt.__version__)

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



################################################################################
# The main application window.
################################################################################

class TestImagePlacement(QMainWindow):

    def __init__(self, tile_dir=TileDirectory):
        super().__init__()

        self.tile_directory = tile_dir
        self.tile_source = Tiles.Tiles()

        # variables for layer IDs
        self.image_map_layer = None
        self.image_view_layer = None

        # build the GUI
        outer_hbox = QHBoxLayout()

        # build the right part of ther display
        vbox = QVBoxLayout()

        # add the map level and mouse position parts to right VBox
        hbox = QHBoxLayout()
        self.map_level = DisplayText(title='Map level', label='Level:',
                                     tooltip=None)
        hbox.addWidget(self.map_level)
        hbox.addStretch(1)
        self.mouse_position = DisplayText(title='Cursor position',
                                          label='Lon/Lat:', text_width=100,
                                          tooltip='Shows the mouse longitude and latitude on the map',)
        hbox.addWidget(self.mouse_position)
        vbox.addLayout(hbox)

        # now add the two image control widgets to right VBox
        self.map_image = ImagePlacementControl('Map-relative Image')
        vbox.addWidget(self.map_image)
        self.view_image = ImagePlacementControl('View-relative Image')
        vbox.addWidget(self.view_image)
        vbox.addStretch(1)

        # add the map widget to the overall HBox
        self.pyslipqt = pySlipQt.PySlipQt(self, tile_src=self.tile_source,
                                          start_level=MinTileLevel)
        outer_hbox.addWidget(self.pyslipqt)

        # add the right VBox to overall HBox
        outer_hbox.addLayout(vbox)

        # create a widget, use outer_hbox layout above and make it replace the main window
        qwidget = QWidget(self)
        qwidget.setLayout(outer_hbox)
        self.setCentralWidget(qwidget)

        # set the size of the demo window, etc
        self.setGeometry(100, 100, DemoWidth, DemoHeight)
        self.setWindowTitle(DemoName)

        # set initial view position
#        self.map_level.set_text('%d' % InitViewLevel)

        # tie events from controls to handlers
        self.map_image.remove.connect(self.remove_image_map)
        self.map_image.change.connect(self.change_image_map)

        self.view_image.remove.connect(self.remove_image_view)
        self.view_image.change.connect(self.change_image_view)

        self.pyslipqt.events.EVT_PYSLIPQT_LEVEL.connect(self.handle_level_change)
        self.pyslipqt.events.EVT_PYSLIPQT_POSITION.connect(self.handle_position_event)


        # set initial view position
#        QTimer.singleShot(1, self.final_setup)

        self.show()

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

##### map-relative image layer

    def change_image_map(self, image, placement, radius, colour,
                           x, y, off_x, off_y):
        """Display updated image."""

        # remove any previous layer
        if self.image_map_layer:
            self.remove_image_map()

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
        self.image_map_layer = None

##### view-relative image layer

    def change_image_view(self, image, placement, radius, colour,
                           x, y, off_x, off_y):
        """Display updated image."""

        if self.image_view_layer:
            self.remove_image_view()

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
app = QApplication(args)
ex = TestImagePlacement(tile_dir)
sys.exit(app.exec_())
