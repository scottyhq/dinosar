#!/usr/bin/env python3
'''
Query ASF catalog with SNWE bounds (manually entered, or using arbitrary polygon
bounding box)

Outputs 2 JSON metadata files for S1A and S1B from ASF Vertex
Outputs 1 merged GeoJSON inventory file

Author: Scott Henderson
Date: 10/2017
'''

import argparse
import dinosar.archive.asf as asf
import sys

def cmdLineParse():
    '''
    Command line parser.
    '''
    parser = argparse.ArgumentParser(description='get_inventory_asf.py')
    parser.add_argument('-r', type=float, nargs=4, dest='roi', required=False,
            metavar=('S','N','W','E'),
            help='Region of interest bbox [S,N,W,E]')
    parser.add_argument('-i', type=str, dest='input', required=False,
            help='Polygon vector file defining region of interest')
    parser.add_argument('-b', type=float, dest='buffer', required=False,
            help='Add buffer [in degrees]')
    parser.add_argument('-f', action='store_true', default=False, dest='footprints', required=False,
            help='Create subfolders with geojson footprints')
    parser.add_argument('-k', action='store_true', default=False, dest='kmls', required=False,
            help='Download kmls from ASF API')
    parser.add_argument('-c', action='store_true', default=False, dest='csvs', required=False,
            help='Download csvs from ASF API')

    return parser


def main(parser):
    args = parser.parse_args()
    if not (args.roi or args.input):
        print("ERROR: requires '-r' or '-i' argument")
        #parser.print_usage()
        parser.print_help()
        sys.exit(1)
    asf.get_inventory_asf.main(args)


if __name__ == '__main__':
    parser = cmdLineParse()
    main(parser)
