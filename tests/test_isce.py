"""Test functions related to running ISCE."""
import dinosar.isce as dice
# from dinosar.archive import asf
import os.path


def test_read_yml_template():
    """Read a yaml file into python ordered dictionary."""
    inputDict = dice.read_yaml_template(
                            './tests/data/topsApp-template-uniongap.yml')

    assert isinstance(inputDict, dict)
    assert inputDict['topsinsar']['azimuthlooks'] == 1
    assert inputDict['topsinsar']['master']['polarization'] == 'vv'


def test_write_topsApp_xml():
    """Make sure directory is created with necessary and valid files."""
    testDict = {'topsinsar': {'azimuthlooks': 7,
                              'filterstrength': 0.5,
                              'master': {'safe': 's1a.zip'},
                              'slave': {'safe': 's1b.zip'}
                              }
                }
    xml = dice.dict2xml(testDict)
    outfile = './tests/tmp/topsApp.xml'
    dice.write_xml(xml, outfile)

    assert os.path.exists(outfile)


def test_create_cmaps():
    """Create .cpt files from matplotlib colormaps."""
    outname = './tests/tmp/coherence-cog.cpt'
    cpt = dice.make_coherence_cmap(outname=outname)
    assert os.path.exists(cpt)

    outname = './tests/tmp/unwrapped-cog.cpt'
    cpt = dice.make_wrapped_phase_cmap(outname=outname)
    assert os.path.exists(cpt)

    outname = './tests/tmp/amplitude-cog.cpt'
    cpt = dice.make_amplitude_cmap(outname=outname)
    assert os.path.exists(cpt)
