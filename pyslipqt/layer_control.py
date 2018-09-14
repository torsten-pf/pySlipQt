"""
Custom LayerControl widget.

This is used to control each type of layer, whether map- or view-relative.
The layout is:

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

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QCheckBox, QGroupBox, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy


class LayerControl(QWidget):

    # signals raised by this widget
    change_add = pyqtSignal(bool)       # signal raised when user toggles "add" checkbox
    change_show = pyqtSignal(bool)      # signal raised when user toggles "show" checkbox
    change_select = pyqtSignal(bool)    # signal raised when user toggles "select" checkbox

    # size of the widget
    WidgetWidth = 80
    AddXOffset = 0
    AddYOffset = 5
    AddWidth = 10
    AddHeight = 10
    ShowXOffset = 35
    ShowYOffset = AddYOffset
    ShowWidth = 10
    ShowHeight = 10
    SelectXOffset = 60
    SelectYOffset = AddYOffset
    SelectWidth = 10
    SelectHeight = 10


    def __init__(self, parent, title, selectable=False, tooltip=None):
        """Initialise a LayerControl instance.

        parent      reference to parent object
        title       text to ahow in static box outline
        selectable  True if 'selectable' checkbox is to be displayed
        tooltip     tooltip text, if any
        """

        QWidget.__init__(self)
        self.setContentsMargins(0,0,0,0)
        self.setStyleSheet("font-style: normal; font-size: 10pt;background-color: rgb(232, 255, 255);");

        self.selectable = selectable

        groupbox_style = ('QGroupBox {'
                          '    border: 1px solid rgb(128, 128, 128); '
                          '    border-radius: 3px;'
                          '    background-color: rgb(232, 255, 255); '
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
        self.cb_add = QCheckBox('Add layer', self)
        self.cb_add.setGeometry(QtCore.QRect(self.AddXOffset, self.AddYOffset,
                                             self.AddWidth, self.AddHeight)) #(x, y, width, height)

        self.cb_show = QCheckBox('Show', self)
        self.cb_show.setGeometry(QtCore.QRect(self.ShowXOffset, self.ShowYOffset,
                                              self.ShowWidth, self.ShowHeight)) #(x, y, width, height)
        self.cb_show.setEnabled(False)

        if selectable:
            self.cb_select = QCheckBox('Select', self)
            self.cb_select.setGeometry(QtCore.QRect(self.SelectXOffset, self.SelectYOffset,
                                                    self.SelectWidth, self.SelectHeight)) #(x, y, width, height)
            self.cb_select.setEnabled(False)

        # start the layout
        layout = QHBoxLayout()

        groupbox = QGroupBox(title)
        groupbox.setStyleSheet(groupbox_style)

        layout.addWidget(groupbox)

        hbox = QHBoxLayout()
        hbox.addWidget(self.cb_add)
        hbox.addWidget(self.cb_show)
        if selectable:
            hbox.addWidget(self.cb_select)
#        hbox.addLayout(hbox)

        groupbox.setLayout(hbox)

        self.setLayout(layout)

######
#        # start the layout
#        layout = QVBoxLayout()
#
#        groupbox = QGroupBox(title)
#        groupbox.setStyleSheet(groupbox_style)
#
#        hbox = QHBoxLayout()
##        hbox.addStretch()
#        hbox.addWidget(self.cb_show)
#        if selectable:
#            hbox.addWidget(self.cb_select)
#
#        vbox = QVBoxLayout()
#        vbox.addWidget(self.cb_add)
#        vbox.addLayout(hbox)
#
##        layout.addWidget(groupbox)
#        groupbox.setLayout(vbox)
#
#        self.setLayout(layout)

        # if tooltip given, set it up
        if tooltip:
            self.setToolTip(tooltip)

        # connect internal widget events to handlers
        self.cb_add.stateChanged.connect(self.changed_add)
        self.cb_show.stateChanged.connect(self.changed_show)
        if selectable:
            self.cb_select.stateChanged.connect(self.changed_select)

        self.show()

    def createExampleGroup(self):
        groupBox = QGroupBox("Best Food")

        radio1 = QRadioButton("&Radio pizza")
        radio2 = QRadioButton("R&adio taco")
        radio3 = QRadioButton("Ra&dio burrito")

        radio1.setChecked(True)

        vbox = QVBoxLayout()
        vbox.addWidget(radio1)
        vbox.addWidget(radio2)
        vbox.addWidget(radio3)
        vbox.addStretch(1)
        groupBox.setLayout(vbox)

        return groupBox

    def changed_add(self):
        """Main checkbox changed."""

        if self.cb_add.checkState():
            # if "add" is ON
            self.cb_show.setEnabled(True)       # enable and set "show"
            if self.selectable:
                self.cb_select.setEnabled(True) # enable "select", if shown
        else:
            self.cb_show.setEnabled(False)
            if self.selectable:
                self.cb_select.setEnabled(False)

        self.change_add.emit(self.cb_add.checkState())

    def changed_show(self):
        """Show checkbox changed."""

        self.change_show.emit(self.cb_show.checkState())

    def changed_select(self):
        """Select checkbox changed."""

        self.change_select.emit(self.cb_select.checkState())
