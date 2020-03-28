"""
Test PySlipQt view-relative text.

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


######
# Various demo constants
######

DemoVersion = '1.0'
DemoName = f'Test view-relative text placement {DemoVersion} (pySlipQt {pySlipQt.__version__})'

DemoHeight = 800
DemoWidth = 1000

MinTileLevel = 0
InitViewLevel = 2
InitViewPosition = (133.87, -23.7)      # Alice Springs

TextViewData = [(  0,   0, 'cc', {'placement':'cc','fontsize':50,'textcolour':'#ff000020'}),
                (  0,  10, 'cn', {'placement':'cn','fontsize':45,'textcolour':'#00ff0020'}),
                (-10,  10, 'ne', {'placement':'ne','fontsize':40,'textcolour':'#0000ff20'}),
                (-10,   0, 'ce', {'placement':'ce','fontsize':35,'textcolour':'#ff000080'}),
                (-10, -10, 'se', {'placement':'se','fontsize':30,'textcolour':'#00ff0080'}),
                (  0, -10, 'cs', {'placement':'cs','fontsize':25,'textcolour':'#0000ff80'}),
                ( 10, -10, 'sw', {'placement':'sw','fontsize':20,'textcolour':'#ff0000ff'}),
                ( 10,   0, 'cw', {'placement':'cw','fontsize':15,'textcolour':'#00ff00ff'}),
                ( 10,  10, 'nw', {'placement':'nw','fontsize':10,'textcolour':'#0000ffff'}),
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

        # set initial view position
#        self.pyslipqt.GotoLevelAndPosition(InitViewLevel, InitViewPosition)

        # add test test layer
        self.text_layer = self.pyslipqt.AddTextLayer(TextViewData,
                                                     map_rel=False,
                                                     name='<text_view_layer>',
                                                     offset_x=20, offset_y=20,
                                                     fontsize=20, colour='red')

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
tile_dir = 'test_viewrel_text'
app = QApplication(args)
ex = TestFrame(tile_dir)
sys.exit(app.exec_())
