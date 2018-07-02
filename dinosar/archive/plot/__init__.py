"""Functions for plotting dinosar inventory GeoDataFames.

Notes
-----
This file contains library functions. To run as a script use::

    $ plot_inventory.py --help


"""
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
# import matplotlib.patheffects as PathEffects
from matplotlib.dates import YearLocator, MonthLocator  # DateFormatter
from pandas.plotting import table
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from cartopy.io.img_tiles import GoogleTiles
# from owslib.wmts import WebMapTileService


def plot_map(gf, snwe, vectorFile=None, zoom=8):
    """Plot dinosar inventory on a static map.

    Parameters
    ----------
    gf :  GeoDataFrame
        A geopandas GeoDataFrame
    snwe : list
        bounding coordinates [south, north, west, east].
    vectorFile: str
        path to region of interest polygon
    zoom: int
        zoom level for WMTS

    """
    pad = 1
    S, N, W, E = snwe
    plot_CRS = ccrs.PlateCarree()
    geodetic_CRS = ccrs.Geodetic()
    x0, y0 = plot_CRS.transform_point(W-pad, S-pad, geodetic_CRS)
    x1, y1 = plot_CRS.transform_point(E+pad, N+pad, geodetic_CRS)

    fig, ax = plt.subplots(figsize=(8, 8), dpi=100,
                           subplot_kw=dict(projection=plot_CRS))

    ax.set_xlim((x0, x1))
    ax.set_ylim((y0, y1))
    url = 'http://tile.stamen.com/terrain/{z}/{x}/{y}.png'
    tiler = GoogleTiles(url=url)
    # NOTE: going higher than zoom=8 is slow...
    ax.add_image(tiler, zoom)

    states_provinces = cfeature.NaturalEarthFeature(
        category='cultural',
        name='admin_1_states_provinces_lines',
        scale='110m',
        facecolor='none')
    ax.add_feature(states_provinces, edgecolor='k', linestyle=':')
    ax.coastlines(resolution='10m', color='black', linewidth=2)
    ax.add_feature(cfeature.BORDERS)

    # Add region of interest polygon in specified
    if vectorFile:
        tmp = gpd.read_file(vectorFile)
        ax.add_geometries(tmp.geometry.values,
                          ccrs.PlateCarree(),
                          facecolor='none',
                          edgecolor='m',
                          lw=2,
                          linestyle='dashed')

    orbits = gf.relativeOrbit.unique()
    colors = plt.cm.jet(np.linspace(0, 1, orbits.size))

    for orbit, color in zip(orbits, colors):
        df = gf.query('relativeOrbit == @orbit')
        poly = df.geometry.cascaded_union

        if df.flightDirection.iloc[0] == 'ASCENDING':
            linestyle = '--'
            xpos, ypos = poly.centroid.x, poly.bounds[3]
        else:
            linestyle = '-'
            xpos, ypos = poly.centroid.x, poly.bounds[1]

        ax.add_geometries([poly],
                          ccrs.PlateCarree(),
                          facecolor='none',
                          edgecolor=color,
                          lw=2,
                          linestyle=linestyle)
        ax.text(xpos, ypos, orbit, color=color, fontsize=16, fontweight='bold',
                transform=geodetic_CRS)

    gl = ax.gridlines(plot_CRS, draw_labels=True,
                      linewidth=0.5, color='gray', alpha=0.5, linestyle='-')
    gl.xlabels_top = False
    gl.ylabels_left = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER

    plt.title('Orbital Footprints')
    plt.savefig('map.pdf', bbox_inches='tight')


def plot_timeline_table(gf):
    """Plot dinosar inventory acquisitions as a timeline with a table.

    Parameters
    ----------
    gf :  GeoDataFrame
        A geopandas GeoDataFrame

    """
    dfA = gf.query('platform == "Sentinel-1A"')
    dfAa = dfA.query(' flightDirection == "ASCENDING" ')
    dfAd = dfA.query(' flightDirection == "DESCENDING" ')
    dfB = gf.query('platform == "Sentinel-1B"')
    dfBa = dfB.query(' flightDirection == "ASCENDING" ')
    dfBd = dfB.query(' flightDirection == "DESCENDING" ')

    # summary table
    dfS = gpd.pd.DataFrame(index=gf.relativeOrbit.unique())
    dfS['Start'] = gf.groupby('relativeOrbit').sceneDateString.min()
    dfS['Stop'] = gf.groupby('relativeOrbit').sceneDateString.max()
    dfS['Dates'] = gf.groupby('relativeOrbit').sceneDateString.nunique()
    dfS['Frames'] = gf.groupby('relativeOrbit').sceneDateString.count()
    dfS['Direction'] = gf.groupby('relativeOrbit').flightDirection.first()
    dfS['UTC'] = gf.groupby('relativeOrbit').utc.first()
    dfS.sort_index(inplace=True, ascending=False)
    dfS.index.name = 'Orbit'

    # Same colors as map
    orbits = gf.relativeOrbit.unique()
    colors = plt.cm.jet(np.linspace(0, 1, orbits.size))

    fig, ax = plt.subplots(figsize=(11, 8.5))
    plt.scatter(dfAa.timeStamp.values, dfAa.orbitCode.values,
                c=colors[dfAa.orbitCode.values], cmap='jet',
                s=60, facecolor='none', label='S1A')
    plt.scatter(dfBa.timeStamp.values, dfBa.orbitCode.values,
                c=colors[dfBa.orbitCode.values], cmap='jet',
                s=60, facecolor='none', marker='d', label='S1B')
    plt.scatter(dfAd.timeStamp.values, dfAd.orbitCode.values,
                c=colors[dfAd.orbitCode.values], cmap='jet',
                s=60, label='S1A')
    plt.scatter(dfBd.timeStamp.values, dfBd.orbitCode.values,
                c=colors[dfBd.orbitCode.values], cmap='jet',
                s=60, marker='d', label='S1B')

    plt.yticks(gf.orbitCode.unique(), gf.relativeOrbit.unique())

    table(ax, dfS, loc='top', zorder=10, fontsize=12,
          cellLoc='center', rowLoc='center',
          bbox=[0.1, 0.7, 0.6, 0.3])  # [left, bottom, width, height])

    ax.xaxis.set_minor_locator(MonthLocator())
    ax.xaxis.set_major_locator(YearLocator())
    plt.legend(loc='upper right')
    plt.ylim(-1, orbits.size+3)
    plt.ylabel('Orbit Number')
    fig.autofmt_xdate()
    plt.title('Acquisition Timeline')
    plt.savefig('timeline_with_table.pdf', bbox_inches='tight')


def plot_timeline_sentinel(gf):
    """Plot dinosar inventory acquisitions as a timeline.

    Parameters
    ----------
    gf :  GeoDataFrame
        A geopandas GeoDataFrame

    """
    dfA = gf.query('platform == "Sentinel-1A"')
    dfAa = dfA.query(' flightDirection == "ASCENDING" ')
    dfAd = dfA.query(' flightDirection == "DESCENDING" ')
    dfB = gf.query('platform == "Sentinel-1B"')
    dfBa = dfB.query(' flightDirection == "ASCENDING" ')
    dfBd = dfB.query(' flightDirection == "DESCENDING" ')

    # Same colors as map
    orbits = gf.relativeOrbit.unique()
    colors = plt.cm.jet(np.linspace(0, 1, orbits.size))

    fig, ax = plt.subplots(figsize=(11, 8.5))
    plt.scatter(dfAa.timeStamp.values, dfAa.orbitCode.values,
                edgecolors=colors[dfAa.orbitCode.values], facecolors='None',
                cmap='jet', s=60, label='Asc S1A')
    plt.scatter(dfBa.timeStamp.values, dfBa.orbitCode.values,
                edgecolors=colors[dfBa.orbitCode.values], facecolors='None',
                cmap='jet', s=60, marker='d', label='Asc S1B')
    plt.scatter(dfAd.timeStamp.values, dfAd.orbitCode.values,
                c=colors[dfAd.orbitCode.values], cmap='jet',
                s=60, label='Dsc S1A')
    plt.scatter(dfBd.timeStamp.values, dfBd.orbitCode.values,
                c=colors[dfBd.orbitCode.values], cmap='jet',
                s=60, marker='d', label='Dsc S1B')

    plt.yticks(gf.orbitCode.unique(), gf.relativeOrbit.unique())

    ax.xaxis.set_minor_locator(MonthLocator())
    ax.xaxis.set_major_locator(YearLocator())
    plt.legend(loc='lower right')
    plt.ylim(-1, orbits.size)
    plt.ylabel('Orbit Number')
    fig.autofmt_xdate()
    plt.title('Acquisition Timeline')
    plt.savefig('timeline.pdf', bbox_inches='tight')


def plot_timeline(gf, platform1, platform2):
    """Plot dinosar inventory acquisitions as a timeline.

    Parameters
    ----------
    gf :  GeoDataFrame
        A geopandas GeoDataFrame

    """
    dfA = gf.query('platform == @platform1')
    dfB = gf.query('platform == @platform2')

    # Same colors as map
    orbits = gf.relativeOrbit.unique()
    colors = plt.cm.jet(np.linspace(0, 1, orbits.size))

    fig, ax = plt.subplots(figsize=(11, 8.5))
    plt.scatter(dfA.timeStamp.values, dfA.orbitCode.values,
                edgecolors=colors[dfA.orbitCode.values], facecolors='None',
                cmap='jet', s=60, label=f'{platform1}')
    plt.scatter(dfB.timeStamp.values, dfB.orbitCode.values,
                edgecolors=colors[dfB.orbitCode.values], facecolors='None',
                cmap='jet', s=60, marker='d', label=f'{platform2}')

    plt.yticks(gf.orbitCode.unique(), gf.relativeOrbit.unique())

    ax.xaxis.set_minor_locator(MonthLocator())
    ax.xaxis.set_major_locator(YearLocator())
    plt.legend(loc='lower right')
    plt.ylim(-1, orbits.size)
    plt.ylabel('Orbit Number')
    fig.autofmt_xdate()
    plt.title('Acquisition Timeline')
    plt.savefig('timeline.pdf', bbox_inches='tight')
