"""
Custom LayerControl widget.

This is used to control each type of layer, whether map- or view-relative.
The grid is:

    + Title text ------------------------------+
    |  +--+                                    |
    |  |  | Add layer                          |
    |  +--+                                    |
    |                                          |
    |       +--+          +--+                 |
    |       |  | Show     |  | Select          |
    |       +--+          +--+                 |
    |                                          |
    +------------------------------------------+

Constructor:

    lc = LayerControl(parent, title, selectable=False, editable=False)

Events:

    .change_add      the "add layer" checkbox was toggled
    .change_show     the "show" checkbox was toggled
    .change_select   the "select" checkbox was toggled
"""

import platform
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QWidget, QCheckBox, QGroupBox, QVBoxLayout,
                             QHBoxLayout, QSpacerItem, QSizePolicy, QGridLayout)

class LayerControl(QWidget):

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
    change_add = pyqtSignal(bool)       # signal raised when user toggles "add" checkbox
    change_show = pyqtSignal(bool)      # signal raised when user toggles "show" checkbox
    change_select = pyqtSignal(bool)    # signal raised when user toggles "select" checkbox

    def __init__(self, parent, title, selectable=False, tooltip=None):
        """Initialise a LayerControl instance.

        parent      reference to parent object
        title       text to ahow in static box outline
        selectable  True if 'selectable' checkbox is to be displayed
        tooltip     tooltip text, if any
        """

        QWidget.__init__(self)

        # create all widgets
        self.cb_show = QCheckBox('Show')
        self.cb_show.setChecked(True)
        self.cb_select = QCheckBox('Select')

        # start layout
        grid = QGridLayout()
        grid.setContentsMargins(2, 2, 2, 2)

        group = QGroupBox(title)
        group.setCheckable(True)
        group.setChecked(False)
        grid.addWidget(group, 0, 0)

        hbox = QHBoxLayout()
        hbox.setContentsMargins(1, 1, 1, 1)
        group.setLayout(hbox)

        hbox.addStretch(1)
        hbox.addWidget(self.cb_show)
        hbox.addWidget(self.cb_select)
        hbox.addStretch(3)

        self.setLayout(grid)

        # if tooltip given, set it up
        if tooltip:
            self.setToolTip(tooltip)

        # connect internal widget events to handlers
        group.toggled.connect(self.changed_add)
        self.cb_show.stateChanged.connect(self.changed_show)
        if selectable:
            self.cb_select.stateChanged.connect(self.changed_select)

        self.show()

    def changed_add(self, state):
        """Main checkbox changed.
       
        state  the state of the group check: True == ticked

        Emit a signal with the state.
        """

        self.change_add.emit(state)

    def changed_show(self, state):
        """'Show' checkbox changed.
       
        state  the state of the 'Show' check: True == ticked

        Emit a signal with the state.
        """

        self.change_show.emit(state)

    def changed_select(self, state):
        """'Select' checkbox changed.
       
        state  the state of the 'Select' check: True == ticked

        Emit a signal with the state.
        """

        self.change_select.emit(state)
