Examples
========

``dinosar`` was designed with Cloud computing in mind, but it is also useful for lots of ordinary tasks, such as querying the Alaska Satellite Facility archive. Here you'll find some short examples of using ``dinosar``. Assuming you've followed the installation instructions, launch dinosar with::

  conda activate dinosar


Query ASF Archive and plot results
----------------------------------

Let's examine the Sentinel-1 archive covering Yakima, Washington, USA::

    get_inventory_asf -r 46.51 46.53 -120.47 -120.45
    plot_inventory_asf -i query.geojson


Download a DEM for processing
-----------------------------

InSAR processing requires a DEM with heights relative to the WGS84 geoid, ISCE can download 30m SRTM data, apply corrections, and crop based on geographic bounds. This command passes NASA URS authentication name and password as environment variables to enable downloading from SRTM data from NASA servers::

    docker run -e NASAUSER=scottyhq -e NASAPASS=xxxxxxxxxxx -it --rm -v $PWD:/home/ubuntu dinosar/isce2:2.3.2 dem.py -c -b 45 48 -122 -119

After downloading, you may want to run ISCE utility scripts ``fixImageXml.py`` (to use a an absolute path in the xml metadata) or ``upsampleDem.py`` (to change the DEM pixel posting).

    docker run -it --rm -v $PWD:/home/ubuntu dinosar/isce2:2.3.2 upsampleDem.py -i demLat_N45_N48_Lon_W122_W119.dem.wgs84 -o demLat_N45_N48_Lon_W122_W119_15m.dem.wgs84 -f 2 2

Local processing of single interferometric pair
-----------------------------------------------

To run ISCE topsApp.py you need to download SLC data from ASF vertex for two dates, as well as precise orbit data files, and create a processing settings file in XML format. ``dinosar`` simplifies this setup with a script. It's common to use similar settings for many interferograms, so you can set processing parameters in a simple YML template file::

    prep_topsApp_local -i query.geojson -m 20180706 -s 20180624 -p 115 -t dinosar-template.yml


Where dinosar-template.yml defines parameters for the topsApp.py workflow::

    topsinsar:
      sensorname: SENTINEL1
      swaths: [1]
      azimuthlooks: 1
      rangelooks: 6
      filterstrength: 0.1
      regionofinterest: [46.45, 46.55, -120.53, -120.43]
      geocodeboundingbox: [46.45, 46.55, -120.53, -120.43]
      geocodelist: [merged/filt_topophase.unw, merged/phsig.cor, merged/topophase.cor, merged/los.rdr]
      doesd: True
      dounwrap: True
      unwrappername: snaphu_mcf
      demfilename: demLat_N45_N48_Lon_W122_W119_15m.dem.wgs84
      usegpu: False

      reference:
        safe: ''
        output directory: reference
        orbit directory: ./
        polarization: vv

      secondary:
        safe: ''
        output directory: secondary
        orbit directory: ./
        polarization: vv


Process interferogram
---------------------

Because SLC data takes up a lot of space, files are not downloaded automatically. Instead the prep_topsApp_local.py script creates a file with the download urls to download them for processing. Once the SLC data and orbit files are downloaded to the local directory you can generate an interferogram::


    export NASAUSER=changeme
    export NASAPASS=changeme
    start_isce
    cd int-20180706-20180624
    mv ../demLat_N45_N48_Lon_W122_W119_15m.dem.wgs84* .
    aria2c -x 8 -s 8 -i download-links.txt
    topsApp.py --steps 2>&1 | tee topsApp.log


Process single interferogram on AWS
-----------------------------------

Instead of processing on your local machine, process on AWS (assumes AWS account and resources properly configured - see https://aws.amazon.com/blogs/compute/creating-a-simple-fetch-and-run-aws-batch-job/). Run the following from the interferogram directory::

  aws batch submit-job --job-name test-single  --job-queue isce-single-c4-ondemand  --job-definition run-single:2 --parameters 'int_s3=s3://int-20160722-20160628,dem_s3=s3://isce-dems' --container-overrides 'environment=[{name=NASAUSER,value=CHANGE},{name=NASAPASS,value=CHANGE}]'


Batch process interferograms on AWS
-----------------------------------

``dinosar`` has the ability to process a list of interferograms in parallel. Note, these are not aligned to a common reference geometry, but rather processed in a pairwise fashion. You should specify a common geocode bounding box so that all interferograms end up on the same grid. Generally, before submitting a batch job, we recommend::

  aws s3 mb s3://batch-uniongap --region us-east-1
  aws s3 cp . s3://batch-uniongap/dem/ --recursive --exclude "*" --include "dem*"

To pull the dem back down to your local computer::

  aws s3 sync s3://batch-uniongap/dem/ .

To remove a subfolder and all contents::

  aws s3 rm s3://batch-uniongap/input/int-20180706-20180624 --recursive

To launch the batch job::

  aws batch submit-job --job-name test-batch-array--job-queue isce-batch-c4-ondemand --job-definition run-batch:1 --array-properties size=3 --parameters 'batch_s3=s3://test-batch-array' --container-overrides 'environment=[{name=NASAUSER,value=CHANGE},{name=NASAPASS,value=CHANGE}]'
