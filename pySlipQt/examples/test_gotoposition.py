"""
Test PySlipQt GototPosition() function.

The idea is to have a set of buttons selecting various geo positions on the OSM
tile map.  When selected, the view would be moved with GotoPosition() and a
map-relative marker would be drawn at that position.  At the same time, a
view-relative marker would be drawn at the centre of the view.  The difference
between the two markers shows errors in the Geo2Tile() & Tile2Geo() functions.

"""


import os
import sys
import traceback

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget,
                             QHBoxLayout, QGridLayout,
                             QPushButton)

import pySlipQt.pySlipQt as pySlipQt
import pySlipQt.open_street_map as tiles
from display_text import DisplayText
from layer_control import LayerControl

# set up logging
import pySlipQt.log as log
log = log.Log('pyslipqt.log')


######
# Various demo constants
######

# demo name/version
DemoVersion = '1.0'
DemoName = "pySlip %s - GotoPosition() test %s" % (pySlipQt.__version__, DemoVersion)
DemoWidth = 800
DemoHeight = 665

# initial level and position
InitViewLevel = 3
InitViewPosition = (0, 0)

# the number of decimal places in a lon/lat display
LonLatPrecision = 2

# a selection of cities, position from WikiPedia, etc
# format is ((<lon>,<lat>),<name>)
# lat+lon from Google Maps
Cities = [((0.0, 51.4778), 'Greenwich, United Kingdom'),
          ((5.33, 60.389444), 'Bergen, Norway'),
          ((151.209444, -33.865), 'Sydney, Australia'),
          ((-77.036667, 38.895111), 'Washington DC, USA'),
          ((132.472638, 34.395359), 'Hiroshima (広島市), Japan'),
          ((-8.008273, 31.632488), 'Marrakech (مراكش), Morocco'),
          ((18.955321, 69.649208), 'Tromsø, Norway'),
          ((-70.917058, -53.163863), 'Punta Arenas, Chile'),
          ((168.347217, -46.413020), 'Invercargill, New Zealand'),
          ((-147.8094268, 64.8282982), 'Fairbanks AK, USA'),
          ((103.8508548, 1.2848402), "Singapore (One Raffles Place)"),
          ((-3.2056135, 55.9552474), "Maxwell's Birthplace"),
          ((7.6059011, 50.3644454), "Deutsches Eck, Koblenz, Germany"),
          ((116.391667, 39.903333), "Beijing (北京市)"),
         ]


################################################################################
# The main application frame
################################################################################

class AppFrame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(300, 300, DemoWidth, DemoHeight)
        self.setWindowTitle(DemoName)
        self.show()

        self.tile_source = tiles.Tiles()
        self.tile_directory = self.tile_source.tiles_dir

        # the data objects for map and view layers
        self.map_layer = None
        self.view_layer = None

        # build the GUI
        self.make_gui()

        self.show()

        # bind events to handlers
        self.pyslipqt.events.EVT_PYSLIPQT_POSITION.connect(self.handle_position_event)
        self.pyslipqt.events.EVT_PYSLIPQT_LEVEL.connect(self.handle_level_change)

        # finally, goto desired level and position
        self.pyslipqt.GotoLevelAndPosition(InitViewLevel, InitViewPosition)

#####
# Build the GUI
#####

    def make_gui(self):
        """Create application GUI."""

        # build the GUI
        grid = QGridLayout()

        qwidget = QWidget(self)
        qwidget.setLayout(grid)
        self.setCentralWidget(qwidget)

        # add controls to right of spacer
        rows = self.make_gui_controls(grid)
#        grid.addLayout(controls)

        # put map view in left of horizontal box
        self.pyslipqt = pySlipQt.PySlipQt(self, start_level=InitViewLevel, tile_src=self.tile_source)
        grid.addWidget(self.pyslipqt, 0, 0, rows+1, 1)

    def make_gui_controls(self, grid):
        """Build the 'controls' part of the GUI

        grid  reference to the grid layout to fill
        Returns reference to containing sizer object.
        """

        # row to put controls into
        row = 0

        # add the map level in use widget
        level_mouse = self.make_gui_level_mouse()
        grid.addLayout(level_mouse, row, 1)
        row += 1

        # buttons for each point of interest
        self.buttons = {}
        for (num, city) in enumerate(Cities):
            (lonlat, name) = city
            btn = QPushButton(name)
            grid.addWidget(btn, row, 1)
            btn.clicked.connect(self.handle_button)
            self.buttons[btn] = city
            row += 1

        return row

    def make_gui_level_mouse(self):
        """Build the control that shows the level and mouse position.

        Returns reference to containing layout.
        """

        hbox = QHBoxLayout()
        self.map_level = DisplayText(title='', label='Level:', tooltip=None)
        self.mouse_position = DisplayText(title='', label='Lon/Lat:',
                                          text_width=100, tooltip=None)
        hbox.addWidget(self.map_level)
        hbox.addWidget(self.mouse_position)

        return hbox

    ######
    # Exception handlers
    ######

    def handle_button(self, event):
        """Handle button event."""

        # get the button that was pressed
        sender_btn = self.sender()
        (posn, name) = self.buttons[sender_btn]
        log(f"Got button event, posn={posn}, name='{name}'")

        self.pyslipqt.GotoPosition(posn)

        if self.map_layer:
            # if there was a previous layer, delete it
            self.pyslipqt.DeleteLayer(self.map_layer)
        map_data = [posn]
        point_colour = '#0000ff40'
        self.map_layer = self.pyslipqt.AddPointLayer(map_data, map_rel=True,
                                                     placement='cc',
                                                     color=point_colour,
                                                     radius=11,
                                                     visible=True,
                                                     name='map_layer')

        if self.view_layer:
            self.pyslipqt.DeleteLayer(self.view_layer)
        view_data = [(((0,0),(0,-10),(0,0),(0,10),
            (0,0),(-10,0),(0,0),(10,0)),{'colour':'#ff0000ff'},)]
#        poly_colour = '#ff0000ff'
        self.view_layer = self.pyslipqt.AddPolygonLayer(view_data, map_rel=False,
                                                        placement='cc',
#                                                        colour=poly_colour,
                                                        closed=False,
                                                        visible=True,
                                                        width=2,
                                                        name='view_layer')

    def handle_position_event(self, event):
        """Handle a pySlip POSITION event."""

        posn_str = ''
        if event.mposn:
            (lon, lat) = event.mposn
            posn_str = ('%.*f / %.*f'
                        % (LonLatPrecision, lon, LonLatPrecision, lat))

        self.mouse_position.set_text(posn_str)

    def handle_level_change(self, event):
        """Handle a pySlip LEVEL event."""

        self.map_level.set_text('%d' % event.level)


################################################################################

# our own handler for uncaught exceptions
def excepthook(type, value, tb):
    msg = '\n' + '=' * 80
    msg += '\nUncaught exception:\n'
    msg += ''.join(traceback.format_exception(type, value, tb))
    msg += '=' * 80 + '\n'
    print(msg)
    sys.exit(1)

# plug our handler into the python system
sys.excepthook = excepthook

# use user tile directory, if supplied
tile_dir = None
if len(sys.argv) > 1:
    tile_dir = sys.argv[1]

app = QApplication(sys.argv)
ex = AppFrame()
sys.exit(app.exec_())
