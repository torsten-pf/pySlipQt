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


class DisplayText(QWidget):

    # size of the widget
    WidgetWidth = 80
    WidgetHeight = 30
    LabelXOffset = 5
    LabelYOffset = 5
    LabelHeight = 24
    LabelWidth = 40
    TextXOffset = 40
    TextYOffset = LabelYOffset
    TextHeight = LabelHeight
    TextWidth = 35

    def __init__(self, title='', label='', text='', tooltip=None, width=None):
        QWidget.__init__(self)
        self.setContentsMargins(0,0,0,0)
#        self.setStyleSheet("font-style: normal;font-size: 10pt;font-weight: bold;");
        self.setStyleSheet("font-style: normal; font-size: 10pt;background-color: rgb(232, 255, 255);");

        # set the style for some sub-widgets
        label_style = 'margin-top: 10px; '

        text_style = ('background-color: rgb(232, 232, 232);'
                      'border:1px solid rgb(128, 128, 128);'
                      'border-radius: 3px;'
                      'margin-top: 10px;')

        groupbox_style = ('QGroupBox {'
                          '    border: 1px solid rgb(128, 128, 128);'
                          '    border-radius: 3px;'
                          '    background-color: rgb(232, 255, 255);'
                          '}'
                          'QGroupBox:title {'
                          '    subcontrol-origin: margin;'
                          '    subcontrol-position: top left;'
                          '    padding-left: 0px;'
                          '    padding-right: 0px;'
                          '    padding-top: 0px;'
                          '    padding-bottom: 0px;'
                          '    font-weight: bold;'
#                          '    border-top: none;'
                          '}'
                         )

        # define the widgets we are going to use
        lbl_label = QLabel(label, self)
        lbl_label.setFixedHeight(self.LabelHeight)
        lbl_label.setFixedWidth(self.LabelWidth)
        lbl_label.setAlignment(Qt.AlignRight|Qt.AlignCenter)
        lbl_label.setStyleSheet(label_style)
        lbl_label.setGeometry(QtCore.QRect(self.LabelXOffset, self.LabelYOffset,
                                           self.LabelWidth, self.LabelHeight)) #(x, y, width, height)

        self.lbl_text = QLabel(text, self)
#        self.lbl_text.setFixedHeight(self.LabelHeight)
#        if width:
#            self.lbl_text.setFixedWidth(width)
#        else:
#            self.lbl_text.setFixedWidth(self.TextWidth)
        self.lbl_text.setGeometry(QtCore.QRect(self.TextXOffset, self.TextYOffset,
                                               self.TextWidth, self.TextHeight)) #(x, y, width, height)
        self.lbl_text.setAlignment(Qt.AlignLeft) # |Qt.AlignCenter)
        self.lbl_text.setStyleSheet(text_style)
    
        # start the layout
        layout = QVBoxLayout()
        print(dir(layout))
        layout.setContentsMargins(0,0,0,0)

        groupbox = QGroupBox(title)
        groupbox.setStyleSheet(groupbox_style)
        groupbox.setContentsMargins(0,0,0,0)

        layout.addWidget(groupbox)

        vbox = QVBoxLayout()

        hbox = QHBoxLayout()
        hbox.addWidget(lbl_label)
        hbox.addWidget(self.lbl_text)
        hbox.addStretch()

        vbox.addLayout(hbox)
        vbox.addStretch()

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
