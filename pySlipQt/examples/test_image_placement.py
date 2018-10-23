"""
Program to test image map-relative and view-relative placement.
Select which to show and experiment with placement parameters.

Usage: test_image_placement.py [-h|--help] [-d] [(-t|--tiles) (GMT|OSM)]
"""


import os
import sys
import getopt
import traceback

try:
    from PyQt5.QtCore import QTimer
    from PyQt5.QtGui import QPixmap
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget,
                                 QAction, QGridLayout, QErrorMessage)
    from pySlipQt.tkinter_error import tkinter_error
except ImportError:
    msg = '*'*60 + '\nSorry, you must install PyQt5\n' + '*'*60
    print(msg)
    sys.exit(1)

try:
    import pySlipQt.pySlipQt as pySlipQt
    import pySlipQt.log as log
except ImportError:
    msg = '*'*60 + '\nSorry, you must install pySlipQt\n' + '*'*60
    print(msg)
    tkinter_error(msg)
    sys.exit(1)

######
# Various demo constants
######

# demo name/version
DemoName = 'Test image placement, pySlipQt %s' % pySlipQt.__version__
DemoVersion = '1.0'

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


##################################
# Custom ImagePlacementControl widget.
# 
# Constructor:
# 
#     ipc = ImagePlacementControl(parent)
# 
# Events:
# 
#     .change   the contents were changed
#     .remove   the image should be removed
#
# The '.change' event has attached attributes holding the values from the
# widget, all checked so they are 'sane'.
##################################

class ImagePlacementControl(QWidget):

    # set platform dependant values
    if platform.system() == 'Linux':
        pass
    elif platform.system() == 'Darwin':
        pass
    elif platform.system() == 'Windows':
        pass
    else:
        raise Exception('Unrecognized platform: %s' % platform.system())

    # signals raised by this widget
    change = pyqtSignal(str, str, int, QColor, int, int, int, int)
    remove = pyqtSignal()

    def __init__(self, parent):
        """Initialise a ImagePlacementControl instance.

        parent      reference to parent object
        """

        QWidget.__init__(self)

        # create all widgets used in this custom widget
        self.filename = QLabel('/file/name')
        self.filename.setToolTip('Click here to change the image file')
        self.placement = QComboBox()
        for p in ['none', 'nw', 'cn', 'ne', 'ce', 'se', 'cs', 'sw', 'cw', 'cc']:
            self.placement.addItem(p)
        self.point_radius = QLineEdit('2')
        self.point_colour = QPushButton('')
        self.posn_x = QLineEdit('0')
        self.posn_y = QLineEdit('0')
        self.offset_x = QLineEdit('0')
        self.offset_y = QLineEdit('0')
        btn_remove = QPushButton('Remove')
        btn_update = QPushButton('Update')

        # start layout
        grid = QGridLayout()
        grid.setContentsMargins(5, 5, 5, 5)
        self.setLayout(grid)

        label = QLabel('filename:')
        label.setAlignment(Qt.AlignRight)
        grid.addWidget(label, 0, 0)
        grid.addWidget(self.filename, 0, 1, 1, 3)

        label = QLabel('placement:')
        label.setAlignment(Qt.AlignRight)
        grid.addWidget(label, 1, 0)
        grid.addWidget(self.placement, 1, 1)

        label = QLabel('point radius:')
        label.setAlignment(Qt.AlignRight)
        grid.addWidget(label, 2, 0)
        grid.addWidget(self.point_radius, 2, 1)
        label = QLabel('point colour:')
        label.setAlignment(Qt.AlignRight)
        grid.addWidget(label, 2, 2)
        grid.addWidget(self.point_colour, 2, 3)

        label = QLabel('X:')
        label.setAlignment(Qt.AlignRight)
        grid.addWidget(label, 3, 0)
        grid.addWidget(self.posn_x, 3, 1)
        label = QLabel('Y:')
        label.setAlignment(Qt.AlignRight)
        grid.addWidget(label, 3, 2)
        grid.addWidget(self.posn_y, 3, 3)

        label = QLabel('X offset:')
        label.setAlignment(Qt.AlignRight)
        grid.addWidget(label, 4, 0)
        grid.addWidget(self.offset_x, 4, 1)

        label = QLabel('Y offset:')
        label.setAlignment(Qt.AlignRight)
        grid.addWidget(label, 4, 2)
        grid.addWidget(self.offset_y, 4, 3)

        grid.addWidget(btn_remove, 5, 1)
        grid.addWidget(btn_update, 5, 3)

        # connect internal widget events to handlers
        self.filename.mouseReleaseEvent = self.changeGraphicsFile
        self.point_colour.clicked.connect(self.changePointColour)
        btn_remove.clicked.connect(self.removeImage)
        btn_update.clicked.connect(self.updateData)

        self.show()

    def changeGraphicsFile(self, event):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_types = "PNG (*.png);;JPG (*.jpg)"
        (filename, _) = QFileDialog.getOpenFileName(self,"Open image file", "",
                                                    file_types,
                                                    options=options)
        if filename:
            # if filepath is relative to working directory, just get relative path
            if filename.startswith(ProgramPath):
                filename = filename[len(ProgramPath)+1:]
            self.filename.setText(filename)

    def changePointColour(self, event):
        color = QColorDialog.getColor()
        if color.isValid():
            colour = color.name()
            print(f'colour={colour}')
            # set colour button background
            self.point_colour.setStyleSheet(f'background-color:{colour};');
 
    def removeImage(self, event):
        self.remove.emit()

    def updateData(self, event):
        filepath = self.filename.text()
        placement = str(self.placement.currentText())
        if placement == 'none':
            placement = None
        radius = int(self.point_radius.text())
        colour = self.point_colour.palette().color(1)
        print(f'colour={colour}')
        x = int(self.posn_x.text())
        y = int(self.posn_y.text())
        offset_x = int(self.offset_x.text())
        offset_y = int(self.offset_y.text())
        
        self.change.emit(filepath, placement, radius, colour, x, y, offset_x, offset_y)

##############################

class ImagePlacementControlExample(QWidget):
    """Application to demonstrate the pySlipQt 'ImagePlacementControl' widget."""

    def __init__(self):
        super().__init__()

        self.lc_group = ImagePlacementControl(self)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(self.lc_group)
        self.setLayout(hbox)

        self.setWindowTitle('ImagePlacementControl widget')
        self.show()

        # connect the widget to '.changed' event handler
        self.lc_group.remove.connect(self.remove_image)
        self.lc_group.change.connect(self.change_image)

    def remove_image(self):
        print('Removing image')

    def change_image(self, filepath, placement, radius, colour,
                           x, y, offset_x, offset_y):
        print(f'change_image: filepath={filepath}, placement={placement}, '
              f'radius={radius}, colour={colour}, x={x}, y={y}, '
              f'offset_x={offset_x}, offset_y={offset_y}')

    def layer_select(self, select):
        print(f'Layer SELECT={select}')

################################################################################
# The main application frame
################################################################################

class AppFrame(wx.Frame):
    def __init__(self, tile_dir=TileDirectory, levels=None):
        wx.Frame.__init__(self, None, size=DefaultAppSize,
                          title='%s, test version %s' % (DemoName, DemoVersion))
        self.SetMinSize(DefaultAppSize)
        self.panel = wx.Panel(self, wx.ID_ANY)
        self.panel.SetBackgroundColour(wx.WHITE)
        self.panel.ClearBackground()

        self.tile_directory = tile_dir
        self.tile_source = Tiles.Tiles()

        # build the GUI
        self.make_gui(self.panel)

        # set initial view position
        self.map_level.SetLabel('%d' % InitialViewLevel)
        wx.CallAfter(self.final_setup, InitialViewLevel, InitialViewPosition)

        # force pyslipqt initialisation
        self.pyslipqt.OnSize()

        # finally, set up application window position
        self.Centre()

        # initialise state variables
        self.image_layer = None
        self.image_view_layer = None

        # finally, bind pySlipQt events to handlers
        self.pyslipqt.Bind(pyslipqt.EVT_PYSLIPQT_POSITION, self.handle_position_event)
        self.pyslipqt.Bind(pyslipqt.EVT_PYSLIPQT_LEVEL, self.handle_level_change)

#####
# Build the GUI
#####

    def make_gui(self, parent):
        """Create application GUI."""

        # start application layout
        all_display = wx.BoxSizer(wx.HORIZONTAL)
        parent.SetSizer(all_display)

        # put map view in left of horizontal box
        sl_box = self.make_gui_view(parent)
        all_display.Add(sl_box, proportion=1, border=0, flag=wx.EXPAND)

        # small spacer here - separate view and controls
        all_display.AddSpacer(HSpacerSize)

        # add controls to right of spacer
        controls = self.make_gui_controls(parent)
        all_display.Add(controls, proportion=0, border=0)

        parent.SetSizerAndFit(all_display)

    def make_gui_view(self, parent):
        """Build the map view widget

        parent  reference to the widget parent

        Returns the static box sizer.
        """

        # create gui objects
        sb = AppStaticBox(parent, '')
        self.pyslipqt = pyslipqt.PySlipQt(parent, tile_src=self.tile_source)

        # lay out objects
        box = wx.StaticBoxSizer(sb, orient=wx.HORIZONTAL)
        box.Add(self.pyslipqt, proportion=1, border=0, flag=wx.EXPAND)

        return box

    def make_gui_controls(self, parent):
        """Build the 'controls' part of the GUI

        parent  reference to parent

        Returns reference to containing sizer object.
        """

        # all controls in vertical box sizer
        controls = wx.BoxSizer(wx.VERTICAL)

        # add the map level in use widget
        level = self.make_gui_level(parent)
        controls.Add(level, proportion=0, flag=wx.EXPAND|wx.ALL)

        # vertical spacer
        controls.AddSpacer(VSpacerSize)

        # add the mouse position feedback stuff
        mouse = self.make_gui_mouse(parent)
        controls.Add(mouse, proportion=0, flag=wx.EXPAND|wx.ALL)

        # vertical spacer
        controls.AddSpacer(VSpacerSize)

        # controls for map-relative image layer
        self.image = self.make_gui_image(parent)
        controls.Add(self.image, proportion=0, flag=wx.EXPAND|wx.ALL)
        self.image.Bind(EVT_DELETE, self.imageDelete)
        self.image.Bind(EVT_UPDATE, self.imageUpdate)

        # vertical spacer
        controls.AddSpacer(VSpacerSize)

        # controls for image-relative image layer
        self.image_view = self.make_gui_image_view(parent)
        controls.Add(self.image_view, proportion=0, flag=wx.EXPAND|wx.ALL)
        self.image_view.Bind(EVT_DELETE, self.imageViewDelete)
        self.image_view.Bind(EVT_UPDATE, self.imageViewUpdate)

        # vertical spacer
        controls.AddSpacer(VSpacerSize)

        return controls

    def make_gui_level(self, parent):
        """Build the control that shows the level.

        parent  reference to parent

        Returns reference to containing sizer object.
        """

        # create objects
        txt = wx.StaticText(parent, wx.ID_ANY, 'Level: ')
        self.map_level = wx.StaticText(parent, wx.ID_ANY, ' ')

        # lay out the controls
        sb = AppStaticBox(parent, 'Map level')
        box = wx.StaticBoxSizer(sb, orient=wx.HORIZONTAL)
        box.Add(txt, border=PackBorder, flag=(wx.ALIGN_CENTER_VERTICAL
                                     |wx.ALIGN_RIGHT|wx.LEFT))
        box.Add(self.map_level, proportion=0, border=PackBorder,
                flag=wx.RIGHT|wx.TOP)

        return box

    def make_gui_mouse(self, parent):
        """Build the mouse part of the controls part of GUI.

        parent  reference to parent

        Returns reference to containing sizer object.
        """

        # create objects
        txt = wx.StaticText(parent, wx.ID_ANY, 'Lon/Lat: ')
        self.mouse_position = ROTextCtrl(parent, '', size=(150,-1),
                                         tooltip=('Shows the mouse '
                                                  'longitude and latitude '
                                                  'on the map'))

        # lay out the controls
        sb = AppStaticBox(parent, 'Mouse position')
        box = wx.StaticBoxSizer(sb, orient=wx.HORIZONTAL)
        box.Add(txt, border=PackBorder, flag=(wx.ALIGN_CENTER_VERTICAL
                                     |wx.ALIGN_RIGHT|wx.LEFT))
        box.Add(self.mouse_position, proportion=1, border=PackBorder,
                flag=wx.RIGHT|wx.TOP|wx.BOTTOM)

        return box

    def make_gui_image(self, parent):
        """Build the image part of the controls part of GUI.

        parent  reference to parent

        Returns reference to containing sizer object.
        """

        # create widgets
        image_obj = LayerControl(parent, 'Image, map-relative',
                                 filename=DefaultFilename,
                                 placement=DefaultPlacement,
                                 x=DefaultX, y=DefaultY,
                                 offset_x=DefaultOffsetX,
                                 offset_y=DefaultOffsetY)

        return image_obj

    def make_gui_image_view(self, parent):
        """Build the view-relative image part of the controls part of GUI.

        parent  reference to parent

        Returns reference to containing sizer object.
        """

        # create widgets
        image_obj = LayerControl(parent, 'Image, view-relative',
                                 filename=DefaultViewFilename,
                                 placement=DefaultViewPlacement,
                                 x=DefaultViewX, y=DefaultViewY,
                                 offset_x=DefaultViewOffsetX,
                                 offset_y=DefaultViewOffsetY)

        return image_obj

    ######
    # event handlers
    ######

##### map-relative image layer

    def imageUpdate(self, event):
        """Display updated image."""

        # remove any previous layer
        if self.image_layer:
            self.pyslipqt.DeleteLayer(self.image_layer)

        # convert values to sanity for layer attributes
        image = event.filename

        placement = event.placement
        if placement == 'none':
            placement= ''

        x = event.x
        if not x:
            x = 0
        try:
            x = float(x)
        except ValueError:
            x = 0.0

        y = event.y
        if not y:
            y = 0
        try:
            y = float(y)
        except ValueError:
            y = 0.0

        off_x = event.offset_x
        if not off_x:
            off_x = 0
        try:
            off_x = int(off_x)
        except ValueError:
            off_x = 0

        off_y = event.offset_y
        if not off_y:
            off_y = 0
        try:
            off_y = int(off_y)
        except ValueError:
            off_y = 0

        radius = event.radius
        colour = event.colour

        image_data = [(x, y, image, {'placement': placement,
                                     'radius': radius,
                                     'colour': colour,
                                     'offset_x': off_x,
                                     'offset_y': off_y})]
        self.image_layer = self.pyslipqt.AddImageLayer(image_data, map_rel=True,
                                                       visible=True,
                                                       name='<image_layer>')

    def imageDelete(self, event):
        """Delete the image map-relative layer."""

        if self.image_layer:
            self.pyslipqt.DeleteLayer(self.image_layer)
        self.image_layer = None

##### view-relative image layer

    def imageViewUpdate(self, event):
        """Display updated image."""

        if self.image_view_layer:
            self.pyslip.DeleteLayer(self.image_view_layer)

        # convert values to sanity for layer attributes
        image = event.filename
        placement = event.placement
        if placement == 'none':
            placement= ''

        x = event.x
        if not x:
            x = 0
        x = int(x)

        y = event.y
        if not y:
            y = 0
        y = int(y)

        off_x = event.offset_x
        if not off_x:
            off_x = 0
        off_x = int(off_x)

        off_y = event.offset_y
        if not off_y:
            off_y = 0
        off_y = int(off_y)

        radius = event.radius
        colour = event.colour

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

    def imageViewDelete(self, event):
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
    tkinter_error.tkinter_error(msg)
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

ProgramFile = __file__
ProgramPath = os.getcwd()
print(f'ProgramFile={ProgramFile}')
print(f'ProgramPath={ProgramPath}')

# start the app
app = QApplication(sys.argv)
ex = ImagePlacementControlExample()
sys.exit(app.exec())

