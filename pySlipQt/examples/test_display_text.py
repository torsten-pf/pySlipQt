"""
Test the DisplayText custom widget used by pySlipQt.
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout

from display_text import DisplayText

class DisplayTextExample(QWidget):
    """Application to demonstrate the pySlipQt 'DisplayText' widget."""

    def __init__(self):
        super().__init__()

        self.dt_group = DisplayText(title='Group title longer', label='Label:',
                                    tooltip='A tooltip')
        self.dt_group.set_text("14")

        hbox = QHBoxLayout()
        hbox.setSpacing(5)
        hbox.setContentsMargins(1, 1, 1, 1)
        hbox.addWidget(self.dt_group)
        self.setLayout(hbox)

        self.setWindowTitle('DisplayText widget')
        self.show()

app = QApplication(sys.argv)
ex = DisplayTextExample()
sys.exit(app.exec())
