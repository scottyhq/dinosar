"""Functions for ISCE software.

This module has functions that facilitate running `ISCE software` (v2.1.0).
Currently extensively uses external calls to GDAL command line scripts. Some
functions borrow from example applications distributed with ISCE.

.. _`ISCE software`: https://winsar.unavco.org/software/isce

"""

# from lxml import objectify, etree
# import os
# import matplotlib
# matplotlib.use("Agg") # Necessary for basic OS (e.g. minimal docker images)

import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
import numpy as np
import yaml


def read_yaml_template(template='topsApp-template.yml'):
    """Read yaml file."""
    with open(template, 'r') as outfile:
        defaults = yaml.load(outfile)

    return defaults


def dict2xml(dictionary, root='topsApp', topcomp='topsinsar'):
    """Convert simple dictionary to XML for ISCE."""
    def add_property(property, value):
        xml = f"        <property name={property}>{value}</property>\n"
        return xml

    def add_component(name, properties):
        xml = f"    <component name={name}>\n"
        for prop, val in properties.items():
            xml += add_property(prop, val)
        xml += f"    </component>\n"
        return xml

    dictionary = dictionary[topcomp]
    xml = f'<{root}>\n   <{topcomp}>\n'
    for key, val in dictionary.items():
        if isinstance(val, dict):
            xml += add_component(key, val)
        else:
            xml += add_property(key, val)

    xml += f'    </{topcomp}>\n</{root}>\n'

    return xml


def write_xml(xml, outname='topsApp.xml'):
    """Write xml string to a file."""
    with open(outname, 'w') as f:
        f.write(xml)


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


def make_amplitude_cmap(mapname='gray', vmin=1, vmax=1e5, ncolors=64,
                        outname='amplitude-cog.cpt'):
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
    write_cmap(outname, vals, scalarMap)

    return outname


def make_wrapped_phase_cmap(mapname='plasma', vmin=-50, vmax=50, ncolors=64,
                            wrapRate=6.28, outname='unwrapped-phase-cog.cpt'):
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

    with open(outname, 'w') as fid:
        for val, wval in zip(vals, vals_wrapped):
            cval = scalarMap.to_rgba(wval)
            fid.write('{0} {1} {2} {3} \n'.format(val,  # value
                                                  int(cval[0]*255),  # R
                                                  int(cval[1]*255),  # G
                                                  int(cval[2]*255)))  # B
        fid.write('nv 0 0 0 0 \n')  # nodata alpha

    return outname


def make_coherence_cmap(mapname='inferno', vmin=1e-5, vmax=1, ncolors=64,
                        outname='coherence-cog.cpt'):
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

    write_cmap(outname, vals, scalarMap)

    return outname


def make_cmap(infile):
    """Call correct cmap function depending on file."""
    cornames = ['phsig.cor.geo.vrt', 'topophase.cor.geo.vrt']
    phsnames = ['filt_topophase.unw.geo.vrt']

    if infile in cornames:
        cpt = make_coherence_cmap()
    elif infile in phsnames:
        cpt = make_wrapped_phase_cmap()
    else: #amplitude cmap
        cpt = make_amplitude_cmap()

    return cpt
