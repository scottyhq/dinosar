#!/usr/bin/env python3
"""Create Cloud-Optimized Geotiff ISCE output and push to S3.

Usage: topsApp2aws.py int-20170828-20170816

NOTES: instead of pre-rendering TILES and RGB files, just save original COGs
and use emerging tools for rendering (see STAC spec on github)

"""
import subprocess
import sys
import os
import dinosar.isce as dice
import dinosar.output as dout


def main():
    """Create COG output from topsApp.py ISCE 2.1.0."""
    intname = sys.argv[1]
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
    cmd = 'mv index.html ../isce.log ../topsApp.xml *-cog* output'
    dout.run_bash_command(cmd)

    # Push to S3 folder
    cmd = f'aws s3 sync output s3://{intname}'
    dout.run_bash_command(cmd)

    print('isce2aws is all done!')


# Get interferogram name from command line argument
if __name__ == '__main__':
    main()
