"""
A program to generate a set of mapping tiles from GMT.

Usage: make_gmt_tiles [-t] [-s <size>] [-v] <tile_dir> <stop_level> [<start_level>]

where <size>        is the tile width/height in pixels (default 256)
      <tile_dir>    is the tile directory to create
      <stop_level>  is the maximum level number to create
      <start_level> is the (optional) level to start at

The -t option forces the use of topo data in the tiles.
The -v option makes the process verbose.

This program attempts to use more than one core, if available.

You *must* have installed the GMT package (and data files)
[http://gmt.soest.hawaii.edu/]
as well as the GEBCO data file if you want oceanfloor topo
[http://www.gebco.net/].

Note: this requires python 3.x.
"""

import sys
import os
import getopt
import tempfile
import shutil
import pickle
import multiprocessing
import queue
import traceback
import datetime

from PIL import Image
import numofcpus

# number of worker processes
NumberOfWorkers = numofcpus.determineNumberOfCPUs()

# where the GEBCO elevation file lives
GEBCOElevationFile = '/home/r-w/GEBCO/gridone.nc'

# default tile size, pixels
DefaultTileSize = 256

# name of info file for each tileset
TileInfoFilename = 'tile.info'

# name of the 'missing tile' picture file
MissingTilePic = 'missing_tile.png'

# various colours and widths (empty string means default)
PoliticalBorderColour = '255/0/0'
PoliticalBorderWidth = ''
WaterColourTuple = (254,254,255)
WaterColour = '%s/%s/%s' % WaterColourTuple
LandColourTuple = (253,233,174)
LandColour = '%s/%s/%s' % LandColourTuple

# dictionary mapping level to detail
Level2Detail = {0: 'l',     # low
                1: 'l',
                2: 'l',
                3: 'i',     # intermediate
                4: 'i',
                5: 'i',
                6: 'h',     # high
                7: 'h',
                8: 'h',
                9: 'f',     # full
               }


class Worker(multiprocessing.Process):
    def __init__(self, work_queue, w_num, tmp_dir):
        # base class initialization
        multiprocessing.Process.__init__(self)
 
        # job management stuff
        self.work_queue = work_queue
        self.w_num = w_num
        self.tmp_dir = os.path.join(tmp_dir, '%02d' % w_num)
        self.kill_received = False

        # set up logging
        self.logfile = 'worker_%02d.log' % w_num
        self.logf = open(self.logfile, 'w')

        # our own handler for uncaught exceptions
        def excepthook(type, value, tb):
            msg = '\n' + '=' * 80
            msg += '\nUncaught exception:\n'
            msg += ''.join(traceback.format_exception(type, value, tb))
            msg += '=' * 80 + '\n'
            self.log(msg)
            sys.exit(1)

        # plug our handler into the python system
        self.save_excepthook = sys.excepthook
        sys.excepthook = excepthook

        self.log('Started, UseTopo=%s' % str(UseTopo))

    def log(self, msg):
        # get time
        to = datetime.datetime.now()
        hr = to.hour
        min = to.minute
        sec = to.second
        msec = to.microsecond

        msg = ('%02d:%02d:%02d.%06d|%s\n' % (hr, min, sec, msec, msg))

        self.logf.write('%s\n' % msg)
        self.logf.flush()

    def run(self):
        self.log('%d starting\n' % self.w_num)

        while not self.kill_received:
            # get a task
            try:
                (tile_file, tile_size, d_opt, r_opt) = self.work_queue.get(timeout=1)
            except queue.Empty as e:
                self.log('Empty queue: %s' % str(e))
                break
 
            # the actual processing - pathnames for temp files
            ps_file = os.path.join(self.tmp_dir, 'tile.ps')
            png_file = os.path.join(self.tmp_dir, 'tile.png')

            # draw the coastline tiles
            if UseTopo:
                cmd = ('gmt grdimage %s %s -JX17.5d -fig -P -C%s -I%s -K > %s'
                       % (GEBCOElevationFile, r_opt, CptFile, GridFile, ps_file))
                self.do_cmd(cmd)
                cmd = ('gmt pscoast -P %s -JX17.5d %s '
                       '-N1/%s,%s -N3/%s,%s -W0.5 -S%s -G%s -O >> %s'
                       % (r_opt, d_opt,
                          PoliticalBorderWidth, PoliticalBorderColour,
                          PoliticalBorderWidth, PoliticalBorderColour,
                          WaterColour, LandColour, ps_file))
                self.do_cmd(cmd)
            else:
                cmd = ('gmt pscoast -P %s -JX17.5d %s '
                       '-N1/%s,%s -N3/%s,%s -W0.5 -S%s -G%s > %s'
                       % (r_opt, d_opt,
                          PoliticalBorderWidth, PoliticalBorderColour,
                          PoliticalBorderWidth, PoliticalBorderColour,
                          WaterColour, LandColour, ps_file))
                self.do_cmd(cmd)

            cmd = 'gmt psconvert %s -A -Tg' % ps_file
            self.do_cmd(cmd)

#            cmd = ('gmt convert -quality 100 -resize %dx%d! %s %s'
#                   % (tile_size, tile_size, png_file, tile_file))
            cmd = ('gmt convert %s %s'
                   % (png_file, tile_file))
            self.do_cmd(cmd)
 
        self.log('stopping')

    def do_cmd(self, cmd):
        """Execute a command.
    
        cmd   the command string to execute
        """

        self.log(cmd)
        if Verbose:
            print(cmd)
        sys.stdout.flush()
        sys.stderr.flush()

        res = os.system(cmd)
        if res:
            self.log('Error doing above command: res=%d' % res)


def do_cmd(cmd):
    if Verbose:
        print(cmd)
    sys.stdout.flush()
    sys.stderr.flush()

    res = os.system(cmd)


def make_gmt_tiles(tile_dir, min_level, max_level, tile_size):
    """Make a set of mapping tiles.

    tile_dir   the directory for output tilesets
    min_level  minimum tileset level number to create
    max_level  maximum tileset level number to create
    tile_size  size of tiles (width & height) in pixels
    """

    # generate the topo grid file, if required
    if UseTopo:
        global GridFile, CptFile

        CptFile = './bath.cpt'
        cmd = 'gmt makecpt -Cglobe > %s' % CptFile
        do_cmd(cmd)
        print(cmd)
        GridFile = './IO_int.grd'
        cmd = 'gmt grdgradient %s -A0 -Nt -G%s' % (GEBCOElevationFile, GridFile)
        do_cmd(cmd)
        print(cmd)

    # prepare queue for workers
    work_queue = multiprocessing.Queue()

    # create a temporary working directory
    tmp_dir = tempfile.mkdtemp(prefix='make_gmt_tiles_')
    for i in range(NumberOfWorkers):
        os.mkdir(os.path.join(tmp_dir, '%02d' % i))

    # define the extent of the world we are mapping
    # this is the whole world, with the break through South America
    # so we have the South Sandwich Islands and points east in one piece
    # (W, E, S, N)
    extent = (-65.0, 295.0, -66.66, 66.66)

    # delete the output directory if it exists before recreating
    #shutil.rmtree(tile_dir, ignore_errors=True)
    try:
        os.mkdir(tile_dir)
    except OSError:
        pass        # ignore error if directory already exists

    # create top-level info file - contains extent
    info_file = os.path.join(tile_dir, TileInfoFilename)
    fd = open(info_file, 'wb')
    obj = (extent, (DefaultTileSize, DefaultTileSize),
           WaterColourTuple, LandColourTuple)
    pickle.dump(obj, fd)
    fd.close()

    # generate each required tileset level
    for level in range(min_level, max_level+1):
        make_tileset(work_queue, tmp_dir, tile_dir, extent, level, tile_size)

    # start the workers and wait until all finished
    workers = []
    for i in range(NumberOfWorkers):
        worker = Worker(work_queue, i, tmp_dir)
        worker.start()
        workers.append(worker)

    for worker in workers:
        worker.join()

    # destroy the temporary working directory
    shutil.rmtree(tmp_dir, ignore_errors=True)


def make_tileset(q, tmp_dir, tile_dir, extent, level, tile_size):
    """Make one tileset directory.

    q          work queue
    tmp_dir    temporary scratch directory
    tile_dir   path to the base of the tileset directories
    extent     global map extent (w, e, s, n)
    level      the level of the tileset to generate
    tile_size  size (width & height) of each tile in set
    """

    # unpack the extent
    (w, e, s, n) = extent

    # get deltas for lon and lat
    d_lon = (e - w) / pow(2, level) / 2
    d_lat = (n - s) / pow(2, level)

    # figure out pixels/degree (for info file)
    ppd_x = tile_size / d_lon
    ppd_y = tile_size / d_lat

    # this should give us number of steps in X and Y directions
    num_tiles_x = int((e - w) / d_lon)
    num_tiles_y = int((n - s) / d_lat)

    # create the actual tileset directory
    tile_dir = os.path.join(tile_dir, '%02d' % level)
    try:
        os.mkdir(tile_dir)
    except OSError:
        pass        # ignore error if directory already exists

    # calculate the detail appropriate for the level
    d_opt = '-D%s' % Level2Detail.get(level, 'f')

    w_num = 0
    # step through each tile
    for x in range(num_tiles_x):
        for y in range(num_tiles_y):
            # get a worker number
            w_num += 1
            if w_num > NumberOfWorkers:
                w_num = 0

            # get output tile filename
            tile_file =  os.path.join(tile_dir, 'tile_%d_%d.png' % (x, y))

            # figure out -R bits
            r_w = w + x * d_lon
            r_e = r_w + d_lon
            r_n = n - y * d_lat
            r_s = r_n - d_lat
            r_opt = '-R%f/%f/%f/%f' % (r_w, r_e, r_s, r_n)

            # prepare data on queue
            q.put((tile_file, tile_size, d_opt, r_opt))

    # now create a tileset info file
    info_file = os.path.join(tile_dir, TileInfoFilename)
    obj = (num_tiles_x, num_tiles_y, ppd_x, ppd_y)
    with open(info_file, 'wb') as fd:
        pickle.dump(obj, fd)

################################################################################
# Program start
################################################################################

def usage(msg=None):
    if msg:
        print(msg+'\n')
    print(__doc__)        # module docstring used


def main(argv=None):
    global Verbose
    global UseTopo

    Verbose = False
    UseTopo = False

    # parse the command line parameters
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hs:tv',
                                   ['help', 'size=', 'topo', 'verbose'])
    except getopt.error as msg:
        usage()
        return 1

    # get all the options
    tile_size = DefaultTileSize
    Verbose = False
    for (opt, param) in opts:
        if opt in ['-s', '--size']:
            try:
                tile_size = int(param)
            except ValueError:
                usage('Tile size must be an integer > 0')
                return 1
            if tile_size < 1:
                usage('Tile size must be an integer > 0')
                return 1
        elif opt in ['-t', '--topo']:
            UseTopo = True
        elif opt in ['-v', '--verbose']:
            Verbose = True
        elif opt in ['-h', '--help']:
            usage()
            return 0

    # check we have required params
    if len(args) != 2 and len(args) != 3:
        usage()
        return 1

    tile_dir = args[0]
    min_level = 0
    try:
        max_level = int(args[1])
    except ValueError:
        usage('Stop level must be a positive integer')
        return 1
    if max_level < 0:
        usage('Stop level must be a positive integer')
        return 1
    if len(args) == 3:
        try:
            min_level = int(args[2])
        except ValueError:
            usage('Start level must be a positive integer')
            return 1
        if min_level < 0:
            usage('Start level must be a positive integer')
            return 1

    # go make the tileset
    make_gmt_tiles(tile_dir, min_level, max_level, tile_size)


if __name__ == '__main__':
    sys.exit(main())

