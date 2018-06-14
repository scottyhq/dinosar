dinosar Quickstart
==================

Here are simple examples of how to use ``dinosar``. If you haven't installed it yet
see installation.rst.

query ASF archive
-----------------

Run the following code::

  get_inventory_asf.py -r 0.610607 1.047751 -78.195699 -77.522255

Plot the results with::
  plot_inventory_asf.py -i query.geojson
