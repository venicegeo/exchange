================
geonode-exchange
================

.. image:: https://travis-ci.org/boundlessgeo/exchange.svg?branch=master
    :target: https://travis-ci.org/boundlessgeo/exchange

About
=====

*geonode-exchange* is a django project with GeoNode support. Boundless Exchange is a web-based platform for your content, built for your enterprise. It facilitates the creation, sharing, and collaborative use of geospatial data. For power users, advanced editing capabilities for versioned workflows via the web browser are included. Boundless Exchange is powered by GeoNode, GeoGig, OpenLayers, PostGIS and GeoServer. Boundless Exchange is designed as a platform for collaboration. You can now focus on your community – getting stakeholders quickly involved and empowering them with information. Exchange supports communal editing – allowing you to crowd-source information in an online, powerful, distributed/versioned architecture with an intuitive user interface.

Pre-requisites
==============

For installation on a CentOS 7 or RHEL 7 machine, you'll need the following packages:

* Python 2.7x
* postgresql-devel
* gdal-devel

Dependecies
===========

With the previously listed packages installed, you can now install the required Python modules
with:

    $ pip install -r ./requirements.txt

It is recommended that you use a `Virtual Environment <https://pypi.python.org/pypi/virtualenv>`_

Which can be added using:

    # yum install python-virtualenv
