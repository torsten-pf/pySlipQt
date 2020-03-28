"""Test PySlipQt map-relative images.

Usage: test_maprel_image.py [-h] [-t (OSM|GMT)]
"""

import sys
import getopt
import traceback

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout

import pySlipQt.pySlipQt as pySlipQt
from display_text import DisplayText
from layer_control import LayerControl
from image_placement import ImagePlacementControl

# initialize the logging system
import pySlipQt.log as log
log = log.Log('pyslipqt.log')


######
# Various constants
######

# demo name/version
DemoVersion = '1.0'
DemoName = f'Test map-relative image placement {DemoVersion} (pySlipQt {pySlipQt.__version__})'

DemoHeight = 800
DemoWidth = 1000

MinTileLevel = 0
InitViewLevel = 3
InitViewPosition = (158.0, -20.0)

arrow = 'graphics/arrow_right.png'

ImageMapData = [(158, -17, arrow, {'offset_x': 0, 'offset_y': 0}),
                (158, -18, arrow, {'offset_x': 0, 'offset_y': 0}),
                (158, -19, arrow, {'offset_x': 0, 'offset_y': 0}),
                (158, -20, arrow, {'offset_x': 0, 'offset_y': 0}),
                (158, -21, arrow, {'offset_x': 0, 'offset_y': 0}),
                (158, -22, arrow, {'offset_x': 0, 'offset_y': 0}),
                (158, -23, arrow, {'offset_x': 0, 'offset_y': 0})
               ]

PolygonMapData = [(((158,-17),(158,-23)),
                      {'width': 1, 'colour': 'black', 'filled': False})
                 ]

################################################################################
# The main application frame
################################################################################

class TestFrame(QMainWindow):

    def __init__(self, tile_dir):
        super().__init__()

        self.tile_directory = tile_dir
        self.tile_source = Tiles.Tiles()

        # build the GUI
        hbox = QHBoxLayout()

        qwidget = QWidget(self)
        qwidget.setLayout(hbox)
        self.setCentralWidget(qwidget)

        self.pyslipqt = pySlipQt.PySlipQt(self, tile_src=self.tile_source,
                                          start_level=MinTileLevel)
        hbox.addWidget(self.pyslipqt)

        # set the size of the demo window, etc
        self.setGeometry(100, 100, DemoWidth, DemoHeight)
        self.setWindowTitle(DemoName)

        # add test layers
        self.poly_layer = self.pyslipqt.AddPolygonLayer(PolygonMapData)
        self.image_layer = self.pyslipqt.AddImageLayer(ImageMapData,
                                                     map_rel=True,
                                                     placement='ce',
                                                     name='<image_map_layer>')

        self.show()

        # set initial view position
        self.pyslipqt.GotoLevelAndPosition(InitViewLevel, InitViewPosition)

################################################################################

# print some usage information
def usage(msg=None):
    if msg:
        print(msg+'\n')
    print(__doc__)        # module docstring used

# our own handler for uncaught exceptions
def excepthook(type, value, tb):
    msg = '\n' + '=' * 80
    msg += '\nUncaught exception:\n'
    msg += ''.join(traceback.format_exception(type, value, tb))
    msg += '=' * 80 + '\n'
    print(msg)
    sys.exit(1)
sys.excepthook = excepthook

# decide which tiles to use, default is GMT
argv = sys.argv[1:]

try:
    (opts, args) = getopt.getopt(argv, 'ht:', ['help', 'tiles='])
except getopt.error:
    usage()
    sys.exit(1)

tile_source = 'GMT'
for (opt, param) in opts:
    if opt in ['-h', '--help']:
        usage()
        sys.exit(0)
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
log(DemoName)
tile_dir = 'test_maprel_tiles'
app = QApplication(args)
ex = TestFrame(tile_dir)
sys.exit(app.exec_())
