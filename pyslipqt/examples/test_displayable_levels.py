"""Test PySlipQt "zoom cancel" AFTER zoom has occurred.

Usage: test_displayable_levels.py [-h] [-t (OSM|GMT)]
"""


import sys
import getopt
import traceback

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel,
                             QHBoxLayout)

import pyslipqt


######
# Various constants
######

DemoName = 'PySlipQt %s - zoom undo test' % pyslipqt.__version__
DemoWidth = 600
DemoHeight = 400

InitViewLevel = 2
InitViewPosition = (158.0, -20.0)


################################################################################
# The main application frame
################################################################################

class AppFrame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(300, 300, DemoWidth, DemoHeight)
        self.setWindowTitle(DemoName)
        self.show()

        # create the tile source object
        self.tile_src = Tiles.Tiles()

        # build the GUI
        box = QHBoxLayout()
        box.setContentsMargins(1, 1, 1, 1)
#        self.setLayout(box)

        self.pyslipqt = pyslipqt.PySlipQt(self, tile_src=self.tile_src, start_level=InitViewLevel)
        box.addWidget(self.pyslipqt)

        # set initial view position
        self.pyslipqt.GotoLevelAndPosition(InitViewLevel, InitViewPosition)

        # bind the pySlipQt widget to the "zoom undo" method
        self.pyslipqt.events.EVT_PYSLIPQT_LEVEL.connect(self.on_zoom)

    def on_zoom(self, event):
        """Catch and undo a zoom.

        Simulate the amount of work a user handler might do before deciding to
        undo a zoom.

        We must check the level we are zooming to.  If we don't, the GotoLevel()
        method below will trigger another exception, which we catch, etc, etc.
        """

        for _ in range(1000):
            pass

        l = [InitViewLevel, InitViewLevel, InitViewLevel, InitViewLevel,
             InitViewLevel, InitViewLevel, InitViewLevel, InitViewLevel,
             InitViewLevel, InitViewLevel, InitViewLevel, InitViewLevel,
             InitViewLevel, InitViewLevel, InitViewLevel, InitViewLevel,
             InitViewLevel, InitViewLevel, InitViewLevel, InitViewLevel,
            ]

        if event.level not in l:
            self.pyslipqt.GotoLevel(InitViewLevel)


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
#    import pyslipqt.gmt_local_tiles as Tiles
    import gmt_local_tiles as Tiles
elif tile_source == 'osm':
#    import pyslipqt.osm_tiles as Tiles
    import osm_tiles as Tiles
else:
    usage('Bad tile source: %s' % tile_source)
    sys.exit(3)

# start the app
app = QApplication(sys.argv)
ex = AppFrame()
sys.exit(app.exec_())
