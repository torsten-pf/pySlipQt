"""
Program to test image map-relative and view-relative placement.
Select which to show and experiment with placement parameters.

Usage: test_image_placement.py [-h|--help] [-d] [(-t|--tiles) (GMT|OSM)]
"""


import os
import sys
import getopt
import traceback

import tkinter_error

try:
    from PyQt5.QtCore import QTimer
    from PyQt5.QtGui import QPixmap
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                                 QAction, QGridLayout, QErrorMessage, QGroupBox)
except ImportError:
    msg = '*'*60 + '\nSorry, you must install PyQt5\n' + '*'*60
    print(msg)
    tkinter_error(msg)
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

    def __init__(self, parent, title):
        """Initialise a ImagePlacementControl instance.

        parent  reference to parent object
        title   title to give the custom widget
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

        # start the layout
        group = QGroupBox(title)

        grid = QGridLayout()
        grid.setContentsMargins(2, 2, 2, 2)

        # start layout
        row = 1
        label = QLabel('filename:')
        label.setAlignment(Qt.AlignRight)
        grid.addWidget(label, row, 0)
        grid.addWidget(self.filename, row, 1, 1, 3)

        row += 1
        label = QLabel('placement:')
        label.setAlignment(Qt.AlignRight)
        grid.addWidget(label, row, 0)
        grid.addWidget(self.placement, row, 1)

        row += 1
        label = QLabel('point radius:')
        label.setAlignment(Qt.AlignRight)
        grid.addWidget(label, row, 0)
        grid.addWidget(self.point_radius, row, 1)
        label = QLabel('point colour:')
        label.setAlignment(Qt.AlignRight)
        grid.addWidget(label, row, 2)
        grid.addWidget(self.point_colour, row, 3)

        row += 1
        label = QLabel('X:')
        label.setAlignment(Qt.AlignRight)
        grid.addWidget(label, row, 0)
        grid.addWidget(self.posn_x, row, 1)
        label = QLabel('Y:')
        label.setAlignment(Qt.AlignRight)
        grid.addWidget(label, row, 2)
        grid.addWidget(self.posn_y, row, 3)

        row += 1
        label = QLabel('X offset:')
        label.setAlignment(Qt.AlignRight)
        grid.addWidget(label, row, 0)
        grid.addWidget(self.offset_x, row, 1)
        label = QLabel('Y offset:')
        label.setAlignment(Qt.AlignRight)
        grid.addWidget(label, row, 2)
        grid.addWidget(self.offset_y, row, 3)

        row += 1
        grid.addWidget(btn_remove, row, 1)
        grid.addWidget(btn_update, row, 3)

        group.setLayout(grid)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(1, 1, 1, 1)
        hbox.addWidget(group)

        self.setLayout(hbox)

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

        grid = QGridLayout()
        grid.setColumnStretch(0, 1)
        grid.setContentsMargins(2, 2, 2, 2)

        qwidget = QWidget(self)
        qwidget.setLayout(grid)
        self.setCentralWidget(qwidget)

########

        # build the GUI
#        layout = self.make_gui(self)
        grid = QGridLayout()
        grid.setContentsMargins(2, 2, 2, 2)

        # make all widgets
        self.pyslipqt = pySlipQt.PySlipQt(self, tile_src=self.tile_source, start_level=0)
        self.map_image = ImagePlacementControl(self, 'Map-relative image')
        self.view_image = ImagePlacementControl(self, 'View-relative image')

        # start the layout
        grid.addWidget(self.pyslipqt, 0, 0)

        vbox = QVBoxLayout()
        vbox.addWidget(self.map_image)
        vbox.addWidget(self.view_image)
        vbox.addStretch(1)

        grid.addLayout(vbox, 0, 1)

        self.setLayout(vbox)

        # tie events from controls to handlers
        self.map_image.remove.connect(self.remove_image_map)
        self.map_image.change.connect(self.change_image_map)

        self.view_image.remove.connect(self.remove_image_view)
        self.view_image.change.connect(self.change_image_view)

        # set window title
        self.setWindowTitle('%s %s' % (DemoName, DemoVersion))
        self.show()

    def make_gui(self, parent):
        """Create application GUI."""

        grid = QGridLayout()
        grid.setContentsMargins(2, 2, 2, 2)

        # make all widgets
        self.pyslipqt = pySlipQt.PySlipQt(parent, tile_src=self.tile_source, start_level=0)
        self.map_image = ImagePlacementControl(self, 'Map-relative image')
        self.view_image = ImagePlacementControl(self, 'View-relative image')

        # start the layout
        grid.addWidget(self.pyslipqt, 0, 0)

        vbox = QVBoxLayout()
        vbox.addWidget(self.map_image)
        vbox.addWidget(self.view_image)
        vbox.addStretch(1)

        grid.addLayout(vbox, 0, 1)

        return vbox

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

ProgramFile = __file__
ProgramPath = os.getcwd()
print(f'ProgramFile={ProgramFile}')
print(f'ProgramPath={ProgramPath}')

# start the app
app = QApplication(sys.argv)
ex = TestImagePlacement(tile_dir)
sys.exit(app.exec())

