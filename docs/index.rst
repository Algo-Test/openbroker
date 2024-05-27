.. Open Broker documentation master file, created by
   sphinx-quickstart on Mon Jan  8 18:11:33 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Open Broker's documentation!
=======================================


:doc:`tutorial`
  A quick tutorial to get you up and running with OpenBroker.

:doc:`api_reference`
  The complete API documentation --- all you need to know about OpenBroker's API.

:doc:`changelog`
  The history of changes in OpenBroker.


.. toctree::
   :maxdepth: 2
   :numbered:
   :hidden:

   tutorial
   api_reference
   changelog


Testing(UAT)
==================

We have an UAT environment to test out the orders interface. 
To try the UAT environment, set an environment variable `OPENBROKER_UAT` to `True` before importing any files from the library.

.. code-block:: python

    import os
    os.environ['OPENBROKER_UAT'] = 'True'

    from openbroker import OpenBroker

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
