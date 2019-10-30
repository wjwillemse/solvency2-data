=============
solvency2-rfr
=============


.. image:: https://img.shields.io/pypi/v/e_solvency2_rfr.svg
        :target: https://pypi.python.org/pypi/solvency2_rfr
        :alt: Pypi Version
.. image:: https://img.shields.io/travis/DeNederlandscheBank/solvency2-rfr.svg
        :target: https://travis-ci.org/DeNederlandscheBank/solvency2-rfr
        :alt: Build Status
.. image:: https://readthedocs.org/projects/solvency2-rfr/badge/?version=latest
        :target: https://solvency2-rfr.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




Package for reading the Solvency 2 Risk-Free Interest Rate Term Structures from the zip-files on the EIOPA website and deriving the term structures for alternative extrapolations.

* Free software: MIT/X license
* Documentation: https://solvency2-rfr.readthedocs.io.


Features
--------

Here is what the package does:

- Downloading and extracting the zip-files from the EIOPA website
- Reading the term structures from Excel-files into Pandas DataFrames
- Deriving term structures with other parameters for alternative extrapolations


Overview
--------

To install the package enter the following in the command prompt.

::

    pip install solvency2-rfr
    

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
