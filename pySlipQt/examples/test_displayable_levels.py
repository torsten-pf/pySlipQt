"""
Test if we can have a list of "allowable levels" and if a user requests
the display of a level not in that list we CANCEL the zoom operation.

Usage: test_displayable_levels.py [-h] [-t (OSM|GMT)]
"""


import sys
import getopt
import traceback

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel,
                             QHBoxLayout)
from display_text import DisplayText

import pySlipQt.pySlipQt as pySlipQt

# initialize the logging system
import pySlipQt.log as log
log = log.Log("pyslipqt.log")


######
# Various constants
######

DemoName = 'PySlipQt %s - Zoom undo test' % pySlipQt.__version__
DemoWidth = 1000
DemoHeight = 800

InitViewLevel = 2
InitViewPosition = (100.494167, 13.7525)    # Bangkok


################################################################################
# The main application frame
################################################################################

class AppFrame(QMainWindow):
    def __init__(self, tiles):
        super().__init__()

        self.setGeometry(300, 300, DemoWidth, DemoHeight)
        self.setWindowTitle(DemoName)
        self.show()

        # create the tile source object
        self.tile_src = tiles.Tiles()

        # build the GUI
        box = QHBoxLayout()
        box.setContentsMargins(1, 1, 1, 1)

        qwidget = QWidget(self)
        qwidget.setLayout(box)
        self.setCentralWidget(qwidget)

        self.pyslipqt = pySlipQt.PySlipQt(self, tile_src=self.tile_src, start_level=InitViewLevel)
        box.addWidget(self.pyslipqt)

        self.show()

        # bind the pySlipQt widget to the "zoom undo" method
        self.pyslipqt.events.EVT_PYSLIPQT_LEVEL.connect(self.on_zoom)

        # set initial view position
        self.pyslipqt.GotoLevelAndPosition(InitViewLevel, InitViewPosition)

    def on_zoom(self, event):
        """Catch and undo a zoom.

        Simulate the amount of work a user handler might do before deciding to
        undo a zoom.

        We must check the level we are zooming to.  If we don't, the GotoLevel()
        method below will trigger another exception, which we catch, etc, etc.
        """

        log('Waiting a bit')
        for _ in range(1000000):
            pass

        l = [InitViewLevel, InitViewLevel, InitViewLevel, InitViewLevel,
             InitViewLevel, InitViewLevel, InitViewLevel, InitViewLevel,
             InitViewLevel, InitViewLevel, InitViewLevel, InitViewLevel,
             InitViewLevel, InitViewLevel, InitViewLevel, InitViewLevel,
             InitViewLevel, InitViewLevel, InitViewLevel, InitViewLevel,
            ]

        log(f'Trying to zoom to level {event.level}, allowed level={InitViewLevel}')
        if event.level not in l:
            # undo zoom
            log('New level NOT in allowed list, undoing zoom')
            self.pyslipqt.GotoLevel(InitViewLevel)
            # set initial view position
#            self.pyslipqt.GotoLevelAndPosition(InitViewLevel, InitViewPosition)


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
app = QApplication(sys.argv)
ex = AppFrame(Tiles)
sys.exit(app.exec_())
