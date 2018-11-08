"""
Test PySlipQt view-relative images.

Usage: test_maprel_image.py [-h] [-t (OSM|GMT)]
"""

import sys
import getopt
import traceback

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout

# initialize the logging system
import pySlipQt.log as log
log = log.Log('pyslipqt.log')

import pySlipQt.pySlipQt as pySlipQt
from display_text import DisplayText
from layer_control import LayerControl
from image_placement import ImagePlacementControl


######
# Various demo constants
######

# demo name/version
DemoVersion = '1.0'
DemoName = f'Test view-relative image placement {DemoVersion} (pySlipQt {pySlipQt.__version__})'

DemoHeight = 800
DemoWidth = 1000

MinTileLevel = 0
InitViewLevel = 2
InitViewPosition = (133.87, -23.7)      # Alice Springs

# test data
arrow_cw = 'graphics/arrow_left.png'
arrow_nw = 'graphics/arrow_leftup.png'
arrow_cn = 'graphics/arrow_up.png'
arrow_ne = 'graphics/arrow_rightup.png'
arrow_ce = 'graphics/arrow_right.png'
arrow_se = 'graphics/arrow_rightdown.png'
arrow_cs = 'graphics/arrow_down.png'
arrow_sw = 'graphics/arrow_leftdown.png'

ImageViewData = [(0, 0, arrow_cw, {'placement': 'cw'}),
                 (0, 0, arrow_nw, {'placement': 'nw'}),
                 (0, 0, arrow_cn, {'placement': 'cn'}),
                 (0, 0, arrow_ne, {'placement': 'ne'}),
                 (0, 0, arrow_ce, {'placement': 'ce'}),
                 (0, 0, arrow_se, {'placement': 'se'}),
                 (0, 0, arrow_cs, {'placement': 'cs'}),
                 (0, 0, arrow_sw, {'placement': 'sw'}),
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

        # set initial view position and add test layer(s)
#        self.pyslipqt.GotoLevelAndPosition(InitViewLevel, InitViewPosition)
        self.text_layer = self.pyslipqt.AddImageLayer(ImageViewData,
                                                    map_rel=False,
                                                    name='<image_view_layer>',
                                                    offset_x=0, offset_y=0)

        self.show()

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
tile_dir = 'test_viewrel_image'
app = QApplication(args)
ex = TestFrame(tile_dir)
sys.exit(app.exec_())

