"""
Test PySlipQt with multiple widget instances.

Usage: test_multi_widget.py [-h]

Uses the GMT and OSM tiles.  Look for interactions of any sort between
the widget instances.
"""


import sys
import getopt
import traceback

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QGridLayout

import pySlipQt.pySlipQt as pySlipQt
import pySlipQt.gmt_local as GMTTiles
import pySlipQt.open_street_map as NetTiles

# initialize the logging system
import pySlipQt.log as log
log = log.Log('pyslipqt.log')


######
# Various demo constants
######

DemoVersion = '1.0'
DemoName = f'Test multi-widget use {DemoVersion} (pySlipQt {pySlipQt.__version__})'

DemoHeight = 800
DemoWidth = 1000

MinTileLevel = 0
InitViewLevel = 2
InitViewPosition = (100.51, 13.75)      # Bangkok

################################################################################
# The main application frame
################################################################################

class TestFrame(QMainWindow):

    def __init__(self, tile_dir):
        super().__init__()

        self.tile_directory = tile_dir

        # note that we need a unique Tile source for each widget
        # sharing directories is OK
        gmt_tile_src_1 = GMTTiles.Tiles()
        gmt_tile_src_2 = GMTTiles.Tiles()
        osm_tile_src_1 = NetTiles.Tiles()
        osm_tile_src_2 = NetTiles.Tiles()

        # build the GUI
        grid = QGridLayout()

        qwidget = QWidget(self)
        qwidget.setLayout(grid)
        self.setCentralWidget(qwidget)

        self.pyslipqt1  = pySlipQt.PySlipQt(self, tile_src=gmt_tile_src_1,
                                            start_level=MinTileLevel)
        grid.addWidget(self.pyslipqt1, 0, 0)
        self.pyslipqt2  = pySlipQt.PySlipQt(self, tile_src=osm_tile_src_1,
                                            start_level=MinTileLevel)
        grid.addWidget(self.pyslipqt2, 0, 1)
        self.pyslipqt3  = pySlipQt.PySlipQt(self, tile_src=osm_tile_src_2,
                                            start_level=MinTileLevel)
        grid.addWidget(self.pyslipqt3, 1, 0)
        self.pyslipqt4  = pySlipQt.PySlipQt(self, tile_src=gmt_tile_src_2,
                                            start_level=MinTileLevel)
        grid.addWidget(self.pyslipqt4, 1, 1)

        # set the size of the demo window, etc
        self.setGeometry(100, 100, DemoWidth, DemoHeight)
        self.setWindowTitle(DemoName)

        # set initial view position
#        gmt_tile_src_1.GotoLevelAndPosition(InitViewLevel, InitViewPosition)
#        gmt_tile_src_2.GotoLevelAndPosition(InitViewLevel, InitViewPosition)
#        osm_tile_src_1.GotoLevelAndPosition(InitViewLevel, InitViewPosition)
#        osm_tile_src_2.GotoLevelAndPosition(InitViewLevel, InitViewPosition)

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
    (opts, args) = getopt.getopt(argv, 'h', ['help'])
except getopt.error:
    usage()
    sys.exit(1)

for (opt, param) in opts:
    if opt in ['-h', '--help']:
        usage()
        sys.exit(0)

# start the app
log(DemoName)
tile_dir = 'test_multi_widget'
app = QApplication(args)
ex = TestFrame(tile_dir)
sys.exit(app.exec_())

