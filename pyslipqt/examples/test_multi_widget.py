#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test PySlipQt with multiple widget instances.

Usage: test_multi_widget.py [-h]

Uses the GMT and OSM tiles.  Look for interactions of any sort between
the widget instances.
"""


import sys

import wx

sys.path.append('..')
import pyslipqt
import gmt_local_tiles as GMTTiles
import osm_tiles as NetTiles


######
# Various demo constants
######

DefaultAppSize = (600, 400)
MinW = 400
MinH = 300
MaxW = 1000
MaxH = 800

MinTileLevel = 0
InitViewLevel = 2
InitViewPosition = (100.51, 13.75)      # Bangkok

################################################################################
# The main application frame
################################################################################

class TestFrame(wx.Frame):
    def __init__(self):
        """Initialize the widget."""

        wx.Frame.__init__(self, None, size=DefaultAppSize,
                          title=('PySlipQt %s - multiwidget test'
                                 % pyslipqt.__version__))
        self.SetMinSize(DefaultAppSize)
        self.panel = wx.Panel(self, wx.ID_ANY)
        self.panel.SetBackgroundColour(wx.WHITE)
        self.panel.ClearBackground()

        # note that we need a unique Tile source for each widget
        # sharing directories is OK
        gmt_tile_src_1 = GMTTiles.Tiles()
        gmt_tile_src_2 = GMTTiles.Tiles()
        osm_tile_src_1 = NetTiles.Tiles()
        osm_tile_src_2 = NetTiles.Tiles()

        # build the GUI
        box = wx.BoxSizer(wx.VERTICAL)
        gsz = wx.GridSizer(rows=2, cols=2, vgap=5, hgap=5)

        self.pyslipqt1 = pyslipqt.PySlipQt(self.panel, tile_src=gmt_tile_src_1)
        gsz.Add(self.pyslipqt1, flag=wx.ALL|wx.EXPAND)

        self.pyslipqt2 = pyslipqt.PySlipQt(self.panel, tile_src=osm_tile_src_1)
        gsz.Add(self.pyslipqt2, flag=wx.ALL|wx.EXPAND)

        self.pyslipqt3 = pyslipqt.PySlipQt(self.panel, tile_src=osm_tile_src_2)
        gsz.Add(self.pyslipqt3, flag=wx.ALL|wx.EXPAND)

        self.pyslipqt4 = pyslipqt.PySlipQt(self.panel, tile_src=gmt_tile_src_2)
        gsz.Add(self.pyslipqt4, flag=wx.ALL|wx.EXPAND)

        box.Add(gsz, proportion=1, flag=wx.ALL|wx.EXPAND)

        self.panel.SetSizer(box)
        self.SetSizeHints(MinW, MinH, MaxW, MaxH)
        self.panel.Fit()
        self.Centre()
        self.Show(True)

        # set initial view position
        self.pyslipqt1.GotoLevelAndPosition(InitViewLevel, InitViewPosition)
        self.pyslipqt2.GotoLevelAndPosition(InitViewLevel, InitViewPosition)
        self.pyslipqt3.GotoLevelAndPosition(InitViewLevel, InitViewPosition)
        self.pyslipqt4.GotoLevelAndPosition(InitViewLevel, InitViewPosition)

################################################################################

if __name__ == '__main__':
    import sys
    import getopt
    import traceback

    # print some usage information
    def usage(msg=None):
        if msg:
            print(msg+'\n')
        print(__doc__)        # module docstring used

    # our own handler for uncaught exceptions
    def excepthook(type, value, tb):
        msg = '\n' + '=' * 80
        msg += '\nUncaught exception:\n'
        msg += ''.join(traceback.format_exception(type, value, tb))
        msg += '=' * 80 + '\n'
        print msg
        sys.exit(1)

    # plug our handler into the python system
    sys.excepthook = excepthook

    # decide which tiles to use, default is GMT
    argv = sys.argv[1:]

    try:
        (opts, args) = getopt.getopt(argv, 'h', ['help'])
    except getopt.error:
        usage()
        sys.exit(1)

    for (opt, param) in opts:
        if opt in ['-h', '--help']:
            usage()
            sys.exit(0)

    # start wxPython app
    app = wx.App()
    TestFrame().Show()
    app.MainLoop()

