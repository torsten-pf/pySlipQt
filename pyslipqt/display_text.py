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

from PyQt5.QtWidgets import *
import sys

class DisplayText(QWidget):

#    # set platform dependant values
#    if platform.system() == 'Linux':
#        pass
#    elif platform.system() == 'Darwin':
#        pass
#    elif platform.system() == 'Windows':
#        pass
#    else:
#        raise Exception('Unrecognized platform: %s' % platform.system())

    text_style = ('background-color: rgb(240, 240, 240);'
                  'border:1px solid rgb(128, 128, 128);'
                  'border-radius: 3px;'
                 )

    def __init__(self, title, label, tooltip=None):
        QWidget.__init__(self)

        # create all widgets
        lbl_label = QLabel(label)
        self.lbl_text = QLabel()
        self.lbl_text.setStyleSheet(self.text_style)

        # start layout
        layout = QGridLayout()

        groupbox = QGroupBox(title)
        layout.addWidget(groupbox)

        hbox = QHBoxLayout()
        groupbox.setLayout(hbox)

        hbox.addWidget(lbl_label)
        hbox.addWidget(self.lbl_text)
        hbox.addStretch()

        self.setLayout(layout)

        if tooltip:
            self.setToolTip(tooltip)


    def set_text(self, text):
        """Set the text of the display field.

        text the text to show
        """

        self.lbl_text.setText(text)
