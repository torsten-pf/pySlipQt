"""
The custom control for test_text_placement.py program.
"""

import os
import sys
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QWidget, QGridLayout, QHBoxLayout, QGroupBox,
                             QPushButton, QLabel, QComboBox, QLineEdit,
                             QSizePolicy, QFileDialog, QColorDialog)
from PyQt5.QtGui import QColor


##################################
# Custom TextPlacementControl widget.
#
# Constructor:
#
#     tpc = TextPlacementControl('test title')
#
# Events:
#
#     .change   the contents were changed
#     .remove   the image should be removed
#
# The '.change' event has attached attributes holding the values from the
# widget, all checked so they are 'sane'.
##################################

class TextPlacementControl(QWidget):
    """
    Custom TextPlacementControl widget.

    Constructor:

        ipc = TextPlacementControl('test title')

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
    TestText = 'Test text'

    # initial colour values
    DefaultPointColour = 'red'
    DefaultTextColour = 'blue'

    # signals raised by this widget
    change = pyqtSignal(str, QColor, str, int, QColor, int, int, int, int)
    remove = pyqtSignal()

    # some stylesheets
    LabelStyle = 'QLabel { background-color : #f0f0f0; border: 1px solid gray; border-radius: 3px; }'
    GroupStyle = ('QGroupBox { background-color: rgb(230, 230, 230); }'
                  'QGroupBox::title { subcontrol-origin: margin; '
                                 '    background-color: rgb(215, 215, 215); '
                                 '    border-radius: 3px; '
                                 '    padding: 2 2px; '
                                 '    color: black; }')
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
        """Initialise a TextPlacementControl instance.

        title   title to give the custom widget
        """

        super().__init__()

        # create subwidgets used in this custom widget
        self.text = QLineEdit()
        self.text.setText(TextPlacementControl.TestText)
        self.text.setToolTip('You can edit this text')

        self.text_colour = QPushButton('')
        self.text_colour.setFixedWidth(TextPlacementControl.ButtonWidth)
        self.text_colour.setToolTip('Click here to change the text colour')

        self.point_radius = QComboBox()
        for p in range(21):
            self.point_radius.addItem(str(p))
        self.point_radius.setCurrentIndex(3)
        self.point_radius.setFixedWidth(TextPlacementControl.ComboboxWidth)
        self.point_radius.setToolTip('Click here to change the point radius')

        self.point_colour = QPushButton('')
        self.point_colour.setFixedWidth(TextPlacementControl.ButtonWidth)
        self.point_colour.setToolTip('Click here to change the point colour')

        self.placement = QComboBox()
        for p in ['none', 'nw', 'cn', 'ne', 'ce', 'se', 'cs', 'sw', 'cw', 'cc']:
            self.placement.addItem(p)
        self.placement.setFixedWidth(TextPlacementControl.ComboboxWidth)
        self.placement.setToolTip('Click here to change the placement')

        self.x_posn = QComboBox()
        for p in range(0, 121, 10):
            self.x_posn.addItem(str(p - 60))
        self.x_posn.setCurrentIndex(6)
        self.x_posn.setFixedWidth(TextPlacementControl.ComboboxWidth)
        self.x_posn.setToolTip('Click here to change the X position')

        self.y_posn = QComboBox()
        for p in range(0, 121, 10):
            self.y_posn.addItem(str(p - 60))
        self.y_posn.setCurrentIndex(6)
        self.y_posn.setFixedWidth(TextPlacementControl.ComboboxWidth)
        self.y_posn.setToolTip('Click here to change the Y position')

        self.x_offset = QComboBox()
        for p in range(0, 121, 10):
            self.x_offset.addItem(str(p - 60))
        self.x_offset.setCurrentIndex(6)
        self.x_offset.setFixedWidth(TextPlacementControl.ComboboxWidth)
        self.x_offset.setToolTip('Click here to change the X offset')

        self.y_offset = QComboBox()
        for p in range(0, 121, 10):
            self.y_offset.addItem(str(p - 60))
        self.y_offset.setCurrentIndex(6)
        self.y_offset.setFixedWidth(TextPlacementControl.ComboboxWidth)
        self.y_offset.setToolTip('Click here to change the Y offset')

        btn_remove = QPushButton('Remove')
        btn_remove.resize(btn_remove.sizeHint())
        btn_remove.setToolTip('Click here to remove the test layer')

        btn_update = QPushButton('Update')
        btn_update.resize(btn_update.sizeHint())
        btn_update.setToolTip('Click here to update the test layer values and show it')

        # start the layout
        option_box = QGroupBox(title)
        option_box.setStyleSheet(TextPlacementControl.GroupStyle)

        box_layout = QGridLayout()
        box_layout.setContentsMargins(5, 5, 5, 5)
        box_layout.setHorizontalSpacing(1)
        box_layout.setColumnStretch(0, 1)

        # start layout
        row = 1
        label = QLabel('text: ')
        label.setAlignment(Qt.AlignRight)
        box_layout.addWidget(label, row, 0)
        box_layout.addWidget(self.text, row, 1)
        label = QLabel('colour: ')
        label.setAlignment(Qt.AlignRight)
        box_layout.addWidget(label, row, 2)
        box_layout.addWidget(self.text_colour, row, 3)

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
        label = QLabel('placement: ')
        label.setAlignment(Qt.AlignRight)
        box_layout.addWidget(label, row, 0)
        box_layout.addWidget(self.placement, row, 1)

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
        self.text_colour.clicked.connect(self.changeTextColour)
        btn_remove.clicked.connect(self.removeLayer)
        btn_update.clicked.connect(self.updateData)

        # finally, put default colours into the colour selector buttons
        self.text_colour.setStyleSheet(TextPlacementControl.ButtonColourStyle
                                       % TextPlacementControl.DefaultTextColour)
        self.point_colour.setStyleSheet(TextPlacementControl.ButtonColourStyle
                                        % TextPlacementControl.DefaultPointColour)

    def changePointColour(self, event):
        color = QColorDialog.getColor()
        if color.isValid():
            colour = color.name()
            # set colour button background
            self.point_colour.setStyleSheet(TextPlacementControl.ButtonColourStyle
                                            % colour)
 
    def changeTextColour(self, event):
        color = QColorDialog.getColor()
        if color.isValid():
            colour = color.name()
            # set colour button background
            self.text_colour.setStyleSheet(TextPlacementControl.ButtonColourStyle
                                           % colour)
 
    def removeLayer(self, event):
        self.remove.emit()

    def updateData(self, event):
        # get data from the widgets
        text = self.text.text()
        textcolour = self.text_colour.palette().color(1)
        placement = str(self.placement.currentText())
        if placement == 'none':
            placement = None
        radius = int(self.point_radius.currentText())
        colour = self.point_colour.palette().color(1)
        x_posn = int(self.x_posn.currentText())
        y_posn = int(self.y_posn.currentText())
        x_offset = int(self.x_offset.currentText())
        y_offset = int(self.y_offset.currentText())

        print(f'updateData: text={text}, placement={placement}, radius={radius}, x_posn={x_posn}, y_posn={y_posn}, x_offset={x_offset}, y_offset={y_offset}')
        
        self.change.emit(text, textcolour, placement, radius, colour, x_posn, y_posn, x_offset, y_offset)
