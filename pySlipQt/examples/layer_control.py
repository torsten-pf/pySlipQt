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

Methods:

    lc.set_show(state)      set 'show' checkbox to 'state'
    lc.set_select(state)    set 'select' checkbox to 'state'

Events:

    .change_add      the "add layer" checkbox was toggled
    .change_show     the "show" checkbox was toggled
    .change_select   the "select" checkbox was toggled
"""

import platform
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QCheckBox, QGroupBox
from PyQt5.QtWidgets import QHBoxLayout, QGridLayout

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

    # some stylesheets
    TextStyle = ('QLabel { background-color: white; '
                          'border:1px solid rgb(128, 128, 128); '
                          'border-radius: 3px; }')
    LabelStyle = ('QLabel { background-color: white; '
                           'border:1px solid rgb(128, 128, 128); '
                           'border-radius: 3px; }')
#    GroupStyle = 'QGroupBox { background-color: rgb(230, 230, 230); }'

#    LabelStyle = 'QLabel { background-color : #f0f0f0; border: 1px solid gray; border-radius: 3px; }'
    GroupStyle = ('QGroupBox { background-color: rgb(230, 230, 230); }'
                  'QGroupBox::title { subcontrol-origin: margin; '
                                 '    background-color: rgb(215, 215, 215); '
                                 '    border-radius: 3px; '
                                 '    padding: 2 2px; '
                                 '    color: black; }')


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
        group = QGroupBox(title)
        group.setCheckable(True)
        group.setChecked(False)
        group.setStyleSheet(LayerControl.GroupStyle)

        grid = QGridLayout()
        grid.setContentsMargins(2, 2, 2, 2)

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

    def set_show(self, state):
        """Set the 'show' checkbox state.

        state  new state of the checkbox, True or False
        """

        self.cb_show.setChecked(state)

    def set_select(self, state):
        """Set the 'select' checkbox state.

        state  new state of the checkbox, True or False
        """

        self.cb_select.setChecked(state)
