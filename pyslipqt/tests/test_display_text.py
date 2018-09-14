#!/usr/bin/env python3

"""
Test the DisplayText custom widget used by pySlipQt.
"""

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout

sys.path.append('..')
from display_text import DisplayText

class DisplayTextExample(QWidget):
    """Application to demonstrate the pySlipQt 'DisplayText' widget."""

    def __init__(self):
        super().__init__()
        self.initUI()
        self.dt_group.set_text("Test test test")

    def initUI(self):
        self.dt_group = DisplayText(title='Group title longer', label='Label:', width=70)

        hbox = QHBoxLayout()
        hbox.addWidget(self.dt_group)
        self.setLayout(hbox)

        self.setWindowTitle('DisplayText widget')
#            self.setFixedSize(400, 125)
        self.show()

app = QApplication(sys.argv)
ex = DisplayTextExample()
sys.exit(app.exec())
