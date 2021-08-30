==============
solvency2-data
==============


.. image:: https://img.shields.io/pypi/v/solvency2_data.svg
        :target: https://pypi.python.org/pypi/solvency2-data
        :alt: Pypi Version
.. image:: https://img.shields.io/travis/wjwillemse/solvency2-data.svg
        :target: https://app.travis-ci.com/github/wjwillemse/solvency2-data
        :alt: Build Status
.. image:: https://readthedocs.org/projects/solvency2-data/badge/?version=latest
        :target: https://solvency2-data.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status
.. image:: https://img.shields.io/badge/License-MIT/X-blue.svg
        :target: https://github.com/DeNederlandscheBank/solvency2-data/blob/master/LICENSE
        :alt: License



Package for reading the Solvency 2 Risk-Free Interest Rate Term Structures from the zip-files on the EIOPA website and deriving the term structures for alternative extrapolations.

* Free software: MIT/X license
* Documentation: https://solvency2-data.readthedocs.io.

.. image:: https://raw.githubusercontent.com/wjwillemse/solvency2-data/master/docs/rfr.gif?raw=true
   :alt: click for animation
   :align: left

Features
--------

Here is what the package does:

- Downloading and extracting the zip-files from the EIOPA website
- Store the financial data in a local database
- Reading the term structures from Excel-files into Pandas DataFrames
- Deriving term structures with other parameters for alternative extrapolations

Overview
--------

To install the package enter the following in the command prompt.

::

    pip install solvency2-data
    

Contributors
------------

| Willem Jan Willemse <https://github.com/wjwillemse>
| Peter Davidson <https://github.com/pdavidsonFIA>
