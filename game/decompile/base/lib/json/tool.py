# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\json\tool.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 1508 bytes
import argparse, json, sys

def main():
    prog = 'python -m json.tool'
    description = 'A simple command line interface for json module to validate and pretty-print JSON objects.'
    parser = argparse.ArgumentParser(prog=prog, description=description)
    parser.add_argument('infile', nargs='?', type=(argparse.FileType()), help='a JSON file to be validated or pretty-printed')
    parser.add_argument('outfile', nargs='?', type=(argparse.FileType('w')), help='write the output of infile to outfile')
    parser.add_argument('--sort-keys', action='store_true', default=False, help='sort the output of dictionaries alphabetically by key')
    options = parser.parse_args()
    infile = options.infile or sys.stdin
    outfile = options.outfile or sys.stdout
    sort_keys = options.sort_keys
    with infile:
        try:
            obj = json.load(infile)
        except ValueError as e:
            try:
                raise SystemExit(e)
            finally:
                e = None
                del e

    with outfile:
        json.dump(obj, outfile, sort_keys=sort_keys, indent=4)
        outfile.write('\n')


if __name__ == '__main__':
    main()