"""
Test PySlipQt view-relative points.

Usage: test_viewrel_point.py [-h] [-t (OSM|GMT)]
"""

import sys
import getopt
import traceback

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout

# initialize the logging system
import pySlipQt.log as log
log = log.Log('pyslipqt.log')

import pySlipQt.pySlipQt as pySlipQt

######
# Various demo constants
######

# demo name/version
DemoVersion = '1.0'
DemoName = f'Test view-relative point placement {DemoVersion} (pySlipQt {pySlipQt.__version__})'

DemoHeight = 800
DemoWidth = 1000

MinTileLevel = 0
InitViewLevel = 2
InitViewPosition = (133.87, -23.7)      # Alice Springs

PointViewDataNW = [( 0, 0), ( 2, 0), ( 4, 0), ( 6, 0), ( 8, 0),
                   (10, 0), ( 0, 2), ( 0, 4), ( 0, 6), ( 0, 8),
                   ( 0,10), ( 2, 2), ( 4, 4), ( 6, 6), ( 8, 8),
                   (10,10), (12,12), (14,14), (16,16), (18,18),
                   (20,20)
                  ]

PointViewDataCN = [(  0,  0), ( -2,  2), ( -4,  4), ( -6,  6),
                   ( -8,  8), (-10, 10), (  2,  2), (  4,  4),
                   (  6,  6), (  8,  8), ( 10, 10), (  0,  2),
                   (  0,  4), (  0,  6), (  0,  8), (  0, 10),
                   (  0, 12), (  0, 14), (  0, 16), (  0, 18),
                   (  0, 20)
                  ]

PointViewDataNE = [(  0,  0), ( -2,  0), ( -4,  0), ( -6,  0),
                   ( -8,  0), (-10,  0), (  0,  2), (  0,  4),
                   (  0,  6), (  0,  8), (  0, 10), ( -2,  2),
                   ( -4,  4), ( -6,  6), ( -8,  8), (-10, 10),
                   (-12, 12), (-14, 14), (-16, 16), (-18, 18),
                   (-20, 20)
                  ]

PointViewDataCE = [(  0,  0), ( -2, -2), ( -4, -4), ( -6, -6),
                   ( -8, -8), (-10,-10), ( -2,  2), ( -4,  4),
                   ( -6,  6), ( -8,  8), (-10, 10), ( -2,  0),
                   ( -4,  0), ( -6,  0), ( -8,  0), (-10,  0),
                   (-12,  0), (-14,  0), (-16,  0), (-18,  0),
                   (-20,  0)
                  ]

PointViewDataSE = [(  0,  0), (  0, -2), (  0, -4), (  0, -6),
                   (  0, -8), (  0,-10), ( -2,  0), ( -4,  0),
                   ( -6,  0), ( -8,  0), (-10,  0), ( -2, -2),
                   ( -4, -4), ( -6, -6), ( -8, -8), (-10,-10),
                   (-12,-12), (-14,-14), (-16,-16), (-18,-18),
                   (-20,-20)
                  ]

PointViewDataCS = [(  0,  0), ( -2, -2), ( -4, -4), ( -6, -6),
                   ( -8, -8), (-10,-10), (  2, -2), (  4, -4),
                   (  6, -6), (  8, -8), ( 10,-10), (  0, -2),
                   (  0, -4), (  0, -6), (  0, -8), (  0,-10),
                   (  0,-12), (  0,-14), (  0,-16), (  0,-18),
                   (  0,-20)
                  ]

PointViewDataSW = [(  0,  0), (  0, -2), (  0, -4), (  0, -6),
                   (  0, -8), (  0,-10), (  2,  0), (  4,  0),
                   (  6,  0), (  8,  0), ( 10,  0), (  2, -2),
                   (  4, -4), (  6, -6), (  8, -8), ( 10,-10),
                   ( 12,-12), ( 14,-14), ( 16,-16), ( 18,-18),
                   ( 20,-20)
                  ]

PointViewDataCW = [(  0,  0), (  2, -2), (  4, -4), (  6, -6),
                   (  8, -8), ( 10,-10), (  2,  2), (  4,  4),
                   (  6,  6), (  8,  8), ( 10, 10), (  2,  0),
                   (  4,  0), (  6,  0), (  8,  0), ( 10,  0),
                   ( 12,  0), ( 14,  0), ( 16,  0), ( 18,  0),
                   ( 20,  0)
                  ]

PointViewDataCC = [(  0,  0), (  2, -2), (  4, -4), (  6, -6),
                   (  8, -8), ( 10,-10),
                   (  0,  0), (  2,  2), (  4,  4), (  6,  6),
                   (  8,  8), ( 10, 10),
                   (  0,  0), ( -2, -2), ( -4, -4), ( -6, -6),
                   ( -8, -8), (-10,-10),
                   (  0,  0), ( -2,  2), ( -4,  4), ( -6,  6),
                   ( -8,  8), (-10, 10),
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

        # add test point layers
        self.pyslipqt.AddPointLayer(PointViewDataNW, placement='nw',
                                    map_rel=False, colour='blue', radius=2,
                                    offset_x=0, offset_y=0,
                                    name='<point_map_layer>')

        self.pyslipqt.AddPointLayer(PointViewDataCN, placement='cn',
                                    map_rel=False, colour='red', radius=2,
                                    offset_x=0, offset_y=0,
                                    name='<point_map_layer>')

        self.pyslipqt.AddPointLayer(PointViewDataNE, placement='ne',
                                    map_rel=False, colour='green', radius=2,
                                    offset_x=0, offset_y=0,
                                    name='<point_map_layer>')

        self.pyslipqt.AddPointLayer(PointViewDataCE, placement='ce',
                                    map_rel=False, colour='black', radius=2,
                                    offset_x=0, offset_y=0,
                                    name='<point_map_layer>')

        self.pyslipqt.AddPointLayer(PointViewDataSE, placement='se',
                                    map_rel=False, colour='yellow', radius=2,
                                    offset_x=0, offset_y=0,
                                    name='<point_map_layer>')

        self.pyslipqt.AddPointLayer(PointViewDataCS, placement='cs',
                                    map_rel=False, colour='gray', radius=2,
                                    offset_x=0, offset_y=0,
                                    name='<point_map_layer>')

        self.pyslipqt.AddPointLayer(PointViewDataSW, placement='sw',
                                    map_rel=False, colour='#7f7fff', radius=2,
                                    offset_x=0, offset_y=0,
                                    name='<point_map_layer>')

        self.pyslipqt.AddPointLayer(PointViewDataCW, placement='cw',
                                    map_rel=False, colour='#ff7f7f', radius=2,
                                    offset_x=0, offset_y=0,
                                    name='<point_map_layer>')

        self.pyslipqt.AddPointLayer(PointViewDataCC, placement='cc',
                                    map_rel=False, colour='#7fff7f', radius=2,
                                    offset_x=0, offset_y=0,
                                    name='<point_map_layer>')

        # set initial view position
#        self.pyslipqt.GotoLevelAndPosition(InitViewLevel, InitViewPosition)

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

# start the app
log(DemoName)
tile_dir = 'test_viewrel_point'
app = QApplication(args)
ex = TestFrame(tile_dir)
sys.exit(app.exec_())
