# -*- coding: utf-8 -*-

"""
Main module.

"""

from datetime import datetime, timedelta
from urllib.request import urlopen
import zipfile
import os
from os.path import join

import pandas as pd

from solvency2_data.util import get_config
from solvency2_data.scraping import eiopa_link

countries_list = [
    "Euro",
    "Austria",
    "Belgium",
    "Bulgaria",
    "Croatia",
    "Cyprus",
    "Czech Republic",
    "Denmark",
    "Estonia",
    "Finland",
    "France",
    "Germany",
    "Greece",
    "Hungary",
    "Iceland",
    "Ireland",
    "Italy",
    "Latvia",
    "Liechtenstein",
    "Lithuania",
    "Luxembourg",
    "Malta",
    "Netherlands",
    "Norway",
    "Poland",
    "Portugal",
    "Romania",
    "Russia",
    "Slovakia",
    "Slovenia",
    "Spain",
    "Sweden",
    "Switzerland",
    "United Kingdom",
    "Australia",
    "Brazil",
    "Canada",
    "Chile",
    "China",
    "Colombia",
    "Hong Kong",
    "India",
    "Japan",
    "Malaysia",
    "Mexico",
    "New Zealand",
    "Singapore",
    "South Africa",
    "South Korea",
    "Taiwan",
    "Thailand",
    "Turkey",
    "United States",
]

currencies = [
    "EUR",
    "BGN",
    "HRK",
    "CZK",
    "DKK",
    "HUF",
    "LIC",
    "PLN",
    "NOK",
    "RON",
    "RUB",
    "SEK",
    "CHF",
    "GBP",
    "AUD",
    "BRL",
    "CAD",
    "CLP",
    "CNY",
    "COP",
    "HKD",
    "INR",
    "JPY",
    "MYR",
    "MXN",
    "NZD",
    "SGD",
    "ZAR",
    "KRW",
    "TWD",
    "THB",
    "TRY",
    "USD",
]


def RFR_reference_date(input_date: str = None, cache: dict = {}) -> dict:
    """
    Returns the closest reference date prior to an input_date
    The reference_date is put in a dict with the original input_date

    If no input_date is given then today() is used
    >>> RFR_reference_date('2018-12-31')
    {'input_date': '2018-12-31', 'reference_date':
    '20171231'}
    >>> RFR_reference_date('2018-12-31')
    {'input_date': '2018-12-31', 'reference_date':
    '20180731'}

    Args:
        input_date:

    Returns
        The cache with the data

    """

    if input_date is not None:
        reference_date = datetime.strptime(input_date, '%Y-%m-%d')
    else:
        reference_date = None

    if (reference_date is None) or (reference_date > datetime.today()):
        reference_date = datetime.today()

        if reference_date.day < 5:
            reference_date = reference_date.replace(day=1) - timedelta(days=1)
    else:
        reference_date = reference_date + timedelta(days=1)

    # to do : check if end of month
    reference_date = reference_date.replace(day=1) - timedelta(days=1)

    cache["input_date"] = reference_date.strftime("%Y-%m-%d")
    cache["reference_date"] = cache["input_date"].replace('-', '')

    return cache


def RFR_dict(input_date: str = None, cache: dict = {}) -> dict:
    """
    Returns a dict with url and filenames from the EIOPA website based on the
    input_date

    >>> RFR_dict(datetime(2018,1,1))
    {'input_date': datetime.datetime(2018, 1, 1, 0, 0),
     'reference_date': '20171231',
     'url': 'https://eiopa.europa.eu/Publications/Standards/',
     'path_zipfile': '',
     'name_zipfile': 'EIOPA_RFR_20171231.zip',
     'path_excelfile': '',
     'name_excelfile': 'EIOPA_RFR_20171231_Term_Structures.xlsx'}

    Args:
        input_date: required date
        cache: the cache with the data

    Returns
        The updated cache with the data

    """
    cache = RFR_reference_date(input_date, cache)
    cache["name_excelfile"] = (
        "EIOPA_RFR_" + cache["reference_date"] + "_Term_Structures" + ".xlsx"
    )
    cache["name_excelfile_spreads"] = (
        "EIOPA_RFR_" + cache["reference_date"] + "_PD_Cod" + ".xlsx"
    )
    return cache


def download_RFR(input_date: str = None, cache: dict = {}) -> dict:
    """
    Downloads the zipfile from the EIOPA website and extracts the Excel file

    Returns the cache with info
    >>> download_RFR('2018-12-31')
    {'name_excelfile': 'EIOPA_RFR_20171231_Term_Structures.xlsx',
     'input_date': '2018-12-31',
     'url': 'https://eiopa.europa.eu/Publications/Standards/',
     'path_zipfile': '',
     'name_zipfile': 'EIOPA_RFR_20171231.zip',
     'path_excelfile': '',
     'reference_date': '20171231',

    Args:
        input_date: required date
        cache: the cache with the data

    Returns
        The updated cache with the data

    """
    cache = RFR_dict(input_date, cache)

    if not (
        os.path.isfile(join(cache["path_excelfile"], cache["name_excelfile"]))
    ) or not (
        os.path.isfile(join(cache["path_excelfile"], cache["name_excelfile_spreads"]))
    ):
        # determine correct url and zipfile
        cache["url"] = eiopa_link(cache["input_date"], data_type="rfr")
        cache["name_zipfile"] = os.path.basename(cache["url"]).split("filename=")[-1]

        # download file
        request = urlopen(cache["url"])

        # save zip-file
        output = open(join(cache["path_zipfile"], cache["name_zipfile"]), "wb")
        output.write(request.read())
        output.close()

        # extract file from zip-file
        zip_ref = zipfile.ZipFile(join(cache["path_zipfile"], cache["name_zipfile"]))
        zip_ref.extract(cache["name_excelfile"], cache["path_excelfile"])
        zip_ref.extract(cache["name_excelfile_spreads"], cache["path_excelfile"])
        zip_ref.close()

        # remove zip file
        # os.remove(cache['path_zipfile'] + cache["name_zipfile"])

    return cache


def read_spreads(xls: pd.ExcelFile, cache: dict = {}) -> dict:
    """
    Function to read spreads from Excel file

    Args:
        xls: the Excel object
        cache: the cache with the data

    Returns
        The updated cache with the data

    """
    cache["financial fundamental spreads"] = {}
    for name in currencies:
        if name in xls.sheet_names:
            df = pd.read_excel(
                io=xls,
                sheet_name=name,
                header=1,
                usecols="W:AC",
                nrows=30,
                skiprows=8,
                names=[0, 1, 2, 3, 4, 5, 6],
            )
            df.index = range(1, 31)
            cache["financial fundamental spreads"][name] = df

    cache["non-financial fundamental spreads"] = {}
    for name in currencies:
        if name in xls.sheet_names:
            df = pd.read_excel(
                io=xls,
                sheet_name=name,
                header=1,
                usecols="W:AC",
                nrows=30,
                skiprows=48,
                names=[0, 1, 2, 3, 4, 5, 6],
            )
            df.index = range(1, 31)
            cache["non-financial fundamental spreads"][name] = df

    return cache


def read_govies(xls, cache: dict = {}) -> dict:
    """
    Function to read government spreads from Excel file

    Args:
        xls: the Excel object
        cache: the cache with the data

    Returns
        The updated cache with the data

    """
    cache["central government fundamental spreads"] = None
    for name in ["FS_Govts"]:
        if name in xls.sheet_names:
            df = pd.read_excel(
                io=xls,
                sheet_name=name,
                usecols="B:AF",
                nrows=53,
                index_col=0,
                skiprows=9,
            )
            # This line introduces a dependency on the spots
            # df.index = cache['RFR_spot_no_VA'].columns
            cache["central government fundamental spreads"] = df.T

    return cache


def read_spot(xls, cache: dict = {}) -> dict:
    """
    Function to read spot rates from Excel file

    Args:
        xls: the Excel object
        cache: the cache with the data

    Returns
        The updated cache with the data

    """
    for name in [
        "RFR_spot_no_VA",
        "RFR_spot_with_VA",
        "Spot_NO_VA_shock_UP",
        "Spot_NO_VA_shock_DOWN",
        "Spot_WITH_VA_shock_UP",
        "Spot_WITH_VA_shock_DOWN",
    ]:
        if name in xls.sheet_names:
            df = pd.read_excel(
                io=xls, sheet_name=name, header=1, nrows=158, index_col=1
            )
            # drop unnamed columns from the excel file
            for col in df.columns:
                if "Unnamed:" in col:
                    df = df.drop(col, axis=1)
            df.loc["VA"].fillna(0, inplace=True)
            df = df.iloc[8:]
            df.index.names = ["Duration"]
            cache[name] = df

    return cache


def read_meta(xls, cache: str = {}) -> dict:
    """
    Function to read meta data from Excel file

    Args:
        xls: the Excel object
        cache: the cache with the data

    Returns
        The updated cache with the data

    """
    df_meta = pd.read_excel(
        xls, sheet_name="RFR_spot_with_VA", header=1, index_col=1, skipfooter=150
    )
    # drop unnamed columns from the excel file
    for col in df_meta.columns:
        if "Unnamed:" in col:
            df_meta = df_meta.drop(col, axis=1)

    df_meta.loc["VA", :].fillna(0, inplace=True)
    df_meta = df_meta.iloc[0:8]
    df_meta.index.names = ["meta"]
    df_meta.index = df_meta.index.fillna("Info")

    # Reference date is not strictly part of meta
    # df_append = pd.DataFrame(index=['reference date'],
    #                          columns=df_meta.columns)
    # # df_append.loc['reference date'] = cache["reference_date"]
    # df_meta = df_meta.append(df_append)

    cache["meta"] = df_meta

    return cache


def read(input_date=None, path: str = None) -> dict:
    """
    Reads the RFR for input_date and stores data in path

    Args:
        input_date: the required input date
        path: the path to the excel file

    Returns
        The cache with the data

    """

    if path is None:
        # look in current directory for .cfg file
        # if not exists then take the .cfg file in the package directory
        config = get_config().get("Directories")

        path_zipfile = config.get("zip_files")
        path_excelfile = config.get("excel_files")
    else:
        path_zipfile = path
        path_excelfile = path

    cache = {"path_zipfile": path_zipfile, "path_excelfile": path_excelfile}

    cache = download_RFR(input_date, cache)
    xls = pd.ExcelFile(
        join(cache["path_excelfile"], cache["name_excelfile"]), engine="openpyxl"
    )
    cache = read_meta(xls, cache)
    cache = read_spot(xls, cache)
    xls_spreads = pd.ExcelFile(
        join(cache["path_excelfile"], cache["name_excelfile_spreads"]),
        engine="openpyxl",
    )
    cache = read_spreads(xls_spreads, cache)
    cache = read_govies(xls_spreads, cache)

    return cache
