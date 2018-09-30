#!/usr/bin/env python3

"""
pySlipQt demonstration program with user-selectable tiles.

Usage: pyslipqt_demo.py <options>

where <options> is zero or more of:
    -d|--debug <level>
        where <level> is either a numeric debug level in the range [0, 50] or
        one of the symbolic debug level names:
            NOTSET    0     nothing is logged (default)
            DEBUG    10     everything is logged
            INFO     20     less than DEBUG, informational debugging
            WARNING  30     less than INFO, only non-fatal warnings
            ERROR    40     less than WARNING
            CRITICAL 50     less than ERROR
    -h|--help
        prints this help and stops
"""


import os
import sys
import copy
from tkinter_error import tkinter_error
try:
    import pyslipqt
except ImportError:
    print('*'*60 + '\nSorry, you must install pySlipQt first\n' + '*'*60)
    raise
try:
    import PyQt5
except ImportError:
    msg = 'Sorry, you must install PyQt5'
    print(msg)
    tkinter_error(msg)
    sys.exit(1)

#from PyQt5.QtWidgets import (QLabel, QLineEdit)
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel,
                             QSpinBox, QVBoxLayout, QVBoxLayout, QAction,
                             QHBoxLayout, QVBoxLayout, QGridLayout,
                             QErrorMessage)

import log
import gmt_local_tiles as tiles
from display_text import DisplayText
from layer_control import LayerControl

log = log.Log("pyslipqt.log")

######
# Various demo constants
######

# demo name/version
DemoName = 'pySlipQt %s - Demonstration' % pyslipqt.__version__
DemoVersion = '1.0'

DemoWidth = 800
DemoHeight = 600

# tiles info
MinTileLevel = 0

# initial view level and position
InitViewLevel = 0

# this will eventually be selectable within the app
# a selection of cities, position from WikiPedia, etc
InitViewPosition = (0.0, 51.48)             # Greenwich, England
#InitViewPosition = (5.33, 60.389444)        # Bergen, Norway
#InitViewPosition = (153.033333, -27.466667) # Brisbane, Australia
#InitViewPosition = (98.3786761, 7.8627326)  # Phuket (ภูเก็ต), Thailand
#InitViewPosition = (151.209444, -33.859972) # Sydney, Australia
#InitViewPosition = (-77.036667, 38.895111)  # Washington, DC, USA
#InitViewPosition = (132.455278, 34.385278)  # Hiroshima, Japan
#InitViewPosition = (-8.008889, 31.63)       # Marrakech (مراكش), Morocco
#InitViewPosition = (18.95, 69.65)           # Tromsø, Norway
#InitViewPosition = (-70.933333, -53.166667) # Punta Arenas, Chile
#InitViewPosition = (168.3475, -46.413056)   # Invercargill, New Zealand
#InitViewPosition = (-147.723056, 64.843611) # Fairbanks, AK, USA
#InitViewPosition = (103.851959, 1.290270)   # Singapore

# levels on which various layers show
MRPointShowLevels = [3, 4]
MRImageShowLevels = [3, 4]
MRTextShowLevels = None #[3, 4]
MRPolyShowLevels = [3, 4]
MRPolylineShowLevels = [3, 4]

# the number of decimal places in a lon/lat display
LonLatPrecision = 3

# startup size of the application
DefaultAppSize = (1100, 770)

# default deltas for various layer types
DefaultPointMapDelta = 40
DefaultPointViewDelta = 40
DefaultImageMapDelta = 40
DefaultImageViewDelta = 40
DefaultTextMapDelta = 40
DefaultTextViewDelta = 40
DefaultPolygonMapDelta = 40
DefaultPolygonViewDelta = 40
DefaultPolylineMapDelta = 40
DefaultPolylineViewDelta = 40

# image used for shipwrecks, glassy buttons, etc
ShipImg = 'examples/graphics/shipwreck.png'

GlassyImg2 = 'examples/graphics/glassy_button_2.png'
SelGlassyImg2 = 'examples/graphics/selected_glassy_button_2.png'
GlassyImg3 = 'examples/graphics/glassy_button_3.png'
SelGlassyImg3 = 'examples/graphics/selected_glassy_button_3.png'
GlassyImg4 = 'examples/graphics/glassy_button_4.png'
SelGlassyImg4 = 'examples/graphics/selected_glassy_button_4.png'
GlassyImg5 = 'examples/graphics/glassy_button_5.png'
SelGlassyImg5 = 'examples/graphics/selected_glassy_button_5.png'
GlassyImg6 = 'examples/graphics/glassy_button_6.png'
SelGlassyImg6 = 'examples/graphics/selected_glassy_button_6.png'

# image used for shipwrecks
CompassRoseGraphic = 'examples/graphics/compass_rose.png'

# logging levels, symbolic to numeric mapping
LogSym2Num = {'CRITICAL': 50,
              'ERROR': 40,
              'WARNING': 30,
              'INFO': 20,
              'DEBUG': 10,
              'NOTSET': 0}

# list of modules containing tile sources
# list of (<long_name>, <module_name>)
# the <long_name>s go into the Tileselect menu
TileSources = [
               ('BlueMarble tiles', 'pyslipqt.bm_tiles'),
               ('GMT tiles', 'pyslipqt.gmt_local_tiles'),
               ('ModestMaps tiles', 'pyslipqt.mm_tiles'),
               ('MapQuest tiles', 'pyslipqt.mq_tiles'),
               ('OpenStreetMap tiles', 'pyslipqt.osm_tiles'),
               ('Stamen Toner tiles', 'pyslipqt.stmt_tiles'),
               ('Stamen Transport tiles', 'pyslipqt.stmtr_tiles'),
               ('Stamen Watercolor tiles', 'pyslipqt.stmw_tiles'),
              ]
DefaultTileset = 'GMT tiles'


######
# Various GUI layout constants
######

# border width when packing GUI elements
PackBorder = 0


###############################################################################
# The main application frame
###############################################################################

class PySlipQtDemo(QWidget):
    def __init__(self):
        super().__init__()

#        #exitAct = QAction(QIcon('exit.png'), '&Exit', self)
#        exitAct = QAction('&Exit', self)
#        exitAct.setShortcut('Ctrl+Q')
#        exitAct.setStatusTip('Exit application')
#        exitAct.triggered.connect(qApp.quit)

#        menubar = self.menuBar()
#        fileMenu = menubar.addMenu('&File')
#        fileMenu.addAction(exitAct)

        self.tile_source = tiles.Tiles()

        # build the GUI
        grid = QGridLayout()
        self.setLayout(grid)

        grid.setColumnStretch(0, 1)
#        grid.setColumnStretch(1, 0)
#        grid.setColumnStretch(2, 0)
        grid.setContentsMargins(2, 2, 2, 2)

        # build the 'controls' part of GUI
        num_rows = self.make_gui_controls(grid)

        self.pyslipqt = pyslipqt.PySlipQt(self, tile_src=self.tile_source, start_level=0)
        grid.addWidget(self.pyslipqt, 0, 0, num_rows, 1)

        # do initialisation stuff - all the application stuff
        self.init()

        # create select event dispatch directory
        self.demo_select_dispatch = {}

        # set the size of the demo window, etc
        self.setGeometry(300, 300, DemoWidth, DemoHeight)
        self.setWindowTitle('%s %s' % (DemoName, DemoVersion))
        self.show()

        # finally, bind events to handlers
        self.pyslipqt.events.EVT_PYSLIPQT_LEVEL.connect(self.level_change_event)
        self.pyslipqt.events.EVT_PYSLIPQT_POSITION.connect(self.mouse_posn_event)
        self.pyslipqt.events.EVT_PYSLIPQT_SELECT.connect(self.select_event)

#        def hovered():
#            self.labelOnlineHelp.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
#        self.labelOnlineHelp.linkHovered.connect(hovered)

#        self.panel = wx.Panel(self, wx.ID_ANY)
#        self.panel.SetBackgroundColour(wx.WHITEself.select_event80)
#        self.panel.ClearBackground()

#        # create tileset menuitems
#        menuBar = wx.MenuBar()
#        tile_menu = wx.Menu()
#
#        # initialise tileset handling
#        self.tile_source = None
#        # a dict of "gui_id: (name, module_name, object)" tuples
#        self.id2tiledata = {}
#        # a dict of "name: gui_id"
#        self.name2guiid = {}
#
#        self.default_tileset_name = None
#        for (name, module_name) in TileSources:
#            new_id = wx.NewId()
#            tile_menu.Append(new_id, name, name, wx.ITEM_RADIO)
#            self.Bind(wx.EVT_MENU, self.onTilesetSelect)
#            self.id2tiledata[new_id] = (name, module_name, None)
#            self.name2guiid[name] = new_id
#            if name == DefaultTileset:
#                self.default_tileset_name = name
#
#        if self.default_tileset_name is None:
#            raise Exception('Bad DefaultTileset (%s) or TileSources (%s)'
#                            % (DefaultTileset, str(TileSources)))

        # finally, bind events to handlers
#        self.pyslipqt.Bind(pyslipqt.EVT_PYSLIP_SELECT, self.handle_select_event)
#        self.pyslipqt.Bind(pyslipqt.EVT_PYSLIP_BOXSELECT, self.handle_select_event)
#        self.pyslipqt.Bind(pyslipqt.EVT_PYSLIP_POSITION, self.handle_position_event)
#        self.pyslipqt.Bind(pyslipqt.EVT_PYSLIP_LEVEL, self.handle_level_change)

#        # select the required tileset
#        item_id = self.name2guiid[self.default_tileset_name]
#        tile_menu.Check(item_id, True)

    def make_gui_controls(self, grid):
        """Build the 'controls' part of the GUI

        grid  reference to grid that we populate

        Returns the number of rows add ed to the 'grid' layout.
        """

        # the 'grid_row' variable is row to add into
        grid_row = 0

        # put level and position into grid at top right
        self.map_level = DisplayText(title='Map level', label='Level:',
                                     tooltip=None, text_width=30)
        grid.addWidget(self.map_level, grid_row, 1, 1, 1)
        self.mouse_position = DisplayText(title='Cursor position',
                                          label='Lon/Lat:', text_width=100,
                                          tooltip='Shows the mouse longitude and latitude on the map',)
        grid.addWidget(self.mouse_position, grid_row, 2, 1, 1)
        grid_row += 1

        # controls for map-relative points layer
        point = LayerControl(self, title='Points, map relative %s' % str(MRPointShowLevels), selectable=True)
        point.change_add.connect(self.pointOnOff)   # tie to event handler(s)
        point.change_show.connect(self.pointShowOnOff)
        point.change_select.connect(self.pointSelectOnOff)
        grid.addWidget(point, grid_row, 1, 1, 3)
        grid_row += 1

        # controls for view-relative points layer
        point_v = LayerControl(self, 'Points, view relative', selectable=True)
        point_v.change_add.connect(self.pointViewOnOff)   # tie to event handler(s)
        point_v.change_show.connect(self.pointViewShowOnOff)
        point_v.change_select.connect(self.pointViewSelectOnOff)
        grid.addWidget(point_v, grid_row, 1, 1, 3)
        grid_row += 1

        # controls for map-relative image layer
        image = LayerControl(self, 'Images, map relative %s' % str(MRImageShowLevels), selectable=True)
        image.change_add.connect(self.imageOnOff)   # tie to event handler(s)
        image.change_show.connect(self.imageShowOnOff)
        image.change_select.connect(self.imageSelectOnOff)
        grid.addWidget(image, grid_row, 1, 1, 3)
        grid_row += 1

        # controls for map-relative image layer
        image_v = LayerControl(self, 'Images, view relative', selectable=True) 
        image_v.change_add.connect(self.imageViewOnOff)   # tie to event handler(s)
        image_v.change_show.connect(self.imageViewShowOnOff)
        image_v.change_select.connect(self.imageViewSelectOnOff)
        grid.addWidget(image_v, grid_row, 1, 1, 3)
        grid_row += 1

        # controls for map-relative text layer
        text = LayerControl(self, 'Text, map relative %s' % str(MRTextShowLevels), selectable=True)
        text.change_add.connect(self.textOnOff)     # tie to event handler(s)
        text.change_show.connect(self.textShowOnOff)
        text.change_select.connect(self.textSelectOnOff)
        grid.addWidget(text, grid_row, 1, 1, 3)
        grid_row += 1

        # controls for view-relative text layer
        text_v = LayerControl(self, 'Text, view relative', selectable=True)
        text_v.change_add.connect(self.textViewOnOff)    # tie to event handler(s)
        text_v.change_show.connect(self.textViewShowOnOff)
        text_v.change_select.connect(self.textViewSelectOnOff)
        grid.addWidget(text_v, grid_row, 1, 1, 3)
        grid_row += 1

        # controls for map-relative polygon layer
        poly = LayerControl(self, 'Polygon, map relative %s' % str(MRPolyShowLevels), selectable=True)
        poly.change_add.connect(self.polyOnOff)     # tie to event handler(s)
        poly.change_show.connect(self.polyShowOnOff)
        poly.change_select.connect(self.polySelectOnOff)
        grid.addWidget(poly, grid_row, 1, 1, 3)
        grid_row += 1

        # controls for view-relative polygon layer
        poly_v = LayerControl(self, 'Polygon, view relative', selectable=True)
        poly_v.change_add.connect(self.polyViewOnOff)    # tie to event handler(s)
        poly_v.change_show.connect(self.polyViewShowOnOff)
        poly_v.change_select.connect(self.polyViewSelectOnOff)
        grid.addWidget(poly_v, grid_row, 1, 1, 3)
        grid_row += 1

        # controls for map-relative polyline layer
        poll = LayerControl(self, 'Polyline, map relative %s' % str(MRPolyShowLevels), selectable=True)
        poll.change_add.connect(self.polylineOnOff)     # tie to event handler(s)
        poll.change_show.connect(self.polylineShowOnOff)
        poll.change_select.connect(self.polylineSelectOnOff)
        grid.addWidget(poll, grid_row, 1, 1, 3)
        grid_row += 1

        # controls for view-relative polyline layer
        poll_v = LayerControl(self, 'Polyline, view relative', selectable=True)
        poll_v.change_add.connect(self.polylineViewOnOff)    # tie to event handler(s)
        poll_v.change_show.connect(self.polylineViewShowOnOff)
        poll_v.change_select.connect(self.polylineViewSelectOnOff)
        grid.addWidget(poll_v, grid_row, 1, 1, 3)
        grid_row += 1

        return grid_row

    def onTilesetSelect(self, event):
        """User selected a tileset from the menu.

        event  the menu select event
        """

        menu_id = event.GetId()
        try:
            (name, module_name, new_tile_obj) = self.id2tiledata[menu_id]
        except KeyError:
            # badly formed self.id2tiledata element
            raise Exception('self.id2tiledata is badly formed:\n%s'
                            % str(self.id2tiledata))

        if new_tile_obj is None:
            # haven't seen this tileset before, import and instantiate
            module_name = self.id2tiledata[menu_id][1]
            exec('import %s as tiles' % module_name)
            new_tile_obj = tiles.Tiles()

            # update the self.id2tiledata element
            self.id2tiledata[menu_id] = (name, module_name, new_tile_obj)

        self.pyslipqt.ChangeTileset(new_tile_obj)

    def onClose(self):
        """Application is closing."""

        pass

        #self.Close(True)

######
## Build the GUI
######
#
#    def make_gui(self, parent):
#        """Create application GUI."""
#
#        # start application layout
#        all_display = QHBoxLayout()
#
#        # put map view in left of horizontal box
#        sl_box = self.make_gui_view(parent)
#        all_display.addLayout(sl_box)
#
#        # add controls at right
#        controls = self.make_gui_controls(parent)
#        all_display.addLayout(controls)
#
#        return all_display
#
#    def make_gui_view(self, parent):
#        """Build the map view widget
#
#        parent  reference to the widget parent
#
#        Returns the box layout.
#        """
#
#        # create gui objects
#        vbox = QVBoxLayout()
#        self.pyslipqt = pyslipqt.PySlipQt(parent, tile_src=self.tile_source, start_level=0)
#        vbox.addWidget(self.pyslipqt)
#
#        return vbox
#
#    def make_gui_controls(self, parent):
#        """Build the 'controls' part of the GUI
#
#        parent  reference to parent
#
#        Returns reference to containing sizer object.
#        """
#
#        # all controls in vertical box sizer
#        controls = QVBoxLayout()
#
#        # put level and position into one 'controls' position
#        l_p = self.make_gui_level_posn(parent)
#        controls.addLayout(l_p)
#
#        # controls for map-relative points layer
#        point = self.make_gui_point(parent)
#        controls.addWidget(point)
#
#        # controls for view-relative points layer
#        point_view = self.make_gui_point_view(parent)
#        controls.addWidget(point_view)
#
#        # controls for map-relative image layer
#        image = self.make_gui_image(parent)
#        controls.addWidget(image)
#
#        # controls for map-relative image layer
#        image_view = self.make_gui_image_view(parent)
#        controls.addWidget(image_view)
#
#        # controls for map-relative text layer
#        text = self.make_gui_text(parent)
#        controls.addWidget(text)
#
#        # controls for view-relative text layer
#        text_view = self.make_gui_text_view(parent)
#        controls.addWidget(text_view)
#
#        # controls for map-relative polygon layer
#        poly = self.make_gui_poly(parent)
#        controls.addWidget(poly)
#
#        # controls for view-relative polygon layer
#        poly_view = self.make_gui_poly_view(parent)
#        controls.addWidget(poly_view)
#
#        # controls for map-relative polyline layer
#        polyline = self.make_gui_polyline(parent)
#        controls.addWidget(polyline)
#
#        # controls for view-relative polyline layer
#        polyline_view = self.make_gui_polyline_view(parent)
#        controls.addWidget(polyline_view)
#
#        return controls
#
#    def make_gui_level_posn(self, parent):
#        """Build the control that shows the level.
#
#        parent  reference to parent
#
#        Returns reference to containing sizer object.
#        """
#
#        hbox = QHBoxLayout()
#        self.map_level = DisplayText(title='Map level', label='Level:', tooltip=None, width=50)
#        hbox.addWidget(self.map_level)
#        self.mouse_position = DisplayText(title='Cursor position',
#                                          label='Lon/Lat:',
#                                          tooltip='Shows the mouse longitude and latitude on the map',
#                                          width=50)
#        hbox.addWidget(self.mouse_position)
#
#        return hbox
#
#    def make_gui_point(self, parent):
#        """Build the points part of the controls part of GUI.
#
#        parent  reference to parent
#
#        Returns reference to containing sizer object.
#        """
#
#        # create widgets
#        point = LayerControl(parent, title='Points, map relative %s' % str(MRPointShowLevels), selectable=True)
#
#        # tie to event handler(s)
#        point.change_add.connect(self.pointOnOff)
#        point.change_show.connect(self.pointShowOnOff)
#        point.change_select.connect(self.pointSelectOnOff)
#
#        return point
#
#    def make_gui_point_view(self, parent):
#        """Build the view-relative points part of the GUI.
#
#        parent  reference to parent
#
#        Returns reference to containing sizer object.
#        """
#
#        # create widgets
#        point = LayerControl(parent, 'Points, view relative', selectable=True)
#
#        # tie to event handler(s)
#        point.change_add.connect(self.pointViewOnOff)
#        point.change_show.connect(self.pointViewShowOnOff)
#        point.change_select.connect(self.pointViewSelectOnOff)
#
#        return point
#
#    def make_gui_image(self, parent):
#        """Build the image part of the controls part of GUI.
#
#        parent  reference to parent
#
#        Returns reference to containing sizer object.
#        """
#
#        # create widgets
#        image = LayerControl(parent, 'Images, map relative %s' % str(MRImageShowLevels), selectable=True)
#
#        # tie to event handler(s)
#        image.change_add.connect(self.imageOnOff)
#        image.change_show.connect(self.imageShowOnOff)
#        image.change_select.connect(self.imageSelectOnOff)
#
#        return image
#
#    def make_gui_image_view(self, parent):
#        """Build the view-relative image part of the controls part of GUI.
#
#        parent  reference to parent
#
#        Returns reference to containing sizer object.
#        """
#
#        # create widgets
#        image = LayerControl(parent, 'Images, view relative', selectable=True) 
#
#        # tie to event handler(s)
#        image.change_add.connect(self.imageViewOnOff)
#        image.change_show.connect(self.imageViewShowOnOff)
#        image.change_select.connect(self.imageViewSelectOnOff)
#
#        return image
#
#    def make_gui_text(self, parent):
#        """Build the map-relative text part of the controls part of GUI.
#
#        parent  reference to parent
#
#        Returns reference to containing sizer object.
#        """
#
#        # create widgets
#        text = LayerControl(parent, 'Text, map relative %s' % str(MRTextShowLevels), selectable=True)
#
#        # tie to event handler(s)
#        text.change_add.connect(self.textOnOff)
#        text.change_show.connect(self.textShowOnOff)
#        text.change_select.connect(self.textSelectOnOff)
#
#        return text
#
#    def make_gui_text_view(self, parent):
#        """Build the view-relative text part of the controls part of GUI.
#
#        parent  reference to parent
#
#        Returns reference to containing sizer object.
#        """
#
#        # create widgets
#        text_view = LayerControl(parent, 'Text, view relative', selectable=True)
#
#        # tie to event handler(s)
#        text_view.change_add.connect(self.textViewOnOff)
#        text_view.change_show.connect(self.textViewShowOnOff)
#        text_view.change_select.connect(self.textViewSelectOnOff)
#
#        return text_view
#
#    def make_gui_poly(self, parent):
#        """Build the map-relative polygon part of the controls part of GUI.
#
#        parent  reference to parent
#
#        Returns reference to containing sizer object.
#        """
#
#        # create widgets
#        poly = LayerControl(parent, 'Polygon, map relative %s' % str(MRPolyShowLevels), selectable=True)
#
#        # tie to event handler(s)
#        poly.change_add.connect(self.polyOnOff)
#        poly.change_show.connect(self.polyShowOnOff)
#        poly.change_select.connect(self.polySelectOnOff)
#
#        return poly
#
#    def make_gui_poly_view(self, parent):
#        """Build the view-relative polygon part of the controls part of GUI.
#
#        parent  reference to parent
#
#        Returns reference to containing sizer object.
#        """
#
#        # create widgets
#        poly_view = LayerControl(parent, 'Polygon, view relative', selectable=True)
#
#        # tie to event handler(s)
#        poly_view.change_add.connect(self.polyViewOnOff)
#        poly_view.change_show.connect(self.polyViewShowOnOff)
#        poly_view.change_select.connect(self.polyViewSelectOnOff)
#
#        return poly_view
#
#    def make_gui_polyline(self, parent):
#        """Build the map-relative polyline part of the controls part of GUI.
#
#        parent  reference to parent
#
#        Returns reference to containing sizer object.
#        """
#
#        # create widgets
#        poly = LayerControl(parent, 'Polyline, map relative %s' % str(MRPolyShowLevels), selectable=True)
#
#        # tie to event handler(s)
#        poly.change_add.connect(self.polylineOnOff)
#        poly.change_show.connect(self.polylineShowOnOff)
#        poly.change_select.connect(self.polylineSelectOnOff)
#
#        return poly
#
#    def make_gui_polyline_view(self, parent):
#        """Build the view-relative polyline part of the controls part of GUI.
#
#        parent  reference to parent
#
#        Returns reference to containing sizer object.
#        """
#
#        # create widgets
#        poly_view = LayerControl(parent, 'Polyline, view relative', selectable=True)
#
#        # tie to event handler(s)
#        poly_view.change_add.connect(self.polylineViewOnOff)
#        poly_view.change_show.connect(self.polylineViewShowOnOff)
#        poly_view.change_select.connect(self.polylineViewSelectOnOff)
#
#        return poly_view

    ######
    # pySlip demo control event handlers
    ######

##### map-relative point layer

    def pointOnOff(self, event):
        """Handle OnOff event for point layer control."""

        if event:
            # event is True, so we are adding the maprel point layer
            self.point_layer = \
                self.pyslipqt.AddPointLayer(PointData, map_rel=True,
                                            colour=PointDataColour, radius=3,
                                            # offset points to exercise placement
                                            offset_x=0, offset_y=0, visible=True,
                                            show_levels=MRPointShowLevels,
                                            delta=DefaultPointMapDelta,
                                            placement='nw',   # check placement
                                            name='<pt_layer>')
        else:
            # event is False, so we are removing the maprel point layer
            self.pyslipqt.DeleteLayer(self.point_layer)
            self.point_layer = None
            if self.sel_point_layer:
                self.pyslipqt.DeleteLayer(self.sel_point_layer)
                self.sel_point_layer = None
                self.sel_point = None

    def pointShowOnOff(self, event):
        """Handle ShowOnOff event for point layer control."""

        if event:
            # if True, user selected "Show"
            self.pyslipqt.ShowLayer(self.point_layer)
            if self.sel_point_layer:
                self.pyslipqt.ShowLayer(self.sel_point_layer)
        else:
            # if False, user unselected "SHow"
            self.pyslipqt.HideLayer(self.point_layer)
            if self.sel_point_layer:
                self.pyslipqt.HideLayer(self.sel_point_layer)

    def pointSelectOnOff(self, event):
        """Handle SelectOnOff event for point layer control."""

        layer = self.point_layer
        if event:
            # if True, user selected "Selectable"
            self.add_select_handler(layer, self.pointSelect)
            self.pyslipqt.SetLayerSelectable(layer, True)
        else:
            # if True, user unselected "Selectable"
            self.del_select_handler(layer)
            self.pyslipqt.SetLayerSelectable(layer, False)

    def pointSelect(self, event):
        """Handle map-relative point select exception from pyslipqt.

        event  the event that contains these attributes:
                   type       the type of point selection: single or box
                   layer_id   ID of the layer the select occurred on
                   selection  [list of] tuple (xgeo,ygeo) of selected point
                              (if None then no point(s) selected)
                   data       userdata object of the selected point

        The selection could be a single or box select.

        The point select is designed to be select point(s) for on, then select
        point(s) again for off.  Clicking away from the already selected point
        doesn't remove previously selected point(s) if nothing is selected.  We
        do this to show the selection/deselection of point(s) is up to the user,
        not pySlip.

        This code also shows how to combine handling of EventSelect and
        EventBoxSelect events.
        """

        selection = event.selection

        if selection == self.sel_point:
            # same point(s) selected again, turn point(s) off
            self.pyslipqt.DeleteLayer(self.sel_point_layer)
            self.sel_point_layer = None
            self.sel_point = None
        elif selection:
            # some other point(s) selected, delete previous selection, if any
            if self.sel_point_layer:
                self.pyslipqt.DeleteLayer(self.sel_point_layer)

            # remember selection (need copy as highlight modifies attributes)
            self.sel_point = copy.deepcopy(selection)

            # choose different highlight colour for different type of selection
            selcolour = '#00ffff'
            if event.type == pyslipqt.EventSelect:
                selcolour = '#0000ff'

            # get selected points into form for display layer
            # delete 'colour' and 'radius' attributes as we want different values
            highlight = []
            for (x, y, d) in selection:
                del d['colour']     # AddLayer...() ensures keys exist
                del d['radius']
                highlight.append((x, y, d))

            # layer with highlight of selected poijnts
            self.sel_point_layer = \
                self.pyslipqt.AddPointLayer(highlight, map_rel=True,
                                            colour=selcolour,
                                            radius=5, visible=True,
                                            show_levels=MRPointShowLevels,
                                            name='<sel_pt_layer>')

            # make sure highlight layer is BELOW selected layer
            self.pyslipqt.PlaceLayerBelowLayer(self.sel_point_layer,
                                               self.point_layer)
        # else: we ignore an empty selection

        return True

##### view-relative point layer

    def pointViewOnOff(self, event):
        """Handle OnOff event for point view layer control."""

        if event:
            self.point_view_layer = \
                self.pyslipqt.AddPointLayer(PointViewData, map_rel=False,
                                            placement=PointViewDataPlacement,
                                            colour=PointViewDataColour, radius=1,
                                            delta=DefaultPointViewDelta,
                                            visible=True,
                                            name='<point_view_layer>')
        else:
            self.pyslipqt.DeleteLayer(self.point_view_layer)
            self.point_view_layer = None
            if self.sel_point_view_layer:
                self.pyslipqt.DeleteLayer(self.sel_point_view_layer)
                self.sel_point_view_layer = None
                self.sel_point_view = None

    def pointViewShowOnOff(self, event):
        """Handle ShowOnOff event for point view layer control."""

        if event:
            self.pyslipqt.ShowLayer(self.point_view_layer)
            if self.sel_point_view_layer:
                self.pyslipqt.ShowLayer(self.sel_point_view_layer)
        else:
            self.pyslipqt.HideLayer(self.point_view_layer)
            if self.sel_point_view_layer:
                self.pyslipqt.HideLayer(self.sel_point_view_layer)

    def pointViewSelectOnOff(self, event):
        """Handle SelectOnOff event for point view layer control."""

        layer = self.point_view_layer
        if event:
            self.add_select_handler(layer, self.pointViewSelect)
            self.pyslipqt.SetLayerSelectable(layer, True)
        else:
            self.del_select_handler(layer)
            self.pyslipqt.SetLayerSelectable(layer, False)

    def pointViewSelect(self, event):
        """Handle view-relative point select exception from pyslipqt.

        event  the event that contains these attributes:
                   type       the type of point selection: single or box
                   selection  [list of] tuple (xgeo,ygeo) of selected point
                              (if None then no point(s) selected)
                   data       userdata object of the selected point

        The selection could be a single or box select.

        The point select is designed to be click point for on, then any other
        select event turns that point off, whether there is a selection or not
        and whether the same point is selected or not.
        """

        selection = event.selection

        # if there is a previous selection, remove it
        if self.sel_point_view_layer:
            self.pyslipqt.DeleteLayer(self.sel_point_view_layer)
            self.sel_point_view_layer = None

        if selection and selection != self.sel_point_view:
            self.sel_point_view = selection

            # get selected points into form for display layer
            highlight = []
            for (x, y, d) in selection:
                del d['colour']
                del d['radius']
                highlight.append((x, y, d))

            # assume a box selection
            self.sel_point_view_layer = \
                self.pyslipqt.AddPointLayer(highlight, map_rel=False,
                                            placement='se',
                                            colour='#0000ff',
                                            radius=3, visible=True,
                                            name='<sel_pt_view_layer>')
        else:
            self.sel_point_view = None

        return True

##### map-relative image layer

    def imageOnOff(self, event):
        """Handle OnOff event for map-relative image layer control."""

        if event:
            self.image_layer = \
                self.pyslipqt.AddImageLayer(ImageData, map_rel=True,
                                            visible=True,
                                            delta=DefaultImageMapDelta,
                                            show_levels=MRImageShowLevels,
                                            name='<image_layer>')
        else:
            self.pyslipqt.DeleteLayer(self.image_layer)
            self.image_layer = None
            if self.sel_image_layer:
                self.pyslipqt.DeleteLayer(self.sel_image_layer)
                self.sel_image_layer = None
                self.sel_image = None

    def imageShowOnOff(self, event):
        """Handle ShowOnOff event for image layer control."""

        if event:
            self.pyslipqt.ShowLayer(self.image_layer)
            if self.sel_image_layer:
                self.pyslipqt.ShowLayer(self.sel_image_layer)
        else:
            self.pyslipqt.HideLayer(self.image_layer)
            if self.sel_image_layer:
                self.pyslipqt.HideLayer(self.sel_image_layer)

    def imageSelectOnOff(self, event):
        """Handle SelectOnOff event for image layer control."""

        layer = self.image_layer
        if event:
            self.add_select_handler(layer, self.imageSelect)
            self.pyslipqt.SetLayerSelectable(layer, True)
        else:
            self.del_select_handler(layer)
            self.pyslipqt.SetLayerSelectable(layer, False)

    def imageSelect(self, event):
        """Select event from pyslipqt.

        event  the event that contains these attributes:
                   type       the type of point selection: single or box
                   selection  [list of] tuple (xgeo,ygeo) of selected point
                              (if None then no point(s) selected)
                   data       userdata object of the selected point

        The selection could be a single or box select.
        """

        selection = event.selection
        #relsel = event.relsel

        # select again, turn selection off
        if selection == self.sel_image:
            self.pyslipqt.DeleteLayer(self.sel_image_layer)
            self.sel_image_layer = self.sel_image = None
        elif selection:
            # new image selected, show highlight
            if self.sel_image_layer:
                self.pyslipqt.DeleteLayer(self.sel_image_layer)
            self.sel_image = selection

            # get selected points into form for display layer
            points = []
            for (x, y, f, d) in selection:
                del d['colour']
                del d['radius']
                points.append((x, y, d))

            self.sel_image_layer = \
                self.pyslipqt.AddPointLayer(points, map_rel=True,
                                            colour='#0000ff',
                                            radius=5, visible=True,
                                            show_levels=[3,4],
                                            name='<sel_pt_layer>')
            self.pyslipqt.PlaceLayerBelowLayer(self.sel_image_layer,
                                               self.image_layer)

        return True

    def imageBSelect(self, id, selection=None):
        """Select event from pyslipqt."""

        # remove any previous selection
        if self.sel_image_layer:
            self.pyslipqt.DeleteLayer(self.sel_image_layer)
            self.sel_image_layer = None

        if selection:
            # get selected points into form for display layer
            points = []
            for (x, y, f, d) in selection:
                del d['colour']
                del d['radius']
                points.append((x, y, d))

            self.sel_image_layer = \
                self.pyslipqt.AddPointLayer(points, map_rel=True,
                                            colour='#e0e0e0',
                                            radius=13, visible=True,
                                            show_levels=[3,4],
                                            name='<boxsel_img_layer>')
            self.pyslipqt.PlaceLayerBelowLayer(self.sel_image_layer,
                                               self.image_layer)

        return True

##### view-relative image layer

    def imageViewOnOff(self, add):
        """Handle OnOff event for view-relative image layer control."""

        if add:
            self.image_view_layer = \
                self.pyslipqt.AddImageLayer(ImageViewData, map_rel=False,
                                            delta=DefaultImageViewDelta,
                                            visible=True,
                                            name='<image_view_layer>')
        else:
            self.pyslipqt.DeleteLayer(self.image_view_layer)
            self.image_view_layer = None
            if self.sel_image_view_layer:
                self.pyslipqt.DeleteLayer(self.sel_image_view_layer)
                self.sel_image_view_layer = None
            if self.sel_imagepoint_view_layer:
                self.pyslipqt.DeleteLayer(self.sel_imagepoint_view_layer)
                self.sel_imagepoint_view_layer = None

    def imageViewShowOnOff(self, event):
        """Handle ShowOnOff event for image layer control."""

        if event:
            self.pyslipqt.ShowLayer(self.image_view_layer)
            if self.sel_image_view_layer:
                self.pyslipqt.ShowLayer(self.sel_image_view_layer)
            if self.sel_imagepoint_view_layer:
                self.pyslipqt.ShowLayer(self.sel_imagepoint_view_layer)
        else:
            self.pyslipqt.HideLayer(self.image_view_layer)
            if self.sel_image_view_layer:
                self.pyslipqt.HideLayer(self.sel_image_view_layer)
            if self.sel_imagepoint_view_layer:
                self.pyslipqt.HideLayer(self.sel_imagepoint_view_layer)

    def imageViewSelectOnOff(self, event):
        """Handle SelectOnOff event for image layer control."""

        layer = self.image_view_layer
        if event:
            self.add_select_handler(layer, self.imageViewSelect)
            self.pyslipqt.SetLayerSelectable(layer, True)
        else:
            self.del_select_handler(layer)
            self.pyslipqt.SetLayerSelectable(layer, False)

    def imageViewSelect(self, event):
        """View-relative image select event from pyslipqt.

        event  the event that contains these attributes:
                   selection  [list of] tuple (xgeo,ygeo) of selected point
                              (if None then no point(s) selected)
                   relsel     relative position of single point select,
                              None if box select

        The selection could be a single or box select.

        The selection mode is different here.  An empty selection will remove
        any current selection.  This shows the flexibility that user code
        can implement.

        The code below doesn't assume a placement of the selected image, it
        figures out the correct position of the 'highlight' layers.  This helps
        with debugging, as we can move the compass rose anywhere we like.
        """

        selection = event.selection
        relsel = event.relsel       # None if box select

        # only one image selectable, remove old selections (if any)
        if self.sel_image_view_layer:
            self.pyslipqt.DeleteLayer(self.sel_image_view_layer)
            self.sel_image_view_layer = None
        if self.sel_imagepoint_view_layer:
            self.pyslipqt.DeleteLayer(self.sel_imagepoint_view_layer)
            self.sel_imagepoint_view_layer = None

        if selection:
            # figure out compass rose attributes
            attr_dict = ImageViewData[0][3]
            img_placement = attr_dict['placement']

            self.sel_imagepoint_view_layer = None
            if relsel:
                # unpack event relative selection point
                (sel_x, sel_y) = relsel     # select relative point in image

# FIXME  This should be cleaner, user shouldn't have to know internal structure
# FIXME  or fiddle with placement perturbations

                # add selection point
                point_place_coords = {'ne': '(sel_x - CR_Width, sel_y)',
                                      'ce': '(sel_x - CR_Width, sel_y - CR_Height/2.0)',
                                      'se': '(sel_x - CR_Width, sel_y - CR_Height)',
                                      'cs': '(sel_x - CR_Width/2.0, sel_y - CR_Height)',
                                      'sw': '(sel_x, sel_y - CR_Height)',
                                      'cw': '(sel_x, sel_y - CR_Height/2.0)',
                                      'nw': '(sel_x, sel_y)',
                                      'cn': '(sel_x - CR_Width/2.0, sel_y)',
                                      'cc': '(sel_x - CR_Width/2.0, sel_y - CR_Height/2.0)',
                                      '':   '(sel_x, sel_y)',
                                      None: '(sel_x, sel_y)',
                                     }

                point = eval(point_place_coords[img_placement])
                self.sel_imagepoint_view_layer = \
                    self.pyslipqt.AddPointLayer((point,), map_rel=False,
                                                colour='green',
                                                radius=5, visible=True,
                                                placement=img_placement,
                                                name='<sel_image_view_point>')

            # add polygon outline around image
            p_dict = {'placement': img_placement, 'width': 3, 'colour': 'green', 'closed': True}
            poly_place_coords = {'ne': '(((-CR_Width,0),(0,0),(0,CR_Height),(-CR_Width,CR_Height)),p_dict)',
                                 'ce': '(((-CR_Width,-CR_Height/2.0),(0,-CR_Height/2.0),(0,CR_Height/2.0),(-CR_Width,CR_Height/2.0)),p_dict)',
                                 'se': '(((-CR_Width,-CR_Height),(0,-CR_Height),(0,0),(-CR_Width,0)),p_dict)',
                                 'cs': '(((-CR_Width/2.0,-CR_Height),(CR_Width/2.0,-CR_Height),(CR_Width/2.0,0),(-CR_Width/2.0,0)),p_dict)',
                                 'sw': '(((0,-CR_Height),(CR_Width,-CR_Height),(CR_Width,0),(0,0)),p_dict)',
                                 'cw': '(((0,-CR_Height/2.0),(CR_Width,-CR_Height/2.0),(CR_Width,CR_Height/2.0),(0,CR_Height/2.0)),p_dict)',
                                 'nw': '(((0,0),(CR_Width,0),(CR_Width,CR_Height),(0,CR_Height)),p_dict)',
                                 'cn': '(((-CR_Width/2.0,0),(CR_Width/2.0,0),(CR_Width/2.0,CR_Height),(-CR_Width/2.0,CR_Height)),p_dict)',
                                 'cc': '(((-CR_Width/2.0,-CR_Height/2.0),(CR_Width/2.0,-CR_Height/2.0),(CR_Width/2.0,CR_Height/2.0),(-CR_Width/2.0,CR_Height/2.0)),p_dict)',
                                 '':   '(((x, y),(x+CR_Width,y),(x+CR_Width,y+CR_Height),(x,y+CR_Height)),p_dict)',
                                 None: '(((x, y),(x+CR_Width,y),(x+CR_Width,y+CR_Height),(x,y+CR_Height)),p_dict)',
                                }
            pdata = eval(poly_place_coords[img_placement])
            self.sel_image_view_layer = \
                self.pyslipqt.AddPolygonLayer((pdata,), map_rel=False,
                                              name='<sel_image_view_outline>',
                                             )

        return True

##### map-relative text layer

    def textOnOff(self, event):
        """Handle OnOff event for map-relative text layer control."""

        if event:
            self.text_layer = \
                self.pyslipqt.AddTextLayer(TextData, map_rel=True,
                                           name='<text_layer>', visible=True,
                                           delta=DefaultTextMapDelta,
                                           show_levels=MRTextShowLevels,
                                           placement='ne')
        else:
            self.pyslipqt.DeleteLayer(self.text_layer)
            self.text_layer = None
            if self.sel_text_layer:
                self.pyslipqt.DeleteLayer(self.sel_text_layer)
                self.sel_text_layer = None
                self.sel_text_point = None

    def textShowOnOff(self, event):
        """Handle ShowOnOff event for text layer control."""

        if event:
            self.pyslipqt.ShowLayer(self.text_layer)
            if self.sel_text_layer:
                self.pyslipqt.ShowLayer(self.sel_text_layer)
        else:
            self.pyslipqt.HideLayer(self.text_layer)
            if self.sel_text_layer:
                self.pyslipqt.HideLayer(self.sel_text_layer)

    def textSelectOnOff(self, event):
        """Handle SelectOnOff event for text layer control."""

        layer = self.text_layer
        if event:
            self.add_select_handler(layer, self.textSelect)
            self.pyslipqt.SetLayerSelectable(layer, True)
        else:
            self.del_select_handler(layer)
            self.pyslipqt.SetLayerSelectable(layer, False)


    def textSelect(self, event):
        """Map-relative text select event from pyslipqt.

        event  the event that contains these attributes:
                   type       the type of point selection: single or box
                   selection  [list of] tuple (xgeo,ygeo) of selected point
                              (if None then no point(s) selected)

        The selection could be a single or box select.

        The selection mode here is more standard: empty select turns point(s)
        off, selected points reselection leaves points selected.
        """

        selection = event.selection

        if self.sel_text_layer:
            # turn previously selected point(s) off
            self.sel_text = None
            self.pyslipqt.DeleteLayer(self.sel_text_layer)
            self.sel_text_layer = None

        if selection:
            if self.sel_text_layer:
                self.pyslipqt.DeleteLayer(self.sel_text_layer)
            self.sel_text = selection

            # get selected points into form for display layer
            points = []
            for (x, y, t, d) in selection:
                del d['colour']     # remove point attributes, want different
                del d['radius']
                del d['offset_x']   # remove offsets, we want point not text
                del d['offset_y']
                points.append((x, y, d))

            self.sel_text_layer = \
                self.pyslipqt.AddPointLayer(points, map_rel=True,
                                            colour='#0000ff',
                                            radius=5, visible=True,
                                            show_levels=MRTextShowLevels,
                                            name='<sel_text_layer>')
            self.pyslipqt.PlaceLayerBelowLayer(self.sel_text_layer,
                                               self.text_layer)

        return True

##### view-relative text layer

    def textViewOnOff(self, event):
        """Handle OnOff event for view-relative text layer control."""

        if event:
            self.text_view_layer = \
                self.pyslipqt.AddTextLayer(TextViewData, map_rel=False,
                                           name='<text_view_layer>',
                                           delta=DefaultTextViewDelta,
                                           placement=TextViewDataPlace,
                                           visible=True,
                                           fontsize=24, textcolour='#0000ff',
                                           offset_x=TextViewDataOffX,
                                           offset_y=TextViewDataOffY)
        else:
            self.pyslipqt.DeleteLayer(self.text_view_layer)
            self.text_view_layer = None
            if self.sel_text_view_layer:
                self.pyslipqt.DeleteLayer(self.sel_text_view_layer)
                self.sel_text_view_layer = None

    def textViewShowOnOff(self, event):
        """Handle ShowOnOff event for view text layer control."""

        if event:
            self.pyslipqt.ShowLayer(self.text_view_layer)
            if self.sel_text_view_layer:
                self.pyslipqt.ShowLayer(self.sel_text_view_layer)
        else:
            self.pyslipqt.HideLayer(self.text_view_layer)
            if self.sel_text_view_layer:
                self.pyslipqt.HideLayer(self.sel_text_view_layer)

    def textViewSelectOnOff(self, event):
        """Handle SelectOnOff event for view text layer control."""

        layer = self.text_view_layer
        if event:
            self.add_select_handler(layer, self.textViewSelect)
            self.pyslipqt.SetLayerSelectable(layer, True)
        else:
            self.del_select_handler(layer)
            self.pyslipqt.SetLayerSelectable(layer, False)

    def textViewSelect(self, event):
        """View-relative text select event from pyslipqt.

        event  the event that contains these attributes:
                   type       the type of point selection: single or box
                   selection  [list of] tuple (xgeo,ygeo) of selected point
                              (if None then no point(s) selected)

        The selection could be a single or box select.

        The selection mode here is more standard: empty select turns point(s)
        off, selected points reselection leaves points selected.
        """

        selection = event.selection

        # turn off any existing selection
        if self.sel_text_view_layer:
            self.pyslipqt.DeleteLayer(self.sel_text_view_layer)
            self.sel_text_view_layer = None

        if selection:
            # get selected points into form for point display layer
            points = []
            for (x, y, t, d) in selection:
                del d['colour']     # want to override colour, radius
                del d['radius']
                points.append((x, y, d))

            self.sel_text_view_layer = \
                self.pyslipqt.AddPointLayer(points, map_rel=False,
                                            colour='black',
                                            radius=5, visible=True,
                                            show_levels=MRTextShowLevels,
                                            name='<sel_text_view_layer>')
            self.pyslipqt.PlaceLayerBelowLayer(self.sel_text_view_layer,
                                               self.text_view_layer)

        return True

##### map-relative polygon layer

    def polyOnOff(self, event):
        """Handle OnOff event for map-relative polygon layer control."""

        if event:
            self.poly_layer = \
                self.pyslipqt.AddPolygonLayer(PolyData, map_rel=True,
                                              visible=True,
                                              delta=DefaultPolygonMapDelta,
                                              show_levels=MRPolyShowLevels,
                                              name='<poly_layer>')
        else:
            self.pyslipqt.DeleteLayer(self.poly_layer)
            self.poly_layer = None
            if self.sel_poly_layer:
                self.pyslipqt.DeleteLayer(self.sel_poly_layer)
                self.sel_poly_layer = None
                self.sel_poly_point = None

    def polyShowOnOff(self, event):
        """Handle ShowOnOff event for polygon layer control."""

        if event:
            self.pyslipqt.ShowLayer(self.poly_layer)
            if self.sel_poly_layer:
                self.pyslipqt.ShowLayer(self.sel_poly_layer)
        else:
            self.pyslipqt.HideLayer(self.poly_layer)
            if self.sel_poly_layer:
                self.pyslipqt.HideLayer(self.sel_poly_layer)

    def polySelectOnOff(self, event):
        """Handle SelectOnOff event for polygon layer control."""

        layer = self.poly_layer
        if event:
            self.add_select_handler(layer, self.polySelect)
            self.pyslipqt.SetLayerSelectable(layer, True)
        else:
            self.del_select_handler(layer)
            self.pyslipqt.SetLayerSelectable(layer, False)

    def polySelect(self, event):
        """Map- and view-relative polygon select event from pyslipqt.

        event  the event that contains these attributes:
                   type       the type of point selection: single or box
                   selection  [list of] tuple (xgeo,ygeo) of selected point
                              (if None then no point(s) selected)

        The selection could be a single or box select.

        Select a polygon to turn it on, any other polygon selection turns
        it off, unless previous selection again selected.
        """

        # .seletion: [(poly,attr), ...]
        selection = event.selection

        # turn any previous selection off
        if self.sel_poly_layer:
            self.pyslipqt.DeleteLayer(self.sel_poly_layer)
            self.sel_poly_layer = None

        # box OR single selection
        if selection:
            # get selected polygon points into form for point display layer
            points = []
            for (poly, d) in selection:
                try:
                    del d['colour']
                except KeyError:
                    pass
                try:
                    del d['radius']
                except KeyError:
                    pass
                for (x, y) in poly:
                    points.append((x, y, d))

            self.sel_poly_layer = \
                self.pyslipqt.AddPointLayer(points, map_rel=True,
                                            colour='#ff00ff',
                                            radius=5, visible=True,
                                            show_levels=[3,4],
                                            name='<sel_poly>')

        return True

##### view-relative polygon layer

    def polyViewOnOff(self, event):
        """Handle OnOff event for map-relative polygon layer control."""

        if event:
            self.poly_view_layer = \
                self.pyslipqt.AddPolygonLayer(PolyViewData, map_rel=False,
                                              delta=DefaultPolygonViewDelta,
                                              name='<poly_view_layer>',
                                              placement='cn', visible=True,
                                              fontsize=24, colour='#0000ff')
        else:
            self.pyslipqt.DeleteLayer(self.poly_view_layer)
            self.poly_view_layer = None
            if self.sel_poly_view_layer:
                self.pyslipqt.DeleteLayer(self.sel_poly_view_layer)
                self.sel_poly_view_layer = None
                self.sel_poly_view_point = None

    def polyViewShowOnOff(self, event):
        """Handle ShowOnOff event for polygon layer control."""

        if event:
            self.pyslipqt.ShowLayer(self.poly_view_layer)
            if self.sel_poly_view_layer:
                self.pyslipqt.ShowLayer(self.sel_poly_view_layer)
        else:
            self.pyslipqt.HideLayer(self.poly_view_layer)
            if self.sel_poly_view_layer:
                self.pyslipqt.HideLayer(self.sel_poly_view_layer)

    def polyViewSelectOnOff(self, event):
        """Handle SelectOnOff event for polygon layer control."""

        layer = self.poly_view_layer
        if event:
            self.add_select_handler(layer, self.polyViewSelect)
            self.pyslipqt.SetLayerSelectable(layer, True)
        else:
            self.del_select_handler(layer)
            self.pyslipqt.SetLayerSelectable(layer, False)

    def polyViewSelect(self, event):
        """View-relative polygon select event from pyslipqt.

        event  the event that contains these attributes:
                   type       the type of point selection: single or box
                   selection  tuple (sel, udata, None) defining the selected
                              polygon (if None then no point(s) selected)

        The selection could be a single or box select.
        """

        selection = event.selection

        # point select, turn any previous selection off
        if self.sel_poly_view_layer:
            self.pyslipqt.DeleteLayer(self.sel_poly_view_layer)
            self.sel_poly_view_layer = None

        # for box OR single selection
        if selection:
            # get selected polygon points into form for point display layer
            points = []
            for (poly, d) in selection:
                try:
                    del d['colour']
                except KeyError:
                    pass
                try:
                    del d['radius']
                except KeyError:
                    pass
                for (x, y) in poly:
                    points.append((x, y, d))

            self.sel_poly_view_layer = \
                self.pyslipqt.AddPointLayer(points, map_rel=False,
                                            colour='#ff00ff',
                                            radius=5, visible=True,
                                            show_levels=[3,4],
                                            name='<sel_view_poly>')

        return True

##### map-relative polyline layer

    def polylineOnOff(self, event):
        """Handle OnOff event for map-relative polyline layer control."""

        if event:
            self.polyline_layer = \
                self.pyslipqt.AddPolylineLayer(PolylineData, map_rel=True,
                                               visible=True,
                                               delta=DefaultPolylineMapDelta,
                                               show_levels=MRPolyShowLevels,
                                               name='<polyline_layer>')
        else:
            self.pyslipqt.DeleteLayer(self.polyline_layer)
            self.polyline_layer = None
            if self.sel_polyline_layer:
                self.pyslipqt.DeleteLayer(self.sel_polyline_layer)
                self.sel_polyline_layer = None
                self.sel_polyline_point = None
            if self.sel_polyline_layer2:
                self.pyslipqt.DeleteLayer(self.sel_polyline_layer2)
                self.sel_polyline_layer2 = None

    def polylineShowOnOff(self, event):
        """Handle ShowOnOff event for polycwlinegon layer control."""

        if event:
            self.pyslipqt.ShowLayer(self.polyline_layer)
            if self.sel_polyline_layer:
                self.pyslipqt.ShowLayer(self.sel_polyline_layer)
            if self.sel_polyline_layer2:
                self.pyslipqt.ShowLayer(self.sel_polyline_layer2)
        else:
            self.pyslipqt.HideLayer(self.polyline_layer)
            if self.sel_polyline_layer:
                self.pyslipqt.HideLayer(self.sel_polyline_layer)
            if self.sel_polyline_layer2:
                self.pyslipqt.HideLayer(self.sel_polyline_layer2)

    def polylineSelectOnOff(self, event):
        """Handle SelectOnOff event for polyline layer control."""

        layer = self.polyline_layer
        if event:
            self.add_select_handler(layer, self.polylineSelect)
            self.pyslipqt.SetLayerSelectable(layer, True)
        else:
            self.del_select_handler(layer)
            self.pyslipqt.SetLayerSelectable(layer, False)

    def polylineSelect(self, event):
        """Map- and view-relative polyline select event from pyslipqt.

        event  the event that contains these attributes:
                   type       the type of point selection: single or box
                   selection  [list of] tuple (xgeo,ygeo) of selected point
                              (if None then no point(s) selected)
                   relsel     a tuple (p1,p2) of polyline segment

        The selection could be a single or box select.

        Select a polyline to turn it on, any other polyline selection turns
        it off, unless previous selection again selected.
        """

        # .seletion: [(poly,attr), ...]
        selection = event.selection
        relsel = event.relsel

        # turn any previous selection off
        if self.sel_polyline_layer:
            self.pyslipqt.DeleteLayer(self.sel_polyline_layer)
            self.sel_polyline_layer = None
        if self.sel_polyline_layer2:
            self.pyslipqt.DeleteLayer(self.sel_polyline_layer2)
            self.sel_polyline_layer2 = None

        # box OR single selection
        if selection:
            # show segment selected first, if any
            if relsel:
                self.sel_polyline_layer2 = \
                    self.pyslipqt.AddPointLayer(relsel, map_rel=True,
                                                colour='#40ff40',
                                                radius=5, visible=True,
                                                show_levels=[3,4],
                                                name='<sel_polyline2>')

            # get selected polygon points into form for point display layer
            points = []
            for (poly, d) in selection:
                try:
                    del d['colour']
                except KeyError:
                    pass
                try:
                    del d['radius']
                except KeyError:
                    pass
                for (x, y) in poly:
                    points.append((x, y, d))

            self.sel_polyline_layer = \
                self.pyslipqt.AddPointLayer(points, map_rel=True,
                                            colour='#ff00ff',
                                            radius=3, visible=True,
                                            show_levels=[3,4],
                                            name='<sel_polyline>')
        return True

##### view-relative polyline layer

    def polylineViewOnOff(self, event):
        """Handle OnOff event for map-relative polyline layer control."""

        if event:
            self.polyline_view_layer = \
                self.pyslipqt.AddPolylineLayer(PolylineViewData, map_rel=False,
                                               delta=DefaultPolylineViewDelta,
                                               name='<polyline_view_layer>',
                                               placement='cn', visible=True,
                                               fontsize=24, colour='#0000ff')
        else:
            self.pyslipqt.DeleteLayer(self.polyline_view_layer)
            self.polyline_view_layer = None
            if self.sel_polyline_view_layer:
                self.pyslipqt.DeleteLayer(self.sel_polyline_view_layer)
                self.sel_polyline_view_layer = None
                self.sel_polyline_view_point = None
            if self.sel_polyline_view_layer2:
                self.pyslipqt.DeleteLayer(self.sel_polyline_view_layer2)
                self.sel_polyline_view_layer2 = None

    def polylineViewShowOnOff(self, event):
        """Handle ShowOnOff event for polyline layer control."""

        if event:
            self.pyslipqt.ShowLayer(self.polyline_view_layer)
            if self.sel_polyline_view_layer:
                self.pyslipqt.ShowLayer(self.sel_polyline_view_layer)
            if self.sel_polyline_view_layer2:
                self.pyslipqt.ShowLayer(self.sel_polyline_view_layer2)
        else:
            self.pyslipqt.HideLayer(self.polyline_view_layer)
            if self.sel_polyline_view_layer:
                self.pyslipqt.HideLayer(self.sel_polyline_view_layer)
            if self.sel_polyline_view_layer2:
                self.pyslipqt.HideLayer(self.sel_polyline_view_layer2)

    def polylineViewSelectOnOff(self, event):
        """Handle SelectOnOff event for polyline layer control."""

        layer = self.polyline_view_layer
        if event:
            self.add_select_handler(layer, self.polylineViewSelect)
            self.pyslipqt.SetLayerSelectable(layer, True)
        else:
            self.del_select_handler(layer)
            self.pyslipqt.SetLayerSelectable(layer, False)

    def polylineViewSelect(self, event):
        """View-relative polyline select event from pyslipqt.

        event  the event that contains these attributes:
                   type       the type of point selection: single or box
                   selection  tuple (sel, udata, None) defining the selected
                              polyline (if None then no point(s) selected)

        The selection could be a single or box select.
        """

        selection = event.selection
        relsel = event.relsel

        # point select, turn any previous selection off
        if self.sel_polyline_view_layer:
            self.pyslipqt.DeleteLayer(self.sel_polyline_view_layer)
            self.sel_polyline_view_layer = None
        if self.sel_polyline_view_layer2:
            self.pyslipqt.DeleteLayer(self.sel_polyline_view_layer2)
            self.sel_polyline_view_layer2 = None

        # for box OR single selection
        if selection:
            # first, display selected segment
            if relsel:
                # get original polyline attributes, get placement and offsets
                (_, attributes) = PolylineViewData[0]
                place = attributes.get('placement', None)
                offset_x = attributes.get('offset_x', 0)
                offset_y = attributes.get('offset_y', 0)

                self.sel_polyline_view_layer2 = \
                    self.pyslipqt.AddPointLayer(relsel, map_rel=False,
                                                placement=place,
                                                offset_x=offset_x,
                                                offset_y=offset_y,
                                                colour='#4040ff',
                                                radius=5, visible=True,
                                                show_levels=[3,4],
                                                name='<sel_view_polyline2>')

            # get selected polyline points into form for point display layer
            points = []
            for (poly, d) in selection:
                try:
                    del d['colour']
                except KeyError:
                    pass
                try:
                    del d['radius']
                except KeyError:
                    pass
                for (x, y) in poly:
                    points.append((x, y, d))

            self.sel_polyline_view_layer = \
                self.pyslipqt.AddPointLayer(points, map_rel=False,
                                            colour='#ff00ff',
                                            radius=3, visible=True,
                                            show_levels=[3,4],
                                            name='<sel_view_polyline>')

        return True


    def level_change_event(self, etype, level):
        """Handle a "level change" event from the pySlipQt widget.
        
        etype  the type of event
        level  the new map level
        """

        log(f'level_change_event: got level change, etype={etype}, level={level}')
        self.map_level.set_text(str(level))

    def mouse_posn_event(self, etype, mposn, vposn):
        """Handle a "mouse position" event from the pySlipQt widget.
        
        etype  the type of event
        mposn  the new mouse position on the map (xgeo, ygeo)
        vposn  the new mouse position on the view (x, y)
        """

        if mposn:
            (lon, lat) = mposn
            self.mouse_position.set_text(f'{lon:.2f}/{lat:.2f}')
        else:
            self.mouse_position.set_text('')

    def select_event(self, etype, mposn, vposn, layer_id, selection, data, relsel):
        """Handle a single select click.

        etype      the event type number
        mposn      select point tuple in map (geo) coordinates: (xgeo, ygeo)
        vposn      select point tuple in view coordinates: (xview, yview)
        layer_id   the ID of the layer containing the selected object (or None)
        selection  a tuple (x,y,attrib) defining the position of the object selected (or [] if no selection)
        data       the user-supplied data object for the selected object (or [] if no selection)
        relsel     relative selection point inside a single selected image (or [] if no selection)
        """

        log(f'select_event: mposn={mposn}, vposn={vposn}, layer_id={layer_id}, selection={selection}, data={data}, relsel={relsel}')

    ######
    # Small utility routines
    ######

    def unimplemented(self, msg):
        """Issue an "Sorry, ..." message."""

        self.pyslipqt.warn('Sorry, %s is not implemented at the moment.' % msg)


    ######
    # Finish initialization of data, etc
    ######

    def init(self):
        global PointData, PointDataColour, PointViewDataPlacement
        global PointViewData, PointViewDataColour
        global ImageData
        global ImageViewData
        global TextData
        global TextViewData
        global TextViewDataPlace, TextViewDataOffX, TextViewDataOffY
        global PolyData, PolyViewData
        global PolylineData, PolylineViewData
        global CR_Width, CR_Height

        # create PointData
        PointData = []
        for lon in range(-70, 290+1, 5):
            for lat in range(-65, 65+1, 5):
                udata = 'point(%s,%s)' % (str(lon), str(lat))
                PointData.append((lon, lat, {'data': udata}))
        PointDataColour = '#ff000080'	# semi-transparent

        # create PointViewData - a point-rendition of 'PYSLIP'
# TODO: add the suffix 'Qt'
        PointViewData = [(-66,-14),(-66,-13),(-66,-12),(-66,-11),(-66,-10),
                         (-66,-9),(-66,-8),(-66,-7),(-66,-6),(-66,-5),(-66,-4),
                         (-66,-3),(-65,-7),(-64,-7),(-63,-7),(-62,-7),(-61,-8),
                         (-60,-9),(-60,-10),(-60,-11),(-60,-12),(-61,-13),
                         (-62,-14),(-63,-14),(-64,-14),(65,-14),            # P
                         (-59,-14),(-58,-13),(-57,-12),(-56,-11),(-55,-10),
                         (-53,-10),(-52,-11),(-51,-12),(-50,-13),(-49,-14),
                         (-54,-9),(-54,-8),(-54,-7),(-54,-6),(-54,-5),
                         (-54,-4),(-54,-3),                                 # Y
                         (-41,-13),(-42,-14),(-43,-14),(-44,-14),(-45,-14),
                         (-46,-14),(-47,-13),(-48,-12),(-48,-11),(-47,-10),
                         (-46,-9),(-45,-9),(-44,-9),(-43,-9),(-42,-8),
                         (-41,-7),(-41,-6),(-41,-5),(-42,-4),(-43,-3),
                         (-44,-3),(-45,-3),(-46,-3),(-47,-3),(-48,-4),      # S
                         (-39,-14),(-39,-13),(-39,-12),(-39,-11),(-39,-10),
                         (-39,-9),(-39,-8),(-39,-7),(-39,-6),(-39,-5),
                         (-39,-4),(-39,-3),(-38,-3),(-37,-3),(-36,-3),
                         (-35,-3),(-34,-3),(-33,-3),(-32,-3),               # L
                         (-29,-14),(-29,-13),(-29,-12),
                         (-29,-11),(-29,-10),(-29,-9),(-29,-8),(-29,-7),
                         (-29,-6),(-29,-5),(-29,-4),(-29,-3),               # I
                         (-26,-14),(-26,-13),(-26,-12),(-26,-11),(-26,-10),
                         (-26,-9),(-26,-8),(-26,-7),(-26,-6),(-26,-5),(-26,-4),
                         (-26,-3),(-25,-7),(-24,-7),(-23,-7),(-22,-7),(-21,-8),
                         (-20,-9),(-20,-10),(-20,-11),(-20,-12),(-21,-13),
                         (-22,-14),(-23,-14),(-24,-14),(25,-14)]            # P
        PointViewDataColour = '#00000040'	# transparent
        PointViewDataPlacement = 'se'

        # create image data - shipwrecks off the Australian east coast
        ImageData = [# Agnes Napier - 1855
                     (160.0, -30.0, ShipImg, {'placement': 'cc'}),
                     # Venus - 1826
                     (145.0, -11.0, ShipImg, {'placement': 'ne'}),
                     # Wolverine - 1879
                     (156.0, -23.0, ShipImg, {'placement': 'nw'}),
                     # Thomas Day - 1884
                     (150.0, -15.0, ShipImg, {'placement': 'sw'}),
                     # Sybil - 1902
                     (165.0, -19.0, ShipImg, {'placement': 'se'}),
                     # Prince of Denmark - 1863
                     (158.55, -19.98, ShipImg),
                     # Moltke - 1911
                     (146.867525, -19.152185, ShipImg)
                    ]
        ImageData2 = []
        ImageData3 = []
        ImageData4 = []
        ImageData5 = []
        ImageData6 = []
        self.map_level_2_img = {0: ImageData2,
                                1: ImageData3,
                                2: ImageData4,
                                3: ImageData5,
                                4: ImageData6}
        self.map_level_2_selimg = {0: SelGlassyImg2,
                                   1: SelGlassyImg3,
                                   2: SelGlassyImg4,
                                   3: SelGlassyImg5,
                                   4: SelGlassyImg6}
        self.current_layer_img_layer = None

        ImageViewData = [(0, 0, CompassRoseGraphic, {'placement': 'ne',
                                                     'data': 'compass rose'})]

        text_placement = {'placement': 'se'}
        transparent_placement = {'placement': 'se', 'colour': '#00000040'}
        capital = {'placement': 'se', 'fontsize': 14, 'colour': 'red',
                   'textcolour': 'red'}
        TextData = [(151.20, -33.85, 'Sydney', text_placement),
                    (144.95, -37.84, 'Melbourne', {'placement': 'ce'}),
                    (153.08, -27.48, 'Brisbane', text_placement),
                    (115.86, -31.96, 'Perth', transparent_placement),
                    (138.30, -35.52, 'Adelaide', text_placement),
                    (130.98, -12.61, 'Darwin', text_placement),
                    (147.31, -42.96, 'Hobart', text_placement),
                    (174.75, -36.80, 'Auckland', text_placement),
                    (174.75, -41.29, 'Wellington', capital),
                    (172.61, -43.51, 'Christchurch', text_placement),
                    (168.74, -45.01, 'Queenstown', text_placement),
                    (147.30, -09.41, 'Port Moresby', capital),
                    (106.822922, -6.185451, 'Jakarta', capital),
                    (110.364444, -7.801389, 'Yogyakarta', text_placement),
                    (120.966667, 14.563333, 'Manila', capital),
                    (271.74, +40.11, 'Champaign', text_placement),
                    (160.0, -30.0, 'Agnes Napier - 1855',
                        {'placement': 'cw', 'offset_x': 20, 'colour': 'green'}),
                    (145.0, -11.0, 'Venus - 1826',
                        {'placement': 'sw', 'colour': 'green'}),
                    (156.0, -23.0, 'Wolverine - 1879',
                        {'placement': 'ce', 'colour': 'green'}),
                    (150.0, -15.0, 'Thomas Day - 1884',
                        {'colour': 'green'}),
                    (165.0, -19.0, 'Sybil - 1902',
                        {'placement': 'cw', 'colour': 'green'}),
                    (158.55, -19.98, 'Prince of Denmark - 1863',
                        {'placement': 'nw', 'offset_x': 20, 'colour': 'green'}),
                    (146.867525, -19.152182, 'Moltke - 1911',
                        {'placement': 'ce', 'offset_x': 20, 'colour': 'green'})
                   ]
        if sys.platform != 'win32':
            TextData.extend([
                    (110.5, 24.783333, '阳朔县 (Yangshuo)', {'placement': 'sw'}),
                    (117.183333, 39.133333, '天津市 (Tianjin)', {'placement': 'sw'}),
                    (106.36, +10.36, 'Mỹ Tho', {'placement': 'ne'}),
                    (105.85, +21.033333, 'Hà Nội', capital),
                    (106.681944, 10.769444, 'Thành phố Hồ Chí Minh',
                        {'placement': 'sw'}),
                    (132.47, +34.44, '広島市 (Hiroshima City)',
                        text_placement),
                    (114.158889, +22.278333, '香港 (Hong Kong)',
                        {'placement': 'nw'}),
                    (98.392, 7.888, 'ภูเก็ต (Phuket)', text_placement),
                    ( 96.16, +16.80, 'ရန်ကုန် (Yangon)', capital),
                    (104.93, +11.54, ' ភ្នំពេញ (Phnom Penh)',
                        {'placement': 'ce', 'fontsize': 12, 'colour': 'red'}),
                    (100.49, +13.75, 'กรุงเทพมหานคร (Bangkok)', capital),
                    ( 77.56, +34.09, 'གླེ་(Leh)', text_placement),
                    (84.991275, 24.695102, 'बोधगया (Bodh Gaya)', text_placement)])

        TextViewData = [(0, 0, '%s %s' % (DemoName, DemoVersion))]
        TextViewDataPlace = 'cn'
        TextViewDataOffX = 0
        TextViewDataOffY = 3

        PolyData = [(((150.0,10.0),(160.0,20.0),(170.0,10.0),(165.0,0.0),(155.0,0.0)),
                      {'width': 3, 'colour': 'blue', 'closed': True}),
                    (((165.0,-35.0),(175.0,-35.0),(175.0,-45.0),(165.0,-45.0)),
                      {'width': 10, 'colour': '#00ff00c0', 'filled': True,
                       'fillcolour': '#ffff0040'}),
                    (((190.0,-30.0),(220.0,-50.0),(220.0,-30.0),(190.0,-50.0)),
                      {'width': 3, 'colour': 'green', 'filled': True,
                       'fillcolour': 'yellow'}),
                    (((190.0,+50.0),(220.0,+65.0),(220.0,+50.0),(190.0,+65.0)),
                      {'width': 10, 'colour': '#00000040'})]

        PolyViewData = [(((230,0),(230,40),(-230,40),(-230,0)),
                        {'width': 3, 'colour': '#00ff00ff', 'closed': True,
                         'placement': 'cn', 'offset_y': 1})]

        PolylineData = [(((150.0,10.0),(160.0,20.0),(170.0,10.0),(165.0,0.0),(155.0,0.0)),
                          {'width': 3, 'colour': 'blue'})]

        PolylineViewData = [(((50,100),(100,50),(150,100),(100,150)),
                            {'width': 3, 'colour': '#00ffffff', 'placement': 'cn'})]

        # define layer ID variables & sub-checkbox state variables
        self.point_layer = None
        self.sel_point_layer = None
        self.sel_point = None

        self.point_view_layer = None
        self.sel_point_view_layer = None
        self.sel_point_view = None

        self.image_layer = None
        self.sel_image_layer = None
        self.sel_image = None

        self.image_view_layer = None
        self.sel_image_view_layer = None
        self.sel_image_view = None
        self.sel_imagepoint_view_layer = None

        self.text_layer = None
        self.sel_text_layer = None
        self.sel_text = None

        self.text_view_layer = None
        self.sel_text_view_layer = None

        self.poly_layer = None
        self.sel_poly_layer = None
        self.sel_poly = None

        self.poly_view_layer = None
        self.sel_poly_view_layer = None
        self.sel_poly = None

        self.polyline_layer = None
        self.sel_polyline_layer = None
        self.sel_polyline_layer2 = None
        self.sel_polyline = None

        self.polyline_view_layer = None
        self.sel_polyline_view_layer = None
        self.sel_polyline_view_layer2 = None
        self.sel_polyline = None

        # get width and height of the compass rose image
        cr_img = QPixmap(CompassRoseGraphic)
        size = cr_img.size()
        CR_Height = size.height()
        CR_Width = size.width()

        # set initial view position
        log(f'InitViewLevel={InitViewLevel}')
        self.map_level.set_text('%d' % InitViewLevel)

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

    def handle_select_event(self, event):
        """Handle a pySlip point/box SELECT event."""

        layer_id = event.layer_id

        self.demo_select_dispatch.get(layer_id, self.null_handler)(event)

    def null_handler(self, event):
        """Routine to handle unexpected events."""

        print('ERROR: null_handler!?')

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

        self.map_level.SetValue('%d' % event.level)

    ######
    # Handle adding/removing select handler functions.
    ######

    def add_select_handler(self, id, handler):
        """Add handler for select in layer 'id'."""

        self.demo_select_dispatch[id] = handler

    def del_select_handler(self, id):
        """Remove handler for select in layer 'id'."""

        del self.demo_select_dispatch[id]

    ######
    # Warning and information dialogs
    ######
    def info(self, msg):
        """Display an information message, log and graphically."""

        log_msg = '# ' + msg
        length = len(log_msg)
        prefix = '#### Information '
        banner = prefix + '#'*(80 - len(log_msg) - len(prefix))
        log(banner)
        log(log_msg)
        log(banner)

        info_dialog = QErrorMessage(self)
        info_dialog.showMessage(msg)


    def warn(self, msg):
        """Display a warning message, log and graphically."""

        log_msg = '# ' + msg
        length = len(log_msg)
        prefix = '#### Warning '
        banner = prefix + '#'*(80 - len(log_msg) - len(prefix))
        log(banner)
        log(log_msg)
        log(banner)

        warn_dialog = QErrorMessage(self)
        warn_dialog.showMessage(msg)

###############################################################################

if __name__ == '__main__':
    import sys
    import getopt
    import traceback

    def usage(msg=None):
        if msg:
            print(('*'*80 + '\n%s\n' + '*'*80) % msg)
        print(__doc__)

    # our own handler for uncaught exceptions
    def excepthook(type, value, tb):
        msg = '\n' + '=' * 80
        msg += '\nUncaught exception:\n'
        msg += ''.join(traceback.format_exception(type, value, tb))
        msg += '=' * 80 + '\n'
        log(msg)
        print(msg)
        tkinter_error(msg)
        sys.exit(1)

    # plug our handler into the python system
    sys.excepthook = excepthook

    # parse the CLI params
    argv = sys.argv[1:]

    try:
        (opts, args) = getopt.getopt(argv, 'd:h', ['debug=', 'help'])
    except getopt.error:
        usage()
        sys.exit(1)

    debug = 10              # no logging

    for (opt, param) in opts:
        if opt in ['-d', '--debug']:
            debug = param
        elif opt in ['-h', '--help']:
            usage()
            sys.exit(0)

    # convert any symbolic debug level to a number
    try:
        debug = int(debug)
    except ValueError:
        # possibly a symbolic debug name
        try:
            debug = LogSym2Num[debug.upper()]
        except KeyError:
            usage('Unrecognized debug name: %s' % debug)
            sys.exit(1)
    log.set_level(debug)

    # start wxPython app
    app = QApplication(args)
    ex = PySlipQtDemo()
    sys.exit(app.exec_())

