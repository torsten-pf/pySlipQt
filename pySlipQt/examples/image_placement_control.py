"""
The custom control for test_image_placement.py program.
"""

import os
import sys
import platform

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QLabel, QComboBox, QPushButton, QLineEdit
from PyQt5.QtWidgets import QGridLayout, QFileDialog, QColorDialog, QGroupBox
from PyQt5.QtGui import QColor


##################################
# Custom ImagePlacementControl widget.
# 
# Constructor:
# 
#     ipc = ImagePlacementControl('test title')
# 
# Events:
# 
#     .change   the contents were changed
#     .remove   the image should be removed
#
# The '.change' event has attached attributes holding the values from the
# widget, all checked so they are 'sane'.
##################################

class ImagePlacementControl(QWidget):

    # set platform dependant values
    if platform.system() == 'Linux':
        pass
    elif platform.system() == 'Darwin':
        pass
    elif platform.system() == 'Windows':
        pass
    else:
        raise Exception('Unrecognized platform: %s' % platform.system())

    # signals raised by this widget
    change = pyqtSignal(str, str, int, QColor, int, int, int, int)
    remove = pyqtSignal()

    def __init__(self, title):
        """Initialise a ImagePlacementControl instance.

        title   title to give the custom widget
        """

        super().__init__()

        # create subwidgets used in this custom widget
        self.filename = QLabel('/file/name')
        self.filename.setToolTip('Click here to change the image file')
        self.placement = QComboBox()
        for p in ['none', 'nw', 'cn', 'ne', 'ce', 'se', 'cs', 'sw', 'cw', 'cc']:
            self.placement.addItem(p)
        self.point_radius = QLineEdit('2')
        self.point_colour = QPushButton('')
        self.posn_x = QLineEdit('0')
        self.posn_y = QLineEdit('0')
        self.offset_x = QLineEdit('0')
        self.offset_y = QLineEdit('0')
        btn_remove = QPushButton('Remove')
        btn_update = QPushButton('Update')

        # start the layout
        option_box = QGroupBox(title)

        box_layout = QGridLayout()
#        box_layout.setContentsMargins(2, 2, 2, 2)

        # start layout
        row = 1
        label = QLabel('filename:')
        label.setAlignment(Qt.AlignRight)
        box_layout.addWidget(label, row, 0)
        box_layout.addWidget(self.filename, row, 1, 1, 3)

        row += 1
        label = QLabel('placement:')
        label.setAlignment(Qt.AlignRight)
        box_layout.addWidget(label, row, 0)
        box_layout.addWidget(self.placement, row, 1)

        row += 1
        label = QLabel('point radius:')
        label.setAlignment(Qt.AlignRight)
        box_layout.addWidget(label, row, 0)
        box_layout.addWidget(self.point_radius, row, 1)
        label = QLabel('point colour:')
        label.setAlignment(Qt.AlignRight)
        box_layout.addWidget(label, row, 2)
        box_layout.addWidget(self.point_colour, row, 3)

        row += 1
        label = QLabel('X:')
        label.setAlignment(Qt.AlignRight)
        box_layout.addWidget(label, row, 0)
        box_layout.addWidget(self.posn_x, row, 1)
        label = QLabel('Y:')
        label.setAlignment(Qt.AlignRight)
        box_layout.addWidget(label, row, 2)
        box_layout.addWidget(self.posn_y, row, 3)

        row += 1
        label = QLabel('X offset:')
        label.setAlignment(Qt.AlignRight)
        box_layout.addWidget(label, row, 0)
        box_layout.addWidget(self.offset_x, row, 1)
        label = QLabel('Y offset:')
        label.setAlignment(Qt.AlignRight)
        box_layout.addWidget(label, row, 2)
        box_layout.addWidget(self.offset_y, row, 3)

        row += 1
        box_layout.addWidget(btn_remove, row, 1)
        box_layout.addWidget(btn_update, row, 3)

        option_box.setLayout(box_layout)

        layout = QHBoxLayout()
#        layout.setContentsMargins(1, 1, 1, 1)
        layout.addWidget(option_box)

        self.setLayout(layout)

        # connect internal widget events to handlers
        self.filename.mouseReleaseEvent = self.changeGraphicsFile
        self.point_colour.clicked.connect(self.changePointColour)
        btn_remove.clicked.connect(self.removeImage)
        btn_update.clicked.connect(self.updateData)

        self.show()

    def changeGraphicsFile(self, event):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_types = "PNG (*.png);;JPG (*.jpg)"
        (filename, _) = QFileDialog.getOpenFileName(self,"Open image file", "",
                                                    file_types,
                                                    options=options)
        if filename:
            # if filepath is relative to working directory, just get relative path
            if filename.startswith(ProgramPath):
                filename = filename[len(ProgramPath)+1:]
            self.filename.setText(filename)

    def changePointColour(self, event):
        color = QColorDialog.getColor()
        if color.isValid():
            colour = color.name()
            print(f'colour={colour}')
            # set colour button background
            self.point_colour.setStyleSheet(f'background-color:{colour};');
 
    def removeImage(self, event):
        self.remove.emit()

    def updateData(self, event):
        filepath = self.filename.text()
        placement = str(self.placement.currentText())
        if placement == 'none':
            placement = None
        radius = int(self.point_radius.text())
        colour = self.point_colour.palette().color(1)
        print(f'colour={colour}')
        x = int(self.posn_x.text())
        y = int(self.posn_y.text())
        offset_x = int(self.offset_x.text())
        offset_y = int(self.offset_y.text())
        
        self.change.emit(filepath, placement, radius, colour, x, y, offset_x, offset_y)
