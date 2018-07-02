import dinosar.isce as dice
# from dinosar.archive import asf
import os.path


def test_write_topsApp_xml():
    """Make sure directory is create with ncessary and valid files."""
    inputDict = {'common': {'poeorb': True,
                            'roi': [0.61, 1.04, -78.19, -77.52]}
                 'master': {}
                 'master_scenes': ['scene1.zip', 'scene2.zip'],
                 'slave_scenes': ['scene3.zip', 'scene4.zip'],
                 'dem': 'elevation.dem',
                 'gbox': [0.63, 1.08, -78.25, -77.50],
                 'swaths': [1, 2]}
    dice.write_topsApp_xml(inputDict)

    assert os.path.exists('topsApp.xml')


def test_isce2cog(url):
    """Convert isce geocoded output to cloud optimized geotiff (COG)."""
    dice.make_cog()
    # dice.make_rgb()
    # dice.make_thumbnails()
    # curl -s "http://cog-validate.radiant.earth/api/validate?url=http://path/to/my.tif"
    assert os.path.exists('coherence-cog.tif')

def test_create_cmaps():
    """Create .cpt files from matplotlib colormaps."""
    dice.make_coherence_cmap()
    dice.make_amplitude_cmap()
    dice.make_wrapped_phase_cmap()

    assert os.path.exists('amplitude-cog.cpt')
    assert os.path.exists('unwrapped-phase-cog.cpt')
    assert os.path.exists('coherence-cog.cpt')
