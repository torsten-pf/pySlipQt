"""
A test program to display tiles from the GMT tileset.

Usage: test.py [osm|gmt]

This will eventually morph into the pySlipQt example program.
"""

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QSpinBox
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtCore import Qt
import pyslipqt

# if we don't have log.py, don't crash
try:
#    from . import log
    import log
    log = log.Log('pyslipqt.log')
except AttributeError:
    # means log already set up
    pass
except ImportError as e:
    # if we don't have log.py, don't crash
    # fake all log(), log.debug(), ... calls
    def logit(*args, **kwargs):
        pass
    log = logit
    log.debug = logit
    log.info = logit
    log.warn = logit
    log.error = logit
    log.critical = logit


# name and version number of the template
TestPySlipQtName = 'PySlipQt Test'
TestPySlipQtVersion = '0.1'

# width and height of top-level widget
TestWidth = 500
TestHeight = 300


class TestPySlipQt(QWidget):

    def __init__(self, tiles_dir):
        super().__init__()

        self.tiles_dir = tiles_dir

        self.l_coord = 0
        self.x_coord = 0
        self.y_coord = 0

        self.spin_l = QSpinBox(self)
        lab_l = QLabel('Level:', self)
        lab_l.setAlignment(Qt.AlignRight)

        self.spin_l.valueChanged.connect(self.change_l)

        self.tile_src = tiles.Tiles(tiles_dir=tiles_dir)

        self.canvas = pyslipqt.PySlipQt(self, self.tile_src, {'background': (255, 0, 0, 255)})
#        self.canvas.setStyleSheet('background-color: rgb(255, 0, 0);')
        self.min_level = min(self.tile_src.levels)
        self.max_level = max(self.tile_src.levels)
        (self.num_tiles_x, self.num_tiles_y, _, _) = self.tile_src.GetInfo(self.l_coord)

        grid = QGridLayout()
        self.setLayout(grid)
        grid.setContentsMargins(2,2,2,2)

        grid.addWidget(self.canvas, 0, 0, 8, 1)

        grid.addWidget(lab_l, 0, 1)
        grid.addWidget(self.spin_l, 0, 2)

        self.spin_l.setMinimum(self.min_level)
        self.spin_l.setMaximum(self.max_level)

        self.canvas.use_level(0)

        self.setGeometry(300, 300, TestWidth, TestHeight)
        self.setWindowTitle('%s %s' % (TestPySlipQtName, TestPySlipQtVersion))
        self.show()

    def display_tile(self):
        self.canvas.update()

    def change_l(self):
        self.l_coord = self.spin_l.value()
        self.canvas.use_level(self.l_coord)
        (self.num_tiles_x, self.num_tiles_y, _, _) = self.tile_src.GetInfo(self.l_coord)
        self.display_tile()


def usage(msg=None):
    """Give help to the befuddled user."""

    if msg:
        print(f"{'*'*60}\n{msg}\n{'*'*60}")
    print(__doc__)
    sys.exit(1)


# look at sys.argv, decide on tileset and source directory
if len(sys.argv) == 2:
    tile_set = sys.argv[1].lower()
    if tile_set == 'gmt':
        import gmt_local_tiles as tiles
        tiles_dir = '/Users/r-w/gmt_tiles'
    elif tile_set == 'osm':
        import osm_tiles as tiles
        tiles_dir = './osm_tiles'
    else:
        usage(f"Bad tileset, expected 'gmt' or 'osm' but got '{tile_set}'")
else:
    usage()

# start the app, passing tile directory
app = QApplication([])
ex = TestPySlipQt(tiles_dir)
sys.exit(app.exec_())
