"""
Downloads rfr and stores in sqlite database for future reference

"""
import os
import zipfile
import pandas as pd
import urllib
from datetime import date

from solvency2_data.sqlite_handler import EiopaDB
from solvency2_data.util import get_config
from solvency2_data.rfr import read_spot, read_spreads
from solvency2_data.scraping import eiopa_link
from solvency2_data.sqlite_handler import create_connection, create_eiopa_db


def get_workspace():
    """ Get the workspace for saving xl and the database """
    config = get_config().get('Directories')
    path_db = config.get('db_folder')
    database = os.path.join(path_db, "eiopa.db")
    path_raw = config.get('raw_data')
    return {'database': database, 'raw_data': path_raw}


def download_file(url: str,
                  raw_folder,  # url of the file to download
                  filename=''  # file path+name to give to the file to download
                  ):
    """
    this function downloads a file and give it a name if not explicitly specified.
    """

    if filename:
        extension = url[(url.rfind(".")):]
        if extension not in filename:
            filename = filename + extension
        else:
            pass
    else:
        # if filename not specified, then the file name will be the original file name
        filename = url[(url.rfind("/") + 1):]

    target_file = os.path.join(raw_folder, filename)

    if os.path.isfile(target_file):
        print("file already exists in this location, not downloading")

    else:
        if not os.path.exists(raw_folder):
            os.makedirs(raw_folder)
        urllib.request.urlretrieve(url, target_file)  # simpler for file downloading
        print("file downloaded and saved in the following location: " + target_file)

    return target_file


def download_EIOPA_rates(url, ref_date, raw_folder):
    """ Download and unzip the EIOPA files """

    zip_file = download_file(url, raw_folder)

    reference_date = ref_date.strftime('%Y%m%d')

    name_excelfile = "EIOPA_RFR_" + reference_date + "_Term_Structures" + ".xlsx"
    name_excelfile_spreads = "EIOPA_RFR_" + reference_date + "_PD_Cod" + ".xlsx"

    with zipfile.ZipFile(zip_file) as zipobj:
        zipobj.extract(name_excelfile, raw_folder)
        zipobj.extract(name_excelfile_spreads, raw_folder)
    return {'rfr': os.path.join(raw_folder, name_excelfile),
            'spreads': os.path.join(raw_folder, name_excelfile_spreads)}


def extract_spot_rates(rfr_filepath):
    # TODO: Complete this remap dictionary
    currency_codes_and_regions = {"EUR": "Euro", "PLN": "Poland", "CHF": "Switzerland",
                                  "USD": "United States", "GBP": "United Kingdom", "NOK": "Norway",
                                  "SEK": "Sweden", "DKK": "Denmark", "HRK": "Croatia"}
    currency_dict = dict((v, k) for k, v in currency_codes_and_regions.items())

    rates_tables = read_spot(rfr_filepath)
    rates_tables = pd.concat(rates_tables)
    rates_tables = rates_tables.rename(columns=currency_dict)[currency_dict.values()]

    label_remap = {"RFR_spot_no_VA": 'base', "RFR_spot_with_VA": 'va',
                   "Spot_NO_VA_shock_UP": 'up', "Spot_NO_VA_shock_DOWN": 'down',
                   "Spot_WITH_VA_shock_UP": 'va_up', "Spot_WITH_VA_shock_DOWN": 'va_down'}
    rates_tables = rates_tables.rename(label_remap)

    rates_tables = rates_tables.stack().rename('spot')

    rates_tables.index.names = ['scenario', 'duration', 'currency_code']
    rates_tables.index = rates_tables.index.reorder_levels([0, 2, 1])
    rates_tables = rates_tables.sort_index()
    return rates_tables


def extract_spreads(spread_filepath):
    spreads = read_spreads(spread_filepath)
    spreads_non_gov = pd.concat({i: pd.concat(spreads[i]) for i in
                                 ["financial fundamental spreads", "non-financial fundamental spreads"]})
    spreads_non_gov = spreads_non_gov.stack().rename('spread')
    spreads_non_gov.index.names = ['type', 'currency_code', 'duration', 'cc_step']
    spreads_non_gov.index = spreads_non_gov.index.reorder_levels([0, 1, 3, 2])
    spreads_non_gov = spreads_non_gov.rename(
        {"financial fundamental spreads": 'fin', "non-financial fundamental spreads": 'non_fin'})

    spreads_gov = spreads["central government fundamental spreads"].stack().rename('spread').to_frame()
    spreads_gov.index.names = ['duration', 'country_code']
    spreads_gov.index = spreads_gov.index.reorder_levels([1, 0])

    return spreads_non_gov, spreads_gov


def get_rfr(ref_date):
    # Check if DB exists, if not, create it:
    workspace = get_workspace()
    database = workspace['database']
    db = EiopaDB(database)

    # Try to SELECT the rates from DB:
    rates_sql = "SELECT * FROM rfr_raw WHERE ref_date = '" + ref_date.strftime('%Y-%m-%d') + "'"
    df = pd.read_sql(rates_sql, con=db.conn)

    if df.empty:
        url = eiopa_link(ref_date, data_type='rfr')
        set_id = db.get_set_id(url)

        files = download_EIOPA_rates(url, ref_date, workspace['raw_data'])
        rfr = extract_spot_rates(files['rfr'])
        rfr = rfr.reset_index()
        rfr['url_id'] = set_id
        rfr['ref_date'] = ref_date.strftime('%Y-%m-%d')
        rfr.to_sql('rfr_raw', con=db.conn, if_exists='append', index=False)
        df = pd.read_sql(rates_sql, con=db.conn)
    df = df.drop(columns='ref_date')
    return df


def get_spreads(ref_date):
    # Check if DB exists, if not, create it:
    workspace = get_workspace()
    database = os.path.join(workspace['db_folder'], "eiopa.db")
    if not os.path.isfile(database):
        if not os.path.exists(workspace['db_folder']):
            os.makedirs(workspace['db_folder'])
        create_eiopa_db(database)

    # Try to SELECT the rates from DB:
    spreads_sql = "SELECT * FROM spreads_raw WHERE ref_date = '" + ref_date.strftime('%Y-%m-%d') + "'"
    df = pd.read_sql(spreads_sql, con=create_connection(database))

    if df.empty:
        files = download_EIOPA_rates(ref_date, workspace['raw_data'])
        spreads, govies = extract_spreads(files['spreads'])
        spreads = spreads.reset_index()
        spreads['ref_date'] = ref_date.strftime('%Y-%m-%d')
        spreads.to_sql('spreads_raw', con=create_connection(database), if_exists='append', index=False)
        df = pd.read_sql(spreads_sql, con=create_connection(database))

    df = df.drop(columns='ref_date')
    return df


def get_govies(ref_date):
    # Check if DB exists, if not, create it:
    workspace = get_workspace()
    database = os.path.join(workspace['db_folder'], "eiopa.db")
    if not os.path.isfile(database):
        if not os.path.exists(workspace['db_folder']):
            os.makedirs(workspace['db_folder'])
        create_eiopa_db(database)

    # Try to SELECT the rates from DB:
    govies_sql = "SELECT * FROM govies_raw WHERE ref_date = '" + ref_date.strftime('%Y-%m-%d') + "'"
    df = pd.read_sql(govies_sql, con=create_connection(database))

    if df.empty:
        files = download_EIOPA_rates(ref_date, workspace['raw_data'])
        spreads, govies = extract_spreads(files['spreads'])
        govies = govies.reset_index()
        govies['ref_date'] = ref_date.strftime('%Y-%m-%d')
        govies.to_sql('govies_raw', con=create_connection(database), if_exists='append', index=False)
        df = pd.read_sql(govies_sql, con=create_connection(database))

    df = df.drop(columns='ref_date')
    return df


def get(ref_date, data_type='rfr'):
    # TODO: expand this to include other types:
    if data_type == 'rfr':
        return get_rfr(ref_date)
    else:
        return None


def full_rebuild():
    dr = pd.date_range(date(2016, 1, 31), date(2021, 7, 31), freq='M')
    for i in dr:
        rfr = get_rfr(i)
    return "Database successfully rebuilt"


def refresh():
    """ Update the local DB with any new dates not already included """
    return "Still #TODO"
