"""Dinosar."""

import subprocess
import sys


def run_bash_command(cmd):
    """Call a system command through the subprocess python module."""
    print(cmd)
    try:
        retcode = subprocess.call(cmd, shell=True)
        if retcode < 0:
            print("Child was terminated by signal", -retcode, file=sys.stderr)
        else:
            print("Child returned", retcode, file=sys.stderr)
    except OSError as e:
        print("Execution failed:", e, file=sys.stderr)


def make_rgb(infile, cptfile, outfile):
    """Create color-mapped RGB Geotiff file.

    Parameters
    ----------
    infile : str
        single-band raster file recognized by GDAL
    cptfile : float
        external colormap cpt file

    """
    # outfile = infile[:-4] + '-rgb.tif'
    # -alpha
    cmd = f'gdaldem color-relief {infile} {cptfile} {outfile}'
    run_bash_command(cmd)


def make_thumbnail(infile, percent=5, format='JPEG'):
    """Make a JPEG or PNG thumbnail - percent of full-size image.

    Parameters
    ----------
    infile : str
        single-band raster file recognized by GDAL
    percent : int
        percentage of orginal raster size for smaller thumbnail
    format : str
        output format (JPEG or PNG)

    """
    suffix = format.lower()
    outfile = infile[:-4] + f'-thumb.{suffix}'
    cmd = f'gdal_translate -of {format} -r cubic -outsize \
            {percent}% 0 {infile} {outfile}'
    run_bash_command(cmd)


def make_leaflet_tiles(infile):
    """Create WMTS tiles for use with leaflet.js library.

    Currently, gdal script gdal2tiles.py is called to do this.

    Parameters
    ----------
    infile : str
        single-band raster file recognized by GDAL

    """
    cmd = f'gdal2tiles.py -w leaflet -z 6-12 {infile}'
    run_bash_command(cmd)


def extract_band(infile, band, outfile):
    """Create WMTS tiles for use with leaflet.js library.

    Currently, gdal script gdal2tiles.py is called to do this.

    Parameters
    ----------
    infile : str
        single-band raster file recognized by GDAL

    """
    cmd = f'gdal_translate -of VRT -b {band} -a_nodata 0.0 {infile} {outfile}'
    run_bash_command(cmd)


def make_overviews(infile):
    """Create internal overviews in cloud-optimized geotiff.

    Currently, gdal script gdaladdo is called to do this.

    """
    cmd = f'gdaladdo {infile} 2 4 8 16 32'
    run_bash_command(cmd)


def make_cog(infile, outfile):
    """Create single-band cloud-optimized geotiff.

    Currently, gdal_tanslate to do this.

    """
    cmd = f'gdal_translate {infile} {outfile} -co COMPRESS=DEFLATE \
-co TILED=YES -co BLOCKXSIZE=512 -co BLOCKYSIZE=512 \
-co COPY_SRC_OVERVIEWS=YES --config GDAL_TIFF_OVR_BLOCKSIZE 512'
    run_bash_command(cmd)


def cleanUp():
    """Remove intermediate and auxiliary files."""
    print('removing temporary files...')
    cmd = 'rm tmp* *aux.xml'
    run_bash_command(cmd)


def writeIndex(intname):
    """Write a super simple HTML index for results webpage.

    Geocoded ISCE outputs are referenced as links on a webpage .

    """
    text = '''<html>
<head>
<title>{intname}</title>
</head>

<body>
<h1>{intname}</h1>

<a href="amplitude-cog-rgb-thumb.png">
  <img src="amplitude-cog-rgb-thumb.png">
</a>
<a href="unwrapped-phase-cog-rgb-thumb.png">
  <img src="unwrapped-phase-cog-rgb-thumb.png">
</a>

<h2>Leaflet Slippy Map Links</h2>
<ul>
  <li><a href="amplitude-cog-rgb/leaflet.html">amplitude-cog-rgb.tif</a> </li>
  <li><a href="unwrapped-phase-cog-rgb/leaflet.html">unwrapped-phase-rgb.tif</a> </li>
  <li><a href="coherence-cog-rgb/leaflet.html">coherence-cog-rgb.tif</a> </li>
</ul>

<h2>Download</h2>
<ul>
<li><a href="amplitude-cog.tif">amplitude-cog.tif</a></li>
<li><a href="unwrapped-phase-cog.tif">unwrapped-phase-cog.tif</a></li>
<li><a href="coherence-cog.tif">coherence-cog.tif</a></li>
<li><a href="elevation-cog.tif">elevation-cog.tif</a></li>
<li><a href="incidence-cog.tif">incidence-cog.tif</a></li>
<li><a href="heading-cog.tif">heading-cog.tif</a></li>
</ul>

<h2>Metadata</h2>
<ul>
<li><a href="topsApp.xml">topsApp.xml</a></li>
<li><a href="topsProc.xml">topsProc.xml</a></li>
<li><a href="isce.log">isce.log</a></li>
</ul>


</body>
</html>'''
    formattedText = text.format(intname=intname)
    with open('index.html', 'w') as index:
        index.write(formattedText)
