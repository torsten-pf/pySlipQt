#!/usr/bin/env python3

"""
A test program to display one tile from the GMT tileset.
"""

import sys
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtWidgets import QLabel, QSpinBox
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt

import gmt_local_tiles as tiles


# name and version number of the template
TestPySlipQtName = 'PySlipQt Test'
TestPySlipQtVersion = '0.1'

# width and height of top-level widget
WidgetWidth = 500
WidgetHeight = 300


class PySlipQt(QLabel):

    def __init__(self, parent, tile_src, start_level=None, **kwargs):
        super().__init__(parent)
        self.tile_src = tile_src
        self.level = 0
        if start_level:
            self.level = start_level

        self.drawlist = []
        self.image = None

        # set tile levels stuff - allowed levels, etc
        self.max_level = max(tile_src.levels)
        self.min_level = min(tile_src.levels)

        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.lightGray)
        self.setPalette(p)

    def use_level(self, level):
        self.level = level
        self.tile_src.UseLevel(level)

    def set_xy(self, x, y):
        self.x = x
        self.y = y
        self.image = self.tile_src.GetTile(x, y)

    def update_drawlist(self, image):
        self.image = image

    def paintEvent(self, e):
        if self.image:
            # put image into canvas
            painter = QPainter()
            painter.begin(self)
            pixmap = self.pixmap()
            QPainter.drawPixmap(painter, 0, 0, self.image)
            painter.end()


class TestPySlipQt(QWidget):

    def __init__(self):
        super().__init__()

        self.image = None

        self.l_coord = 0
        self.x_coord = 0
        self.y_coord = 0

        self.spin_l = QSpinBox(self)
        self.spin_x = QSpinBox(self)
        self.spin_y = QSpinBox(self)
        lab_l = QLabel('Level:', self)
        lab_l.setAlignment(Qt.AlignRight)
        lab_x = QLabel('X coord:', self)
        lab_x.setAlignment(Qt.AlignRight)
        lab_y = QLabel('Y coord:', self)
        lab_y.setAlignment(Qt.AlignRight)

        self.spin_l.valueChanged.connect(self.change_l)
        self.spin_x.valueChanged.connect(self.change_x)
        self.spin_y.valueChanged.connect(self.change_y)

        self.tile_src = tiles.Tiles(tiles_dir='/Users/r-w/tiles')

        self.canvas = PySlipQt(self, self.tile_src)
        self.min_level = min(self.tile_src.levels)
        self.max_level = max(self.tile_src.levels)
        (self.num_tiles_x, self.num_tiles_y, _, _) = self.tile_src.GetInfo(self.l_coord)

        grid = QGridLayout()
        self.setLayout(grid)
        grid.setContentsMargins(2,2,2,2)

        grid.addWidget(self.canvas, 0, 0, 8, 1)

        grid.addWidget(lab_l, 0, 1)
        grid.addWidget(self.spin_l, 0, 2)

        grid.addWidget(lab_x, 1, 1)
        grid.addWidget(self.spin_x, 1, 2)

        grid.addWidget(lab_y, 2, 1)
        grid.addWidget(self.spin_y, 2, 2)

        self.spin_l.setMinimum(self.min_level)
        self.spin_l.setMaximum(self.max_level)

        self.limit_xy_spin()

        self.setGeometry(300, 300, WidgetWidth, WidgetHeight)
        self.setWindowTitle('%s %s' % (TestPySlipQtName, TestPySlipQtVersion))
        self.show()

    def limit_xy_spin(self):
        if self.spin_x.value() >= self.num_tiles_x:
            self.x_coord = self.num_tiles_x-1

        if self.spin_y.value() >= self.num_tiles_y:
            self.y_coord = self.num_tiles_y-1

        self.spin_x.setValue(self.x_coord)
        self.spin_y.setValue(self.y_coord)

        self.spin_x.setMaximum(self.num_tiles_x-1)
        self.spin_y.setMaximum(self.num_tiles_y-1)

    def display_tile(self):
        self.canvas.set_xy(self.x_coord, self.y_coord)
        self.canvas.update()

    def change_l(self):
        self.l_coord = self.spin_l.value()
        self.canvas.use_level(self.l_coord)
        (self.num_tiles_x, self.num_tiles_y, _, _) = self.tile_src.GetInfo(self.l_coord)
        self.limit_xy_spin()
        self.display_tile()

    def change_x(self):
        self.x_coord = self.spin_x.value()
        self.display_tile()

    def change_y(self):
        self.y_coord = self.spin_y.value()
        self.display_tile()


app = QApplication(sys.argv[1:])
ex = TestPySlipQt()
sys.exit(app.exec_())
