=============
solvency2-rfr
=============


.. image:: https://img.shields.io/pypi/v/e_solvency2_rfr.svg
        :target: https://pypi.python.org/pypi/solvency2_rfr

.. image:: https://img.shields.io/travis/DeNederlandscheBank/solvency2-rfr.svg
        :target: https://travis-ci.org/DeNederlandscheBank/solvency2-rfr

.. image:: https://readthedocs.org/projects/solvency2-rfr/badge/?version=latest
        :target: https://solvency2-rfr.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




Package for reading the Solvency 2 Risk-Free Interest Rate Term Structures from the zip-files on the EIOPA website and deriving the term structures for alternative extrapolations.

* Free software: MIT license
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
    

After installation you can use the functions in the package in for example a Jupyter notebook.

To get the term structures per 31/12/2017 enter

:: 
	d = solvency2_rfr.read(datetime(2017,12,31))

If you do not add a input datetime, i.e. solvency2_rfr.read(), then the function will use today() and you will receive the most recent published term structure.

This returns a dictionary with all the information about the term structures. The dictionary has the following keys

* 'input_date': the original date by which the function was called is stored in the dictionary as input_date
* 'reference_date': the proper reference date generated from the input date. The reference date is the most recent end of the month prior to the input date. So if for example the input is datetime(2018, 1, 1) then the reference date is '20171231', because this the most recent end of the month prior to the input date. The reference date is a string because it is used in the name of the files to be downloaded from the EIOPA-website.
* 'url': the url of the term structures
* 'name_zipfile': the name of the zip-file 
* 'name_excelfile': the name of the Excel-file contained in the zip-file that was downloaded
* 'metadata': the information per term structure contained in the Excel-file, 
			  - the Coupon frequency, 
			  - the Last Liquid Point,
			  - the Convergence period,
			  - the Ultimate Forward Rate, 
			  - the alpha parameter of the Smith-Wilson algorithm,
			  - the Credit Rate Adjustment,
			  - the Volatility adjustment
* 'RFR_spot_no_VA': the term structures without Volatility adjustment (a Pandas DataFrame)
* 'RFR_spot_with_VA': the term structures with Volatility adjustment (a Pandas DataFrame)

You can get the term structure without Volatility adjustment for the Euro by 

::
	rates = d['RFR_spot_no_VA']['Euro']

This returns a Pandas Series (convert it to a Numpy array to use it in calculations).

To derive a term structure with different parameters you do the following. First define the liquid maturities of the term structure, together with a dictionary of rates. Then use the smith_wilson function.

::
	liquid_maturities = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20]
	rates = d['RFR_spot_no_VA']['Euro']
	ratesin = {num: float(rates[num]) for num in liquid_maturities}

	alt_curve = smith_wilson(liquid_maturities = liquid_maturities,
             				 RatesIn = ratesin, 
             	 			 nrofcoup = d['metadata'].loc[:, 'Euro'].Coupon_freq, 
             	 			 cra = 0,
             	 			 ufr = 0,
             	 			 T2  = d['metadata'].loc[:, 'Euro'].LLP + 
                       		 d['metadata'].loc[:, 'Euro'].Convergence)

In this case, we use a ufr of zero.

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
