"""
Test PySlipQt map-relative text.

Usage: test_maprel_text.py [-h] [-t (OSM|GMT)]
"""

import sys
import getopt
import traceback

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout

import pySlipQt.pySlipQt as pySlipQt

# initialize the logging system
import pySlipQt.log as log
log = log.Log('pyslipqt.log')


######
# Various demo constants
######

# demo name/version
DemoVersion = '1.0'
DemoName = f'Test map-relative text placement {DemoVersion} (pySlipQt {pySlipQt.__version__})'

DemoHeight = 800
DemoWidth = 1000

MinTileLevel = 0
InitViewLevel = 2
InitViewPosition = (133.87, -23.7)      # Alice Springs

TextMapData = [(151.20, -33.85, 'Sydney cc', {'placement': 'cc'}),
               (144.95, -37.84, 'Melbourne ne', {'placement': 'ne'}),
               (153.08, -27.48, 'Brisbane ce', {'placement': 'ce'}),
               (115.86, -31.96, 'Perth se', {'placement': 'se'}),
               (138.30, -35.52, 'Adelaide cs', {'placement': 'cs'}),
               (130.98, -12.61, 'Darwin sw', {'placement': 'sw'}),
               (147.31, -42.96, 'Hobart cw', {'placement': 'cw'}),
               (149.20, -35.31, 'Canberra nw', {'placement': 'nw',
                                                'colour': 'red',
                                                'textcolour': 'blue',
                                                'fontsize': 10}),
               (133.90, -23.70, 'Alice Springs cn', {'placement': 'cn'})]


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
        # add test test layer
        self.text_layer = self.pyslipqt.AddTextLayer(TextMapData,
                                                     map_rel=True,
                                                     name='<text_map_layer>',
                                                     offset_x=5, offset_y=1)

        self.show()

        # finally, set initial view position
        self.pyslipqt.GotoLevelAndPosition(InitViewLevel, InitViewPosition)

################################################################################

import sys
import getopt
import traceback

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

# start the app
log(DemoName)
tile_dir = 'test_maprel_text'
app = QApplication(args)
ex = TestFrame(tile_dir)
sys.exit(app.exec_())
