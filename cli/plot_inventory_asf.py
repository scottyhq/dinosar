#!/usr/bin/env python3
"""Query ASF catalog with SNWE bounds or vector file.

Author: Scott Henderson
Date: 10/2017

"""

import argparse
import dinosar.archive.plot as plot
from dinosar.archive.asf import load_inventory


def cmdLineParse():
    """Command line parser."""
    parser = argparse.ArgumentParser(description="plot_inventory.py")
    parser.add_argument(
        "-i",
        type=str,
        dest="input",
        required=True,
        help="Vector inventory (query.geojson)",
    )
    parser.add_argument(
        "-p",
        type=str,
        dest="polygon",
        required=False,
        help="Polygon defining region of interest",
    )

    return parser


def main():
    """Run as a script with args coming from argparse."""
    print("Generating map and timeline plots...")
    parser = cmdLineParse()
    args = parser.parse_args()
    gf = load_inventory(args.input)
    w, s, e, n = gf.geometry.cascaded_union.bounds
    snwe = [s, n, w, e]
    plat1, plat2 = gf.platform.unique()
    plot.plot_map(gf, snwe, args.polygon)
    plot.plot_timeline(gf, plat1, plat2)
    print("Saved map.pdf and timeline.pdf figures")


if __name__ == "__main__":
    main()
