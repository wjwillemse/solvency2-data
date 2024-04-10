# solvency2-data

[![Documentation](https://readthedocs.org/projects/solvency2-data/badge)](https://solvency2-data.readthedocs.io)
[![image](https://img.shields.io/pypi/v/solvency2-data.svg)](https://pypi.python.org/pypi/solvency2-data)
[![image](https://img.shields.io/pypi/pyversions/solvency2-data.svg)](https://pypi.python.org/pypi/solvency2-data)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Python Package for reading the Solvency 2 Risk-Free Interest Rate Term
Structures from the zip-files on the EIOPA website and deriving the term
structures for alternative extrapolations.

-   Free software: MIT/X license
-   Documentation: <https://solvency2-data.readthedocs.io>.

![click for animation](https://raw.githubusercontent.com/wjwillemse/solvency2-data/master/docs/rfr.gif?raw=true)

## Features

Here is what the package does:

-   Downloading and extracting the zip-files from the EIOPA website
-   Store the financial data in a local database
-   Reading the term structures from Excel-files into Pandas DataFrames
-   Deriving term structures with other parameters for alternative
    extrapolations

## Contributors

* Willem Jan Willemse <https://github.com/wjwillemse>
* Peter Davidson <https://github.com/pdavidsonFIA>
