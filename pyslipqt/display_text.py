#!/usr/bin/env python3

"""
A PyQt5 custom widget used by pySlipQt.

Used to display text.  The layout and components:

    +-----------------------------------------+
    |  <title>                                |
    |                                         |
    |                  +----------------+     |
    |       <label>    | <text>         |     |
    |                  +----------------+     |
    |                                         |
    +-----------------------------------------+

The constructor:

    dt = DisplayText(parent, title='', label='', tooltip=None, width=None)

Methods:

    dt.set_text("some text")
    dt.clear()

"""

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout
from PyQt5.QtWidgets import QLabel, QSpinBox, QGroupBox, QCheckBox, QSpacerItem
from PyQt5.QtCore import pyqtSignal

from rotextctrl import ROTextCtrl


class DisplayText(QWidget):

    # size of the widget
    WidgetWidth = 90
    WidgetHeight = 50

    def __init__(self, title='', label='', text='', tooltip=None, width=None):
        QWidget.__init__(self)

        # set the style for some sub-widgets
        style = ('margin-top: 5px; ')

        rostyle = ('background-color: rgb(232,232,232); '
                   'border:1px solid rgb(128, 128, 128); '
                   'border-radius: 3px; '
                   'margin-top: 5px; ')

        groupbox_style = ('QGroupBox {'
                          '    border: 1px solid rgb(128, 128, 128); '
                          '    border-radius: 3px;'
                          '}'
                          'QGroupBox:title {'
                          '    subcontrol-origin: margin;'
                          '    subcontrol-position: top left;'
                          '    padding-left: 0px;'
                          '    padding-right: 5px;'
                          '    padding-top: -7px;'
                          '    border-top: none;'
                          '}'
                         )

        # define the widgets we are going to use
        lbl_label = QLabel(label, self)
        lbl_label.setFixedHeight(self.WidgetHeight // 2)
        lbl_label.setFixedWidth(self.WidgetWidth // 2)
        lbl_label.setAlignment(Qt.AlignRight|Qt.AlignCenter)
        lbl_label.setStyleSheet(style)

        self.lbl_text = QLabel(text, self)
        self.lbl_text.setFixedHeight(self.WidgetHeight // 2)
        if width:
            self.lbl_text.setFixedWidth(width)
        else:
            self.lbl_text.setFixedWidth(self.WidgetWidth // 2)
        lbl_label.setGeometry(QtCore.QRect(self.WidgetWidth // 2, 0, self.WidgetWidth // 2, self.WidgetHeight // 2)) #(x, y, width, height)
        self.lbl_text.setAlignment(Qt.AlignLeft) # |Qt.AlignCenter)
        self.lbl_text.setStyleSheet(rostyle)
    
        # start the layout
        layout = QVBoxLayout()

        groupbox = QGroupBox(title)
        groupbox.setStyleSheet(groupbox_style)

        layout.addWidget(groupbox)

        vbox = QVBoxLayout()

        hbox = QHBoxLayout()
        hbox.addWidget(lbl_label)
        hbox.addWidget(self.lbl_text)
        hbox.addStretch()

        vbox.addLayout(hbox)

        groupbox.setLayout(vbox)

        self.setLayout(layout)

        # if tooltip
        if tooltip:
            self.setToolTip(tooltip)

        # set height of the widget
        self.setFixedHeight(self.WidgetHeight + 20)
        self.show()

    def set_text(self, text):
        """Set the text in the widget.

        text  the string to put intoi the text field
        """

        self.lbl_text.setText(text)
        self.update()
