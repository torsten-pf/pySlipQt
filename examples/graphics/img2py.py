#!/usr/bin/env python3

"""
A little program to take an image file (PNG, JPG, etc) and convert
it to python data.  Does the same thing as the wxPython tool "img2py"
which, as of 9 Feb 2018, is really hard to use.

Usage: img2py [-n <name>] <input_file> <output_file>

where -n <name> sets the internal name for the image
"""

import sys
import os


LineLength = 60


def img2py(name, in_file, out_file):
    """Convert 'in_file' to python data in 'out_file'.

    where name      is the internal procedure name
          in_file   is the path to the input file
          out_file  is the path to the output file
    """

    header = ['import base64',
              '',
              f'def get_{name}_image():',
              f'    """Generate \'{name}\' image from embedded data."""',
              '',
              '    return base64.b64decode(',
              '',
             ]

    # make sure the input file *is* there
    if not os.path.exists(in_file):
        print(f"The input file '{in_file}' doesn't exist.")
        sys.exit(1)

    # make sure the output file isn't there
    if os.path.exists(out_file):
        print(f"The output file '{out_file}' exists.  Delete it before rerunning.")
        sys.exit(1)

    # put raw base64 data in the output file temporarily
    os.system(f'base64 -i {in_file} -o {out_file}')

    # read the 'out_file' base64 data string
    with open(out_file, 'r') as fd:
        data = fd.read().strip()    # get rid of trailing newline

    # generate python code and overwrite 'out_file'
    with open(out_file, 'w') as fd:
        fd.write('\n'.join(header))

        while data:
            l_data = data[:LineLength]
            data = data[LineLength:]

            fd.write(f'        "{l_data}"')
            if data:
                fd.write('\n')

        fd.write(')\n')


if __name__ == '__main__':
    import getopt
    import traceback

    # to help the befuddled user
    def usage(msg=None):
        if msg:
            print(('*'*80 + '\n%s\n' + '*'*80) % msg)
        print(__doc__)

    # parse the CLI params
    argv = sys.argv[1:]

    try:
        (opts, args) = getopt.getopt(argv, 'hn:', ['help', 'name='])
    except getopt.GetoptError as err:
        usage(err)
        sys.exit(1)

    if len(args) != 2:
        usage()
        sys.exit(1)

    name = 'Name'

    for (opt, param) in opts:
        if opt in ['-h', '--help']:
            usage()
            sys.exit(0)
        elif opt in ['-n', '--name']:
            name = param

    # run the program code
    result = img2py(name, args[0], args[1])
    sys.exit(result)

