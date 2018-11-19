pySlipQt
========

pySlipQt is a 'slip map' widget for PyQt5.  You can use it to embed a tiled map
into your PyQt5 application.  The map can be overlayed with points, images, text
and other layers.  The map tiles can come from a local source of pre-generated
tiles or from a tile server.  The tiles may have any desired coordinate system
as tile coordinates are translated to pySlipQt internal coordinates.

pySlipQt works on Linux, Mac and Windows.  Requirements are python 3 and PyQt5.

For more information visit the
`GitHub repository <https://github.com/rzzzwilson/pySlipQt/>`_ or view the API
documentation in
`the wiki <https://github.com/rzzzwilson/pySlipQt/wiki/The-pySlipQt-API>`_.

Release Notes
-------------

Release 0.5 of pySlipQt is early-release and is considered BETA software.
It is being released so anyone interested in pySlipQt can run the
"pyslipqt_demo.py" program and get comfortable with the way pySlipQt
works.  Note that testing has only been under macOS and no testing has been
done on either of Linux or Windows, though the aim is to make pySlipQt
cross-platform.

This release has these notes:

1. Some testing has been done, but not comprehensive testing, so please report
   any errors to me at rzzzwilson@gmail.com and attach the "pyslipqt.log" file.

2. "Box selection" now works.

3. Wrap-around of tiles doesn't work yet, but I *hope* to have it working even
   though it will come with some limitations.

4. The included GMT tileset is very old and has a different zoom compared to any
   tiles from the 'net, such as OSM tiles, for instance.  I hope to fix this
   later.  The GMT tiles can still be used an example of how to use locally
   generated tiles.

5. All the "examples/test_*.py" programs have been converted to python3
   and PyQt5, but there may still be problems.

6. Some bugs found and removed.

The GMT example tileset is included in the "examples" subdirectory.  The
gmt_local_tiles.py tileset code assumes that the zip file has been unzipped in
the user's home directory (ie, ~/gmt_local_tiles).  If you put the tiles in any
other place, please make the appropriate changes in gmt_local_tiles.py or make
your own version of gmt_local_tiles.py.

See the API documentation for the details on how to use pySlipQt.  The
demonstration program "examples/pyslipqt_demo.py" does require that the pySlipQt
package has been installed, though you make run pyslipqt_demo.py from any place
as long as it is moved along with its required files from the "pySlipQt/examples"
directory.
