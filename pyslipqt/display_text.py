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

    dt = DisplayText(parent, title='', label='', tooltip=None)

Methods:

    dt.set_text("some text")
    dt.clear()

"""

#import platform
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

class DisplayText(QWidget):

#    # set platform dependent values, if any
#    if platform.system() == 'Linux':
#        pass
#    elif platform.system() == 'Darwin':
#        pass
#    elif platform.system() == 'Windows':
#        pass
#    else:
#        raise Exception('Unrecognized platform: %s' % platform.system())

#    text_style = ('background-color: rgb(240, 240, 240);'
#                  'border:1px solid rgb(128, 128, 128);'
#                  'border-radius: 3px;'
#                 )
    text_style = ('background-color: rgb(255, 255, 255);'
                  'border:1px solid rgb(128, 128, 128);'
                  'border-radius: 3px;'
                 )

    def __init__(self, title, label, tooltip=None, text_width=None):
        QWidget.__init__(self)

        # create both labels required for display
        lbl_label = QLabel(label)
#        lbl_label.setAlignment(Qt.AlignRight)
        self.lbl_text = QLabel()
        self.lbl_text.setStyleSheet(self.text_style)
        if text_width:
            self.lbl_text.setFixedWidth(text_width)

        # start grid
        grid = QGridLayout()
        grid.columnStretch(1)
#        grid.setSpacing(0)
        grid.setContentsMargins(5, 5, 3, 5)

        groupbox = QGroupBox(title)
        groupbox.setContentsMargins(3, 3, 3, 3)
        grid.addWidget(groupbox)

        grid.addWidget(lbl_label, 0, 0)
        grid.addWidget(self.lbl_text, 0, 1)

        self.setLayout(grid)

        if tooltip:
            self.setToolTip(tooltip)


    def set_text(self, text):
        """Set the text of the display field.

        text the text to show
        """

        self.lbl_text.setText(text)
