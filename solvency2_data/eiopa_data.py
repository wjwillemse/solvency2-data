# -*- coding: utf-8 -*-

"""
Downloads rfr and stores in sqlite database for future reference

"""

import datetime
import os
import re
import zipfile
import pandas as pd
import urllib
from datetime import date
import logging

from solvency2_data.sqlite_handler import EiopaDB
from solvency2_data.util import get_config
from solvency2_data.rfr import read_spot, read_spreads, read_govies, read_meta
from solvency2_data.scraping import eiopa_link


def get_workspace() -> dict:
    """
    Retrieves workspace directories and paths from the configuration.

    Returns:
        dict: A dictionary containing workspace directories and paths.
            The dictionary includes the following keys:
                - "database": The path to the EIOPA database file.
                - "raw_data": The path to the directory containing raw data.
    """
    config = get_config().get("Directories")
    path_db = config.get("db_folder")
    database = os.path.join(path_db, "eiopa.db")
    path_raw = config.get("raw_data")
    return {"database": database, "raw_data": path_raw}


def download_file(url: str, raw_folder: str, filename: str = "") -> str:
    """
    Downloads a file from a URL and saves it in a specified folder.

    Args:
        url (str): The URL of the file to download.
        raw_folder (str): The path to the directory where the file will be saved.
        filename (str, optional): The desired filename. If not provided,
            the filename will be derived from the URL. Defaults to "".

    Returns:
        str: The path to the downloaded file.
    """
    if filename:
        extension = url[(url.rfind(".")) :]
        if extension not in filename:
            filename = filename + extension
        else:
            pass
    else:
        # if filename not specified, then the file name will be the original file name
        filename = url[(url.rfind("/") + 1) :]
        # make sure that the filename does not contain illegal characters
        filename = re.sub(r"[^\w_. -]", "_", filename)

    if filename[-4:] != ".zip":
        filename = filename + ".zip"

    target_file = os.path.join(raw_folder, filename)

    if os.path.isfile(target_file):
        logging.info("file already exists in this location, not downloading")
    else:
        if not os.path.exists(raw_folder):
            os.makedirs(raw_folder)
        urllib.request.urlretrieve(url, target_file)  # simpler for file downloading
        logging.info(
            "file downloaded and saved in the following location: " + target_file
        )

    return target_file


def download_EIOPA_rates(url: str, ref_date: str, workspace: dict = None) -> dict:
    """
    Downloads EIOPA RFR (Risk-Free Rate) files from a given URL and extracts them.

    Args:
        url (str): The URL from which to download the EIOPA RFR files.
        ref_date (str): The reference date in the format "%Y-%m-%d".
        workspace (dict, optional): A dictionary containing workspace directories and paths.
            If None, it retrieves workspace information using get_workspace() function.
            Defaults to None.

    Returns:
        dict: A dictionary containing the paths to the downloaded files.
            The dictionary includes the following keys:
                - "rfr": The path to the downloaded EIOPA RFR term structures Excel file.
                - "meta": The path to the downloaded EIOPA RFR meta Excel file.
                - "spreads": The path to the downloaded EIOPA RFR PD Cod Excel file.
                - "govies": The path to the downloaded EIOPA RFR govvies Excel file.
    """
    if workspace is None:
        workspace = get_workspace()
    raw_folder = workspace["raw_data"]
    zip_file = download_file(url, raw_folder)

    # Change format of ref_date string for EIOPA Excel files from YYYY-mm-dd to YYYYmmdd:
    reference_date = ref_date.replace("-", "")

    name_excelfile = "EIOPA_RFR_" + reference_date + "_Term_Structures" + ".xlsx"
    name_excelfile_spreads = "EIOPA_RFR_" + reference_date + "_PD_Cod" + ".xlsx"
    # Making file paths string insensitve via regex
    re_rfr = re.compile(f"(?i:{name_excelfile})")
    re_spreads = re.compile(f"(?i:{name_excelfile_spreads})")

    with zipfile.ZipFile(zip_file) as zipobj:
        for file in zipobj.namelist():
            res_rfr = re_rfr.search(file)
            res_spreads = re_spreads.search(file)
            if res_rfr:
                rfr_file = res_rfr.group(0)
                zipobj.extract(rfr_file, raw_folder)
            if res_spreads:
                spreads_file = res_spreads.group(0)
                zipobj.extract(spreads_file, raw_folder)
    return {
        "rfr": os.path.join(raw_folder, name_excelfile),
        "meta": os.path.join(raw_folder, name_excelfile),
        "spreads": os.path.join(raw_folder, name_excelfile_spreads),
        "govies": os.path.join(raw_folder, name_excelfile_spreads),
    }


def extract_spot_rates(rfr_filepath: str) -> dict:
    """
    Extracts spot rates from an EIOPA RFR Excel file.

    Args:
        rfr_filepath (str): The path to the EIOPA RFR Excel file.

    Returns:
        dict: A dictionary containing extracted spot rates.
            The dictionary includes spot rates indexed by scenario, currency code, and duration.
    """
    logging.info("Extracting spots: " + rfr_filepath)
    # TODO: Complete this remap dictionary
    currency_codes_and_regions = {
        "EUR": "Euro",
        "PLN": "Poland",
        "CHF": "Switzerland",
        "USD": "United States",
        "GBP": "United Kingdom",
        "NOK": "Norway",
        "SEK": "Sweden",
        "DKK": "Denmark",
        "HRK": "Croatia",
    }
    currency_dict = dict((v, k) for k, v in currency_codes_and_regions.items())

    xls = pd.ExcelFile(rfr_filepath, engine="openpyxl")
    rates_tables = read_spot(xls)

    rates_tables = pd.concat(rates_tables)
    rates_tables = rates_tables.rename(columns=currency_dict)[currency_dict.values()]

    label_remap = {
        "RFR_spot_no_VA": "base",
        "RFR_spot_with_VA": "va",
        "Spot_NO_VA_shock_UP": "up",
        "Spot_NO_VA_shock_DOWN": "down",
        "Spot_WITH_VA_shock_UP": "va_up",
        "Spot_WITH_VA_shock_DOWN": "va_down",
    }
    rates_tables = rates_tables.rename(label_remap)

    rates_tables = rates_tables.stack().rename("spot")

    rates_tables.index.names = ["scenario", "duration", "currency_code"]
    rates_tables.index = rates_tables.index.reorder_levels([0, 2, 1])
    rates_tables = rates_tables.sort_index()
    return rates_tables


def extract_meta(rfr_filepath: str) -> dict:
    """
    Extracts metadata from an EIOPA RFR Excel file.

    Args:
        rfr_filepath (str): The path to the EIOPA RFR Excel file.

    Returns:
        dict: A dictionary containing extracted metadata.
            The dictionary includes metadata indexed by country.
    """
    logging.info("Extracting meta data :" + rfr_filepath)
    meta = read_meta(rfr_filepath)
    meta = pd.concat(meta).T
    meta.columns = meta.columns.droplevel()
    meta.index.name = "Country"
    meta = meta.sort_index()
    return meta


def extract_spreads(spread_filepath):
    """
    Extracts spreads data from an EIOPA RFR spreads Excel file.

    Args:
        spread_filepath (str): The path to the EIOPA RFR spreads Excel file.

    Returns:
        pandas.DataFrame: A DataFrame containing extracted spreads data.
            The DataFrame includes spreads indexed by type, currency code, credit curve step, and duration.
    """
    logging.info("Extracting spreads: " + spread_filepath)
    xls = pd.ExcelFile(spread_filepath, engine="openpyxl")
    spreads = read_spreads(xls)
    spreads_non_gov = pd.concat(
        {
            i: pd.concat(spreads[i])
            for i in [
                "financial fundamental spreads",
                "non-financial fundamental spreads",
            ]
        }
    )
    spreads_non_gov = spreads_non_gov.stack().rename("spread")
    spreads_non_gov.index.names = ["type", "currency_code", "duration", "cc_step"]
    spreads_non_gov.index = spreads_non_gov.index.reorder_levels([0, 1, 3, 2])
    spreads_non_gov = spreads_non_gov.rename(
        {
            "financial fundamental spreads": "fin",
            "non-financial fundamental spreads": "non_fin",
        }
    )
    return spreads_non_gov


def extract_govies(govies_filepath):
    """
    Extracts government spreads data from an EIOPA RFR spreads Excel file.

    Args:
        govies_filepath (str): The path to the EIOPA RFR spreads Excel file containing government spreads.

    Returns:
        pandas.DataFrame or None: A DataFrame containing extracted government spreads data,
            indexed by country code and duration.
            Returns None if no government spreads are found.
    """
    logging.info("Extracting govies: " + govies_filepath)
    xls = pd.ExcelFile(govies_filepath, engine="openpyxl")
    cache = read_govies(xls)
    if cache["central government fundamental spreads"] is not None:
        spreads_gov = (
            cache["central government fundamental spreads"]
            .stack()
            .rename("spread")
            .to_frame()
        )
        spreads_gov.index.names = ["duration", "country_code"]
        spreads_gov.index = spreads_gov.index.reorder_levels([1, 0])
    else:
        logging.error("No govies found: " + govies_filepath)
        spreads_gov = None
    return spreads_gov


def extract_sym_adj(sym_adj_filepath: str, ref_date: str) -> pd.DataFrame:
    """
    Extracts symmetric adjustment data from a file.

    Args:
        sym_adj_filepath (str): The path to the file containing symmetric adjustment data.
        ref_date (str): The reference date in the format "%Y-%m-%d".

    Returns:
        pd.DataFrame or None: A DataFrame containing symmetric adjustment data.
            Returns None if there is a date mismatch between the reference date provided
            and the date in the file.
    """
    df = pd.read_excel(
        sym_adj_filepath,
        sheet_name="Symmetric_adjustment",
        usecols="E, K",
        nrows=1,
        skiprows=7,
        header=None,
        names=["ref_date", "sym_adj"],
    ).squeeze("columns")

    input_ref = ref_date
    ref_check = df.at[0, "ref_date"].strftime("%Y-%m-%d")

    if input_ref != ref_check:
        logging.warning("Date mismatch in sym_adj file: " + sym_adj_filepath)
        logging.warning(
            "Try opening this file and setting the date correctly then save and close, and rerun."
        )
        return None
    else:
        df = df.set_index("ref_date")
        return df


def add_to_db(
    ref_date: str, db: EiopaDB, data_type: str = "rfr", workspace: dict = None
):
    """
    Adds data to the EIOPA database, to use when you are missing data.

    Args:
        ref_date (str): The reference date in the format "%Y-%m-%d".
        db (EiopaDB): The EIOPA database instance.
        data_type (str, optional): The type of data to add.
            Options: "rfr" (default), "meta", "spreads", "govies", "sym_adj".
        workspace (dict, optional): A dictionary containing workspace directories and paths.
            If None, it retrieves workspace information using get_workspace() function.
            Defaults to None.

    Returns:
        None
    """
    url = eiopa_link(ref_date, data_type=data_type)
    set_id = db.get_set_id(url)

    if data_type != "sym_adj":
        files = download_EIOPA_rates(url, ref_date)
        if data_type == "rfr":
            df = extract_spot_rates(files[data_type])
        elif data_type == "meta":
            df = extract_meta(files[data_type])
        elif data_type == "spreads":
            df = extract_spreads(files[data_type])
        elif data_type == "govies":
            df = extract_govies(files[data_type])
        else:
            raise KeyError
    elif data_type == "sym_adj":
        if workspace is None:
            workspace = get_workspace()
        raw_folder = workspace["raw_data"]
        file = download_file(url, raw_folder)
        df = extract_sym_adj(file, ref_date)

    if df is not None:
        df = df.reset_index()
        df["url_id"] = set_id
        df["ref_date"] = ref_date
        df.to_sql(data_type, con=db.conn, if_exists="append", index=False)
        set_types = {"govies": "rfr", "spreads": "rfr", "meta": "rfr"}
        db.update_catalog(
            url_id=set_id,
            dict_vals={
                "set_type": set_types.get(data_type, data_type),
                "primary_set": True,
                "ref_date": ref_date,
            },
        )
    return None


def validate_date_string(ref_date):
    """
    Validates the input date string.

    Args:
        ref_date (str or datetime.date): The input date string or datetime.date object.

    Returns:
        str or None: A validated date string in the format "%Y-%m-%d".
            Returns None if the input date type is not recognized or cannot be converted.
    """
    if type(ref_date) == datetime.date:
        return ref_date.strftime("%Y-%m-%d")
    elif isinstance(ref_date, str):
        try:
            return datetime.datetime.strptime(ref_date, "%Y-%m-%d").strftime("%Y-%m-%d")
        except (TypeError, ValueError):
            logging.warning("Date type not recognised. Try datetime.date or YYYY-mm-dd")
            return None
    else:
        return None


def get(ref_date: str, data_type: str = "rfr", workspace: dict = None):
    """
    Retrieves data from the EIOPA database for a given reference date and data type.

    Args:
        ref_date (str): The reference date in the format "%Y-%m-%d".
        data_type (str, optional): The type of data to retrieve.
            Options: "rfr" (default), "meta", "spreads", "govies", "sym_adj".
        workspace (dict, optional): A dictionary containing workspace directories and paths.
            If None, it retrieves workspace information using get_workspace() function.
            Defaults to None.

    Returns:
        pandas.DataFrame or None: A DataFrame containing retrieved data.
            Returns None if no data is found for the given reference date and data type.
    """
    # Validate the provided ref_date:
    ref_date = validate_date_string(ref_date)
    # Check if DB exists, if not, create it:
    if workspace is None:
        workspace = get_workspace()
    database = workspace["database"]
    db = EiopaDB(database)

    sql_map = {
        "rfr": "SELECT * FROM rfr WHERE ref_date = '" + ref_date + "'",
        "meta": "SELECT * FROM meta WHERE ref_date = '" + ref_date + "'",
        "spreads": "SELECT * FROM spreads WHERE ref_date = '" + ref_date + "'",
        "govies": "SELECT * FROM govies WHERE ref_date = '" + ref_date + "'",
        "sym_adj": "SELECT * FROM sym_adj WHERE ref_date = '" + ref_date + "'",
    }
    sql = sql_map.get(data_type)
    df = pd.read_sql(sql, con=db.conn)
    if df.empty:
        add_to_db(ref_date, db, data_type)
        df = pd.read_sql(sql, con=db.conn)
    if not df.empty:
        df = df.drop(columns=["url_id", "ref_date"])
        return df
    else:
        return None


def refresh():
    """
    Refreshes the EIOPA database by updating data for each month from January 2016 to the current month.

    Returns:
        str: A message indicating that the database has been successfully rebuilt.
    """
    dr = pd.date_range(date(2016, 1, 31), date.today(), freq="M")
    # dr = pd.date_range(date(2021, 11, 30), date.today(), freq="M")
    for ref_date in dr:
        for data_type in ["rfr", "meta", "spreads", "govies", "sym_adj"]:
            _ = get(ref_date.date(), data_type)
    return "Database successfully rebuilt"
