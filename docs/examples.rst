Examples
========

``dinosar`` was designed with Cloud computing in mind, but it is also useful for lots of ordinary tasks, such as querying the Alaska Satellite Facility archive. Here you'll find some short examples of using dinosar


Query ASF Archive and plot results
----------------------------------

Let's examine the Sentinel-1 archive covering Yakima, WA::

    get_inventory_asf.py -r 46.51 46.53 -120.47 -120.45
    plot_inventory.py -i query.geojson


Download a DEM for processing
-----------------------------

InSAR processing requires a DEM, which ISCE can download based on geographic bounds::

    start_isce
    dem.py -b 45 48 -122 -119


Prepare InSAR processing
------------------------

To run ISCE topsApp.py you need to download SLC data from ASF vertex for two dates, as well as precise orbit data files, and create a processing settings file in XML format. ``dinosar`` simplifies this setup with a script. It's common to use similar settings for many interferograms, so you can set processing parameters in a simple YML template file::

    prep_topsApp_local.py -i query.geojson -m 20180706 -s 20180624 -p 115 -t topsApp-template.yml


Because SLC data takes up a lot of space, files are not downloaded automatically. Instead the prep_topsApp_local.py script creates a file with the download urls to download them for processing::

    cd int-20180706-20180624
    wget -i download-links.txt


Process interferogram
---------------------

Once the SLC data and orbit files are downloaded to the local directory you can generate an interferogram::

    start_isce
    topsApp.py --steps 2>&1 | tee topsApp.log
