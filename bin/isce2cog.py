#!/usr/bin/env python3
"""Create Cloud-Optimized Geotiff ISCE output and push to S3.

Usage:
isce2cog.py -i topophase.cor.geo.vrt -b 2 -c -n
isce2cog.py -i filt_topophase.unw.geo.vrt -b 2 -c -n

NOTES: instead of pre-rendering TILES and RGB files, just save original COGs
and use emerging tools for rendering (see STAC spec on github)

"""
import argparse
import dinosar.output as dout
import dinosar.isce as dice

def cmdLineParse():
    """Command line parser."""
    parser = argparse.ArgumentParser(description='convert flat binary to COG')
    parser.add_argument('-i', type=str, dest='inFile', required=True,
                        help='input image file')
    parser.add_argument('-b', type=int, dest='band', default=1, required=False,
                        help='specify band from input image')
    parser.add_argument('-o', type=str, dest='outFile', required=False,
                        help='output file')
    # parser.add_argument('-h', action='store_true', default=False, dest='html',
    #                    required=False, help='create HTML index')
    parser.add_argument('-c', action='store_true', default=False, dest='cpt',
                        required=False, help='create colored RGB images')
    parser.add_argument('-t', action='store_true', default=False, dest='tiles',
                        required=False, help='Create image tiles for leaflet')
    parser.add_argument('-n', action='store_true', default=False, dest='nail',
                        required=False, help='Create image thumbnail')

    return parser


def main(parser):
    """Create COG output from topsApp.py ISCE 2.1.0."""
    args = parser.parse_args()

    if not args.outFile:
        args.outFile = args.inFile[:-4] + '-cog.tif'
        print(f'No output file name given, using {args.outFile}')

    msg = f'Creating COG {args.outFile} from {args.inFile} (band {args.band})'
    print(msg)

    dout.extract_band(args.inFile, args.band, 'tmp.vrt')
    dout.make_overviews('tmp.vrt')
    dout.make_cog('tmp.vrt', args.outFile)

    if not args.cpt:
        print('Skipping RGB image creation')
    else:
        rgbFile = args.outFile[:-4] + '-rgb.tif'
        print(f'Creating RGB file {rgbFile}')
        cpt = dice.make_cmap(args.inFile)
        dout.make_rgb(args.outFile, cpt, 'tmp.tif')
        dout.make_overviews('tmp.tif')
        dout.make_cog('tmp.tif', rgbFile)

        # Thumbnails and tiles only work well with colorized geotif
        if args.nail:
            dout.make_thumbnail(rgbFile)
        # if args.tiles:
        #    dout.make_leaflet_tiles(args.outFile)

    # Clean up temporary GDAL files
    dout.cleanUp()

    # Write an html index file
    # dout.writeIndex(intname)


# Get interferogram name from command line argument
if __name__ == '__main__':
    parser = cmdLineParse()
    main(parser)
