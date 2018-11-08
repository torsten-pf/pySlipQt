"""
Test the LayerControl custom widget used by pySlipQt.
"""

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout

from layer_control import LayerControl

# initialize the logging system
import pySlipQt.log as log
log = log.Log('pyslipqt.log')


class LayerControlExample(QWidget):
    """Application to demonstrate the pySlipQt 'LayerControl' widget."""

    def __init__(self):
        super().__init__()

        self.lc_group = LayerControl(self, title='Group title longer', selectable=True, tooltip="tooltip")

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(self.lc_group)
        self.setLayout(hbox)

        self.setWindowTitle('LayerControl widget')
        self.show()

        # connect the widget to '.changed' event handler
        self.lc_group.change_add.connect(self.layer_add)
        self.lc_group.change_show.connect(self.layer_show)
        self.lc_group.change_select.connect(self.layer_select)

    def layer_add(self, add):
        print(f'Layer ADD={add}')
        log(f'Layer ADD={add}')

    def layer_show(self, show):
        print(f'Layer SHOW={show}')
        log(f'Layer SHOW={show}')

    def layer_select(self, select):
        print(f'Layer SELECT={select}')
        log(f'Layer SELECT={select}')


app = QApplication(sys.argv)
ex = LayerControlExample()
sys.exit(app.exec())
