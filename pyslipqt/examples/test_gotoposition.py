"""
Test PySlipQt GototPosition() function.

The idea is to have a set of buttons selecting various geo positions on the OSM
tile map.  When selected, the view would be moved with GotoPosition() and a
map-relative marker would be drawn at that position.  At the same time, a
view-relative marker would be drawn at the centre of the view.  The difference
between the two markers shows errors in the Geo2Tile() & Tile2GEO() functions.
"""


import os
import sys
import traceback

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QApplication, QMainWindow, QHBoxLayout)

#import pyslipqt.pyslipqt as pyslipqt
import pyslipqt
#import pyslipqt.osm_tiles as tiles
import osm_tiles as tiles

# If we have log.py, well and good.  Otherwise ...
try:
#    import pyslipqt.log as log
    import log
except ImportError:
    def logit(*args, **kwargs):
        pass
    log = logit
    log.debug = logit
    log.info = logit
    log.warn = logit
    log.error = logit
    log.critical = logit

#import pyslipqt.tkinter_error as tkinter_error
import tkinter_error


######
# Various demo constants
######

# demo name/version
DemoVersion = '1.0'
DemoName = "pySlip %s - GotoPosition() test %s" % (pyslipqt.__version__, DemoVersion)
DemoWidth = 800
DemoHeight = 665

# initial level and position
InitViewLevel = 3

# the number of decimal places in a lon/lat display
LonLatPrecision = 3

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
          ((98.3763357, 7.8605885), "Home"),
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

        hbox = QHBoxLayout()
        self.setLayout(hbox)

        # put map view in left of horizontal box
        sl_box = self.make_gui_view()
        all_display.Add(sl_box, proportion=1, border=1, flag=wx.EXPAND)

        # small spacer here - separate view and controls
        all_display.AddSpacer(HSpacerSize)

        # add controls to right of spacer
        controls = self.make_gui_controls(self)
        all_display.Add(controls, proportion=0, border=1)

        self.SetSizerAndFit(all_display)

    def make_gui_view(self):
        """Build the map view widget

        Returns the static box sizer.
        """

        # create gui objects
        sb = AppStaticBox(self, '')
#        tile_object = tiles.Tiles(self.tile_directory)
        self.pyslipqt = pyslipqt.PySlipQt(self, tile_src=self.tile_source)

        # lay out objects
        box = wx.StaticBoxSizer(sb, orient=wx.HORIZONTAL)
        box.Add(self.pyslipqt, proportion=1, border=1, flag=wx.EXPAND)

        return box

    def make_gui_controls(self):
        """Build the 'controls' part of the GUI

        Returns reference to containing sizer object.
        """

        # all controls in vertical box sizer
        controls = wx.BoxSizer(wx.VERTICAL)

        # add the map level in use widget
        level = self.make_gui_level(self)
        controls.Add(level, proportion=0, flag=wx.EXPAND|wx.ALL)

        # vertical spacer
        controls.AddSpacer(VSpacerSize)

        # add the mouse position feedback stuff
        mouse = self.make_gui_mouse(self)
        controls.Add(mouse, proportion=0, flag=wx.EXPAND|wx.ALL)

        # buttons for each point of interest
        self.buttons = {}
        for (num, city) in enumerate(Cities):
            controls.AddSpacer(VSpacerSize)
            (lonlat, name) = city
            btn = wx.Button(self, num, name)
            controls.Add(btn, proportion=0, flag=wx.EXPAND|wx.ALL)
            btn.Bind(wx.EVT_BUTTON, self.handle_button)
            self.buttons[num] = city
        return controls

    def make_gui_level(self):
        """Build the control that shows the level.

        Returns reference to containing sizer object.
        """

        # create objects
        txt = wx.StaticText(self, wx.ID_ANY, 'Level: ')
        self.map_level = wx.StaticText(self, wx.ID_ANY, ' ')

        # lay out the controls
        sb = AppStaticBox(self, 'Map level')
        box = wx.StaticBoxSizer(sb, orient=wx.HORIZONTAL)
        box.Add(txt, border=PackBorder, flag=(wx.ALIGN_CENTER_VERTICAL
                                     |wx.ALIGN_RIGHT|wx.LEFT))
        box.Add(self.map_level, proportion=0, border=PackBorder,
                flag=wx.RIGHT|wx.TOP)

        return box

    def make_gui_mouse(self):
        """Build the mouse part of the controls part of GUI.

        Returns reference to containing sizer object.
        """

        # create objects
        txt = wx.StaticText(self, wx.ID_ANY, 'Lon/Lat: ')
        self.mouse_position = ROTextCtrl(self, '', size=(150,-1),
                                         tooltip=('Shows the mouse '
                                                  'longitude and latitude '
                                                  'on the map'))

        # lay out the controls
        sb = AppStaticBox(self, 'Mouse position')
        box = wx.StaticBoxSizer(sb, orient=wx.HORIZONTAL)
        box.Add(txt, border=PackBorder, flag=(wx.ALIGN_CENTER_VERTICAL
                                     |wx.ALIGN_RIGHT|wx.LEFT))
        box.Add(self.mouse_position, proportion=1, border=PackBorder,
                    flag=wx.RIGHT|wx.TOP|wx.BOTTOM)

        return box

    ######
    # Exception handlers
    ######

    def handle_button(self, event):
        """Handle button event."""

        (posn, name) = self.buttons[event.Id]
        self.pyslipqt.GotoPosition(posn)

        if self.map_layer:
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
                                                        name='view_layer')

    def handle_position_event(self, event):
        """Handle a pySlip POSITION event."""

        posn_str = ''
        if event.mposn:
            (lon, lat) = event.mposn
            posn_str = ('%.*f / %.*f'
                        % (LonLatPrecision, lon, LonLatPrecision, lat))

        self.mouse_position.SetValue(posn_str)

    def handle_level_change(self, event):
        """Handle a pySlip LEVEL event."""

        self.map_level.SetLabel('%d' % event.level)


################################################################################

# our own handler for uncaught exceptions
def excepthook(type, value, tb):
    msg = '\n' + '=' * 80
    msg += '\nUncaught exception:\n'
    msg += ''.join(traceback.format_exception(type, value, tb))
    msg += '=' * 80 + '\n'
    log(msg)
    tkinter_error.tkinter_error(msg)
    sys.exit(1)

# use user tile directory, if supplied
tile_dir = None
if len(sys.argv) > 1:
    tile_dir = sys.argv[1]

# plug our handler into the python system
sys.excepthook = excepthook

app = QApplication(sys.argv)
ex = AppFrame()
sys.exit(app.exec_())
