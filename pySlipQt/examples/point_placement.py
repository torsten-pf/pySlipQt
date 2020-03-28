"""
The custom control for test_point_placement.py program.
"""

import os
import sys
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QWidget, QGridLayout, QHBoxLayout, QGroupBox,
                             QPushButton, QLabel, QComboBox, QLineEdit,
                             QSizePolicy, QFileDialog, QColorDialog)
from PyQt5.QtGui import QColor


##################################
# Custom PointPlacementControl widget.
#
# Constructor:
#
#     ppc = PointPlacementControl('test title')
#
# Events:
#
#     .change   the contents were changed
#     .remove   the image should be removed
#
# The '.change' event has attached attributes holding the values from the
# widget, all checked so they are 'sane'.
##################################

class PointPlacementControl(QWidget):
    """
    Custom PointPlacementControl widget.

    Constructor:

        ipc = PointPlacementControl('test title')

    Events:

        .change   the contents were changed
        .remove   the image should be removed

    The '.change' event has attached attributes holding the values from the
    widget, all checked so they are 'sane'.
    """

    # various sizes
    LineEditWidth = 40
    ButtonWidth = 40
    ComboboxWidth = 70

    # signals raised by this widget
    change = pyqtSignal(str, int, QColor, int, int, int, int)
    remove = pyqtSignal()

    # some stylesheets
    LabelStyle = 'QLabel { background-color : #f0f0f0; border: 1px solid gray; border-radius: 3px; }'
    GroupStyle = ('QGroupBox { background-color: rgb(230, 230, 230); }'
                  'QGroupBox::title { subcontrol-origin: margin; '
                                 '    background-color: rgb(215, 215, 215); '
                                 '    border-radius: 3px; '
                                 '    padding: 2 2px; '
                                 '    color: black; }')
    ButtonStyle = ('QPushButton {'
                                 'margin: 1px;'
                                 'border-color: #0c457e;'
                                 'border-style: outset;'
                                 'border-radius: 3px;'
                                 'border-width: 1px;'
                                 'color: black;'
                                 'background-color: white;'
                               '}')
    ButtonColourStyle = ('QPushButton {'
                                       'margin: 1px;'
                                       'border-color: #0c457e;'
                                       'border-style: outset;'
                                       'border-radius: 3px;'
                                       'border-width: 1px;'
                                       'color: black;'
                                       'background-color: %s;'
                                     '}')

    def __init__(self, title):
        """Initialise a LayerControl instance.

        title   title to give the custom widget
        """

        super().__init__()

        # create subwidgets used in this custom widget
        self.placement = QComboBox()
        for p in ['none', 'nw', 'cn', 'ne', 'ce', 'se', 'cs', 'sw', 'cw', 'cc']:
            self.placement.addItem(p)
        self.placement.setCurrentIndex(9)

        self.point_radius = QComboBox()
        for p in range(21):
            self.point_radius.addItem(str(p))
        self.point_radius.setCurrentIndex(3)
        self.point_radius.setFixedWidth(PointPlacementControl.ComboboxWidth)

        self.point_colour = QPushButton('')
        self.point_colour.setFixedWidth(PointPlacementControl.ButtonWidth)
        self.point_colour.setToolTip('Click here to change the point colour')

        self.x_posn = QComboBox()
        for p in range(0, 121, 10):
            self.x_posn.addItem(str(p - 60))
        self.x_posn.setCurrentIndex(6)
        self.x_posn.setFixedWidth(PointPlacementControl.ComboboxWidth)

        self.y_posn = QComboBox()
        for p in range(0, 121, 10):
            self.y_posn.addItem(str(p - 60))
        self.y_posn.setCurrentIndex(6)
        self.y_posn.setFixedWidth(PointPlacementControl.ComboboxWidth)

        self.x_offset = QComboBox()
        for p in range(0, 121, 10):
            self.x_offset.addItem(str(p - 60))
        self.x_offset.setCurrentIndex(6)
        self.x_offset.setFixedWidth(PointPlacementControl.ComboboxWidth)

        self.y_offset = QComboBox()
        for p in range(0, 121, 10):
            self.y_offset.addItem(str(p - 60))
        self.y_offset.setCurrentIndex(6)
        self.y_offset.setFixedWidth(PointPlacementControl.ComboboxWidth)

        btn_remove = QPushButton('Remove')
        btn_remove.resize(btn_remove.sizeHint())

        btn_update = QPushButton('Update')
        btn_update.resize(btn_update.sizeHint())

        # start the layout
        option_box = QGroupBox(title)
        option_box.setStyleSheet(PointPlacementControl.GroupStyle)

        box_layout = QGridLayout()
        box_layout.setContentsMargins(2, 2, 2, 2)
        box_layout.setHorizontalSpacing(1)
        box_layout.setColumnStretch(0, 1)

        # start layout
        row = 1
        label = QLabel('placement: ')
        label.setAlignment(Qt.AlignRight)
        box_layout.addWidget(label, row, 0)
        box_layout.addWidget(self.placement, row, 1)

        row += 1
        label = QLabel('point radius: ')
        label.setAlignment(Qt.AlignRight)
        box_layout.addWidget(label, row, 0)
        box_layout.addWidget(self.point_radius, row, 1)
        label = QLabel('colour: ')
        label.setAlignment(Qt.AlignRight)
        box_layout.addWidget(label, row, 2)
        box_layout.addWidget(self.point_colour, row, 3)

        row += 1
        label = QLabel('X: ')
        label.setAlignment(Qt.AlignRight)
        box_layout.addWidget(label, row, 0)
        box_layout.addWidget(self.x_posn, row, 1)
        label = QLabel('Y: ')
        label.setAlignment(Qt.AlignRight)
        box_layout.addWidget(label, row, 2)
        box_layout.addWidget(self.y_posn, row, 3)

        row += 1
        label = QLabel('offset X: ')
        label.setAlignment(Qt.AlignRight)
        box_layout.addWidget(label, row, 0)
        box_layout.addWidget(self.x_offset, row, 1)
        label = QLabel('Y: ')
        label.setAlignment(Qt.AlignRight)
        box_layout.addWidget(label, row, 2)
        box_layout.addWidget(self.y_offset, row, 3)

        row += 1
        box_layout.addWidget(btn_remove, row, 1)
        box_layout.addWidget(btn_update, row, 3)

        option_box.setLayout(box_layout)

        layout = QHBoxLayout()
        layout.setContentsMargins(1, 1, 1, 1)
        layout.addWidget(option_box)

        self.setLayout(layout)

        # set size hints
        self.setMinimumSize(300, 200)
        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setSizePolicy(size_policy)

        # connect internal widget events to handlers
        self.point_colour.clicked.connect(self.changePointColour)
        btn_remove.clicked.connect(self.removeImage)
        btn_update.clicked.connect(self.updateData)

    def changePointColour(self, event):
        color = QColorDialog.getColor()
        if color.isValid():
            colour = color.name()
            # set colour button background
            self.point_colour.setStyleSheet(PointPlacementControl.ButtonColourStyle % colour);
 
    def removeImage(self, event):
        self.remove.emit()

    def updateData(self, event):
        # get data from the widgets
        placement = str(self.placement.currentText())
        if placement == 'none':
            placement = None
        radius = int(self.point_radius.currentText())
        colour = self.point_colour.palette().color(1)
        x_posn = int(self.x_posn.currentText())
        y_posn = int(self.y_posn.currentText())
        x_offset = int(self.x_offset.currentText())
        y_offset = int(self.y_offset.currentText())

        print(f'updateData: placement={placement}, radius={radius}, x_posn={x_posn}, y_posn={y_posn}, x_offset={x_offset}, y_offset={y_offset}')
        
        self.change.emit(placement, radius, colour, x_posn, y_posn, x_offset, y_offset)
