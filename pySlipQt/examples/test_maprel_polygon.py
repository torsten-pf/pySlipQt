"""Test PySlipQt map-relative polygons.

Usage: test_maprel_poly.py [-h] [-t (OSM|GMT)]
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
# Various demo constants
######

# demo name/version
DemoVersion = '1.0'
DemoName = f'Test map-relative polygon placement {DemoVersion} (pySlipQt {pySlipQt.__version__})'

DemoHeight = 800
DemoWidth = 1000

MinTileLevel = 0
InitViewLevel = 2
InitViewPosition = (152.0, -8.0)

# create polygon data
OpenPoly = ((145,5),(135,5),(135,-5),(145,-5))
ClosedPoly = ((170,5),(160,5),(160,-5),(170,-5))
FilledPoly = ((170,-20),(160,-20),(160,-10),(170,-10))
ClosedFilledPoly = ((145,-20),(135,-20),(135,-10),(145,-10))

PolyMapData = [[OpenPoly, {'width': 2}],
               [ClosedPoly, {'width': 10, 'color': '#00ff0040',
                             'closed': True}],
               [FilledPoly, {'colour': 'blue',
                             'filled': True,
                             'fillcolour': '#00ff0022'}],
               [ClosedFilledPoly, {'colour': 'black',
                                   'closed': True,
                                   'filled': True,
                                   'fillcolour': 'yellow'}]]

TextMapData = [(135, 5, 'open (polygons always closed in pSlipQt)', {'placement': 'ce', 'radius': 0}),
               (170, 5, 'closed', {'placement': 'cw', 'radius': 0}),
               (170, -10, 'open but filled (translucent) (polygons always closed in pSlipQt)',
                   {'placement': 'cw', 'radius': 0}),
               (135, -10, 'closed & filled (solid)',
                   {'placement': 'ce', 'radius': 0}),
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
        self.poly_layer = self.pyslipqt.AddPolygonLayer(PolyMapData,
                                                        map_rel=True,
                                                        name='<poly_map_layer>')
        self.text_layer = self.pyslipqt.AddTextLayer(TextMapData, map_rel=True,
                                                     name='<text_map_layer>')

        self.show()

        # finally, set initial view position
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

# plug our handler into the python system
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

# start wxPython app
log(DemoName)
tile_dir = 'test_maprel_polygon.tiles'
app = QApplication(args)
ex = TestFrame(tile_dir)
sys.exit(app.exec_())
