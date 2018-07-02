"""Functions for ISCE software.

This module has functions that facilitate running `ISCE software` (v2.1.0).
Currently extensively uses external calls to GDAL command line scripts. Some
functions borrow from example applications distributed with ISCE.

.. _`ISCE software`: https://winsar.unavco.org/software/isce

"""

from lxml import objectify, etree
import os
# import matplotlib
# matplotlib.use("Agg") # Necessary for some systems
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
import numpy as np


def read_topsApp_xml(xmlFile):
    """Write topsApp.py control file.

    Parameters
    ----------
    xmlPath : str
        path to xmlFile

    Returns
    -------
    xmlString : str
        XML as a formatted string

    """
    x = etree.parse(xmlFile)
    xmlString = etree.tostring(x, pretty_print=True, encoding="unicode")
    return xmlString


def create_topsApp_xml(inputDict):
    c = etree.Element("thisdoesntmatter")


def write_topsApp_xml(inputDict):
    """Write topsApp.py control file.

    This function creates topsApp.xml given a dictionary of parameters and
    settings.

    Parameters
    ----------
    inputDict : dict
        dictionary of input settings

    """
    print('Writing topsApp.xml with the following configuration:')
    print(inputDict)
    xmlString = read_topsApp_xml("topsApp-template.xml")
    with open('topsApp.xml', 'w') as outfile:
        print(etree.tostring(xmlString.format(**inputDict),
                             pretty_print=True,
                             encoding="unicode"), file=outfile)


def write_cmap(outname, vals, scalarMap):
    """Write external cpt colormap file based on matplotlib colormap.

    Parameters
    ----------
    outname : str
        name of output file (e.g. amplitude-cog.cpt)
    vals : float
        values to be mapped to ncolors
    scalarMap: ScalarMappable
        mapping between array value and colormap value between 0 and 1

    """
    with open(outname, 'w') as fid:
        for val in vals:
            cval = scalarMap.to_rgba(val)
            fid.write('{0} {1} {2} {3} \n'.format(val,  # value
                                                  int(cval[0]*255),  # R
                                                  int(cval[1]*255),  # G
                                                  int(cval[2]*255)))  # B
        fid.write('nv 0 0 0 0 \n')  # nodata alpha transparency


def make_amplitude_cmap(mapname='gray', vmin=1, vmax=1e5, ncolors=64):
    """Write default colormap (amplitude-cog.cpt) for isce amplitude images.

    Uses a LogNorm colormap by default since amplitude return values typically
    span several orders of magnitude.

    Parameters
    ----------
    mapname : str
        matplotlib colormap name
    vmin : float
        data value mapped to lower end of colormap
    vmax : float
        data value mapped to upper end of colormap
    ncolors : int
        number of discrete mapped values between vmin and vmax

    """
    cmap = plt.get_cmap(mapname)
    # NOTE for strong contrast amp return:
    # cNorm = colors.Normalize(vmin=1e3, vmax=1e4)
    cNorm = colors.LogNorm(vmin=vmin, vmax=vmax)
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cmap)
    vals = np.linspace(vmin, vmax, ncolors, endpoint=True)
    outname = 'amplitude-cog.cpt'
    write_cmap(outname, vals, scalarMap)

    return outname


def make_wrapped_phase_cmap(mapname='plasma', vmin=-50, vmax=50, ncolors=64,
                            wrapRate=6.28):
    """Re-wrap unwrapped phase values and write 'unwrapped-phase-cog.cpt'.

    Each color cycle represents wavelength/2 line-of-sight change for
    wrapRate=6.28.

    Parameters
    ----------
    mapname : str
        matplotlib colormap name
    vmin : float
        data value mapped to lower end of colormap
    vmax : float
        data value mapped to upper end of colormap
    ncolors : int
        number of discrete mapped values between vmin and vmax
    wrapRate : float
        number of radians per phase cycle

    """
    cmap = plt.get_cmap(mapname)
    cNorm = colors.Normalize(vmin=0, vmax=1)  # re-wrapping normalization
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cmap)
    vals = np.linspace(vmin, vmax, ncolors, endpoint=True)
    vals_wrapped = np.remainder(vals, wrapRate) / wrapRate
    outname = 'unwrapped-phase-cog.cpt'
    with open(outname, 'w') as fid:
        for val, wval in zip(vals, vals_wrapped):
            cval = scalarMap.to_rgba(wval)
            fid.write('{0} {1} {2} {3} \n'.format(val,  # value
                                                  int(cval[0]*255),  # R
                                                  int(cval[1]*255),  # G
                                                  int(cval[2]*255)))  # B
        fid.write('nv 0 0 0 0 \n')  # nodata alpha

    return outname


def make_coherence_cmap(mapname='inferno', vmin=1e-5, vmax=1, ncolors=64):
    """Write default colormap (coherence-cog.cpt) for isce coherence images.

    Parameters
    ----------
    mapname : str
        matplotlib colormap name
    vmin : float
        data value mapped to lower end of colormap
    vmax : float
        data value mapped to upper end of colormap
    ncolors : int
        number of discrete mapped values between vmin and vmax

    """
    cmap = plt.get_cmap(mapname)
    cNorm = colors.Normalize(vmin=vmin, vmax=vmax)
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cmap)
    vals = np.linspace(vmin, vmax, ncolors, endpoint=True)
    outname = 'coherence-cog.cpt'
    write_cmap(outname, vals, scalarMap)

    return outname


def make_rgb(infile, cptfile):
    """Create color-mapped RGBA Geotiff file.

    Parameters
    ----------
    infile : str
        single-band raster file recognized by GDAL
    cptfile : float
        external colormap cpt file

    """
    outfile = infile[:-4] + '-rgb.tif'
    cmd = f'gdaldem color-relief -alpha {infile} {cptfile} {outfile}'
    print(cmd)
    os.system(cmd)
    return outfile


def make_thumbnails(infile, small=5, large=10):
    """Make a large and small png overview image.

    Parameters
    ----------
    infile : str
        single-band raster file recognized by GDAL
    small : int
        percentage of orginal raster size for smaller thumbnail
    large : float
        percentage of original raster size for larger thumbnail

    """
    outfile = infile[:-4] + '-thumb-large.png'
    cmd = f'gdal_translate -of PNG -r cubic -outsize {large}% 0 {infile} {outfile}'
    print(cmd)
    os.system(cmd)
    outfile = infile[:-4] + '-thumb-small.png'
    cmd = f'gdal_translate -of PNG -r cubic -outsize {small}% 0 {infile} {outfile}'
    print(cmd)
    os.system(cmd)


def make_leaflet_tiles(infile):
    """Create WMTS tiles for use with leaflet.js library.

    Currently, gdal script gdal2tiles.py is called to do this.

    Parameters
    ----------
    infile : str
        single-band raster file recognized by GDAL

    """
    cmd = f'gdal2tiles.py -w leaflet -z 6-12 {infile}'
    print(cmd)
    os.system(cmd)


def extract_band(infile, band):
    """Create WMTS tiles for use with leaflet.js library.

    Currently, gdal script gdal2tiles.py is called to do this.

    Parameters
    ----------
    infile : str
        single-band raster file recognized by GDAL

    """
    cmd = f'gdal_translate -of VRT -b {band} -a_nodata 0.0 {infile} tmp.vrt'
    print(cmd)
    os.system(cmd)


def make_overviews():
    """Create internal overviews in cloud-optimized geotiff.

    Currently, gdal script gdaladdo is called to do this.

    """
    cmd = 'gdaladdo tmp.vrt 2 4 8 16 32'
    print(cmd)
    os.system(cmd)


def make_cog(outfile):
    """Create single-band cloud-optimized geotiff.

    Currently, gdal_tanslate to do this.

    """
    cmd = f'gdal_translate tmp.vrt {outfile} -co COMPRESS=DEFLATE \
-co TILED=YES -co BLOCKXSIZE=512 -co BLOCKYSIZE=512 \
-co COPY_SRC_OVERVIEWS=YES  --config GDAL_TIFF_OVR_BLOCKSIZE 512'
    print(cmd)
    os.system(cmd)


def cleanUp():
    """Remove intermediate and auxiliary files."""
    print('removing temporary files...')
    cmd = 'rm tmp* *aux.xml'
    print(cmd)
    os.system(cmd)


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

<a href="amplitude-cog-rgb-thumb-large.png">
  <img src="amplitude-cog-rgb-thumb-small.png">
</a>
<a href="unwrapped-phase-cog-rgb-thumb-large.png">
  <img src="unwrapped-phase-cog-rgb-thumb-small.png">
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
