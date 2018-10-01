#!/usr/bin/env python3

"""
A PyQt5 custom widget used by pySlipQt.

Used to display text.  The grid and components:

    +-----------------------------------------+
    |  <title>                                |
    |                                         |
    |                  +----------------+     |
    |       <label>    | <text>         |     |
    |                  +----------------+     |
    |                                         |
    +-----------------------------------------+

The constructor:

    dt = DisplayText(parent, title='', label='', textwidth=None, tooltip=None)

    where title      is the text to display at the top of the widget
          label      is the text to the left of the displayed <text>
          textwidth  is the width (in pixels) of the <text> field
          tooltip    is the text of a tooltip for the widget

Methods:

    dt.set_text("some text")
    dt.clear()

"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

class DisplayText(QWidget):

    text_style = ('background-color: rgb(255, 255, 255);'
                  'border:1px solid rgb(128, 128, 128);'
                  'border-radius: 3px;')

    def __init__(self, title, label, tooltip=None, text_width=None):
        QWidget.__init__(self)

        grid = QGridLayout()
        grid.setContentsMargins(2, 2, 2, 2)

        group = QGroupBox(title)

        lbl_label = QLabel(label)
        lbl_label.setFixedHeight(20)
        self.lbl_text = QLabel()
        self.lbl_text.setStyleSheet(DisplayText.text_style)
        if text_width:
            self.lbl_text.setFixedWidth(text_width)
        self.lbl_text.setFixedHeight(20)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(1, 1, 1, 1)
        hbox.addWidget(lbl_label)
        hbox.addWidget(self.lbl_text)
        hbox.addStretch(1)
        group.setLayout(hbox)

        grid.addWidget(group)
        self.setLayout(grid)

        if tooltip:
            self.setToolTip(tooltip)

    def set_text(self, text):
        """Set the text of the display field.

        text the text to show
        """

        self.lbl_text.setText(text)
