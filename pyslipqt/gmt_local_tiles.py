"""
A tile source that serves pre-generated GMT tiles from the local filesystem.

Uses pyCacheBack to provide in-memory and on-disk caching.
"""

import os
import pickle
import tiles


# if we don't have log.py, don't crash
try:
#    from . import log
    import log
    log = log.Log('pyslipqt.log')
except AttributeError:
    # means log already set up
    pass
except ImportError as e:
    # if we don't have log.py, don't crash
    # fake all log(), log.debug(), ... calls
    def logit(*args, **kwargs):
        pass
    log = logit
    log.debug = logit
    log.info = logit
    log.warn = logit
    log.error = logit
    log.critical = logit


###############################################################################
# Change values below here to configure the GMT local tile source.
###############################################################################

# attributes used for tileset introspection
# names must be unique amongst tile modules
tileset_name = 'GMT local tiles'
tileset_shortname = 'GMT tiles'
tileset_version = '1.0'

# the pool of tile servers used
TileServers = None

# the path on the server to a tile
# {} params are Z=level, X=column, Y=row, origin at map top-left
TileURLPath = None

# tile levels to be used
TileLevels = range(5)

# maximum pending requests for each tile server
# unused with local tiles
MaxServerRequests = None

# set maximum number of in-memory tiles for each level
MaxLRU = 10000

# path to the INFO file for GMT tiles
TileInfoFilename = "tile.info"

################################################################################
# Class for GMT local tiles.   Builds on tiles.BaseTiles.
################################################################################

class Tiles(tiles.BaseTiles):
    """An object to source GMT tiles for pySlipQt."""

    # size of these tiles
    TileWidth = 256
    TileHeight = 256

    # where earlier-cached tiles will be
    # this can be overridden in the __init__ method
    TilesDir = os.path.abspath(os.path.expanduser('~/gmt_tiles'))

    def __init__(self, tiles_dir=TilesDir):
        """Override the base class for GMT tiles.

        Basically, just fill in the BaseTiles class with GMT values from above
        and provide the Geo2Tile() and Tile2Geo() methods.
        """

        super(Tiles, self).__init__(TileLevels,
                                    Tiles.TileWidth, Tiles.TileHeight,
                                    max_lru=MaxLRU, tiles_dir=tiles_dir)

        # we *can* wrap tiles in X direction, but not Y
        self.wrap_x = True
        self.wrap_y = False

        # override the tiles.py extent here, the GMT tileset is different
        self.extent = (-65.0, 295.0, -66.66, 66.66)

        # get tile information into instance
        self.level = min(TileLevels)
        (self.num_tiles_x, self.num_tiles_y,
         self.ppd_x, self.ppd_y) = self.GetInfo(self.level)

    def GetInfo(self, level):
        """Get tile info for a particular level.
        Override the tiles.py method.

        level  the level to get tile info for

        Returns (num_tiles_x, num_tiles_y, ppd_x, ppd_y) or None if 'levels'
        doesn't exist.
        """

        # is required level available?
        if level not in self.levels:
            return None

        # see if we can open the tile info file.
        info_file = os.path.join(self.tiles_dir, '%d' % level, TileInfoFilename)
        try:
            with open(info_file, 'rb') as fd:
                info = pickle.load(fd)
        except IOError:
            log(f'GetInfo: problem reading info file {info_file}')
            info = None

        return info

    def Geo2Tile(self, geo):
        """Convert geo to tile fractional coordinates for level in use.

        geo  a tuple of geo coordinates (xgeo, ygeo)

        Returns (xtile, ytile).

        This is an easy transformation as geo coordinates are Cartesian.
        """

        log(f'Geo2Tile: geo={geo}')

        # unpack the 'geo' tuple
        (xgeo, ygeo) = geo

        # get extent information
        (min_xgeo, max_xgeo, min_ygeo, max_ygeo) = self.extent

        log(f'Geo2Tile: min_xgeo={min_xgeo}, max_xgeo={max_xgeo}, min_ygeo={min_ygeo}, max_ygeo={max_ygeo}')

        # get 'geo-like' coords with origin at top-left
        x = xgeo - min_xgeo
        y = max_ygeo - ygeo

        log(f'Geo2Tile: x={x}, y={y}')
        log(f'Geo2Tile: self.ppd_x={self.ppd_x}')

        tiles_x = x * self.ppd_x / self.tile_size_x
        tiles_y = y * self.ppd_y / self.tile_size_y

        log(f'Geo2Tile: returning X={tiles_x}, Y={tiles_y}')

        return (tiles_x, tiles_y)

    def Tile2Geo(self, tile):
        """Convert tile fractional coordinates to geo for level in use.

        tile  a tuple (xtile,ytile) of tile fractional coordinates

        Note that we assume the point *is* on the map!

        This is an easy transformation as geo coordinates are Cartesian.
        """

        (xtile, ytile) = tile

        # get extent information
        (min_xgeo, max_xgeo, min_ygeo, max_ygeo) = self.extent

        # compute tile degree sizes and position in the coordinate system
        tdeg_x = self.tile_size_x / self.ppd_x
        tdeg_y = self.tile_size_y / self.ppd_y
        xgeo = xtile*tdeg_x + min_xgeo
        ygeo = max_ygeo - ytile*tdeg_y

        return (xgeo, ygeo)

