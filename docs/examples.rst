Examples
========

``dinosar`` was designed with Cloud computing in mind, but it is also useful for lots of ordinary tasks, such as querying the Alaska Satellite Facility archive. Here you'll find some short examples of using ``dinosar``. Assuming you've followed the installation instructions, launch dinosar with::

  conda activate dinosar


Query ASF Archive and plot results
----------------------------------

Let's examine the Sentinel-1 archive covering Yakima, WA::

    get_inventory_asf.py -r 46.51 46.53 -120.47 -120.45
    plot_inventory.py -i query.geojson


Download a DEM for processing
-----------------------------

InSAR processing requires a DEM, ISCE can download 30m SRTM data based on geographic bounds. After downloading, you may want to run ``fixImageXml.py`` or ``upsampleDem.py``::

    start_isce
    dem.py -b 45 48 -122 -119


Prepare InSAR processing
------------------------

To run ISCE topsApp.py you need to download SLC data from ASF vertex for two dates, as well as precise orbit data files, and create a processing settings file in XML format. ``dinosar`` simplifies this setup with a script. It's common to use similar settings for many interferograms, so you can set processing parameters in a simple YML template file::

    prep_topsApp_local.py -i query.geojson -m 20180706 -s 20180624 -p 115 -t topsApp-dinosar-template.yml


Note the template file can be found wherever dinosar was installed (e.g ``dinosar/isce/topsApp-dinosar-template.yml``)


Process interferogram
---------------------

Because SLC data takes up a lot of space, files are not downloaded automatically. Instead the prep_topsApp_local.py script creates a file with the download urls to download them for processing. Once the SLC data and orbit files are downloaded to the local directory you can generate an interferogram::

    cd int-20180706-20180624
    start_isce
    aria2c -x 8 -s 8 -i download-links.txt
    topsApp.py --steps 2>&1 | tee topsApp.log


Process single interferogram on AWS
----------------------------

Instead of processing on your local machine, process on AWS (assumes AWS account and resources properly configured). Run the following from the interferogram directory **TODO: simplify this**::

  aws batch submit-job --job-name test-single  --job-queue isce-single-c4-ondemand  --job-definition run-single:2 --parameters 'int_s3=s3://int-20160722-20160628,dem_s3=s3://isce-dems' --container-overrides 'environment=[{name=NASAUSER,value=CHANGE},{name=NASAPASS,value=CHANGE}]'


Batch process interferograms on AWS
-----------------------------------

Currently, ``dinosar`` has the ability to process a list of interferograms in parallel. Note, these are not aligned to a common master geometry, but rather processed in a pairwise fashion. You should specify a common geocode bounding box so that all interferograms end up on the same grid. Generally, before submitting a batch job, we recommend::

  aws s3 mb s3://batch-uniongap --region us-east-1
  aws s3 cp . s3://batch-uniongap/dem/ --recursive --exclude "*" --include "dem*"

To pull the dem back down to your local computer::

  aws s3 sync s3://batch-uniongap/dem/ .

To launch the batch job::

  aws batch submit-job --job-name test-batch-array--job-queue isce-batch-c4-ondemand --job-definition run-batch:1 --array-properties size=3 --parameters 'batch_s3=s3://test-batch-array' --container-overrides 'environment=[{name=NASAUSER,value=CHANGE},{name=NASAPASS,value=CHANGE}]'
