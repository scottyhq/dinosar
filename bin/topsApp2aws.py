#!/usr/bin/env python3
"""Create Cloud-Optimized Geotiff ISCE output and push to S3.

Usage: topsApp2aws.py int-20170828-20170816

NOTES: instead of pre-rendering TILES and RGB files, just save original COGs
and use emerging tools for rendering (see STAC spec on github)

"""
import argparse
import subprocess
import os
import dinosar.isce as dice
import dinosar.output as dout

def cmdLineParse():
    """Command line parser."""
    parser = argparse.ArgumentParser(description='create COGs')
    parser.add_argument('-i', type=str, dest='int_s3', required=True,
                        help='interferogram bucket name (s3://[int_s3])')
    parser.add_argument('-o', type=str, dest='out_s3', required=False,
                        help='output bucket (s3://[out_s3])')
    return parser.parse_args()


def main():
    """Create COG output from topsApp.py ISCE 2.2.0."""
    inps = cmdLineParse()
    intname = inps.int_s3.lstrip('s3://')
    os.chdir(os.path.join(intname, 'merged'))
    # Output name : (corresponding ISCE output, band number)
    conversions = {'amplitude-cog.tif': ('filt_topophase.unw.geo.vrt', 1),
                   'unwrapped-phase-cog.tif': ('filt_topophase.unw.geo.vrt', 2),
                   # 'coherence-cog.tif' : ('phsig.cor.geo.vrt',1),
                   'coherence-cog.tif': ('topophase.cor.geo.vrt', 2),
                   'incidence-cog.tif': ('los.rdr.geo.vrt', 1),
                   'heading-cog.tif': ('los.rdr.geo.vrt', 2),
                   'elevation-cog.tif': ('dem.crop.vrt', 1)}

    # Create Cloud-optimized geotiffs of select single-band files
    for outfile, (infile, band) in conversions.items():
        # print(infile, band, outfile)
        dout.extract_band(infile, band, 'tmp.vrt')
        dout.make_overviews('tmp.vrt')
        dout.make_cog('tmp.vrt', outfile)

    # Create RGB color-mapped thumbnails and tiles
    infiles = ['coherence-cog.tif',
               'amplitude-cog.tif',
               'unwrapped-phase-cog.tif']
    for infile in infiles:
        cptFile = dice.make_cmap(infile)
        dout.make_rgb(infile, cptFile, 'tmp.tif')
        dout.make_overviews('tmp.tif')
        outfile = infile[:-4] + '-rgb.tif'
        dout.make_cog('tmp.tif', outfile)

        dout.make_thumbnail(outfile)
        # Using stac-browser now, which utilizes marblecutter lambda-tiler
        # dout.make_leaflet_tiles(outfile)

    # Clean up temporary files, etc
    dout.cleanUp()

    # Write an html index file
    dout.writeIndex(intname)

    # Put everything into a single output folder
    if not os.path.isdir('output'):
        os.mkdir('output')
    cmd = 'cp index.html ../isce.log ../topsApp.xml output'
    dout.run_bash_command(cmd)
    cmd = 'mv *-cog* output'
    dout.run_bash_command(cmd)

    # Push to S3 folder
    if not inps.out_s3:
        s3output = inps.int_s3.replace('input','output')
    else:
        s3output = inps.out_s3
    cmd = f'aws s3 sync output {s3output}'
    dout.run_bash_command(cmd)

    print('isce2aws is all done!')


# Get interferogram name from command line argument
if __name__ == '__main__':
    main()
