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
from solvency2_data.rfr import read_spot, read_spreads, read_govies, read_meta
from solvency2_data.scraping import eiopa_link


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


def download_EIOPA_rates(url, ref_date):
    """ Download and unzip the EIOPA files """
    workspace = get_workspace()
    raw_folder = workspace['raw_data']
    zip_file = download_file(url, raw_folder)

    reference_date = ref_date.strftime('%Y%m%d')

    name_excelfile = "EIOPA_RFR_" + reference_date + "_Term_Structures" + ".xlsx"
    name_excelfile_spreads = "EIOPA_RFR_" + reference_date + "_PD_Cod" + ".xlsx"

    with zipfile.ZipFile(zip_file) as zipobj:
        zipobj.extract(name_excelfile, raw_folder)
        zipobj.extract(name_excelfile_spreads, raw_folder)
    return {'rfr': os.path.join(raw_folder, name_excelfile),
            'meta': os.path.join(raw_folder, name_excelfile),
            'spreads': os.path.join(raw_folder, name_excelfile_spreads),
            'govies': os.path.join(raw_folder, name_excelfile_spreads),
            }


def extract_spot_rates(rfr_filepath):
    print('Extracting spots: ' + rfr_filepath)
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


def extract_meta(rfr_filepath):
    print('Extracting meta data :' + rfr_filepath)
    meta = read_meta(rfr_filepath)
    meta = pd.concat(meta).T
    meta.columns = meta.columns.droplevel()
    meta.index.name = 'Country'
    meta = meta.sort_index()
    return meta

def extract_spreads(spread_filepath):
    print('Extracting spreads: ' + spread_filepath)
    spreads = read_spreads(spread_filepath)
    spreads_non_gov = pd.concat({i: pd.concat(spreads[i]) for i in
                                 ["financial fundamental spreads", "non-financial fundamental spreads"]})
    spreads_non_gov = spreads_non_gov.stack().rename('spread')
    spreads_non_gov.index.names = ['type', 'currency_code', 'duration', 'cc_step']
    spreads_non_gov.index = spreads_non_gov.index.reorder_levels([0, 1, 3, 2])
    spreads_non_gov = spreads_non_gov.rename(
        {"financial fundamental spreads": 'fin', "non-financial fundamental spreads": 'non_fin'})
    return spreads_non_gov


def extract_govies(govies_filepath):
    print('Extracting govies: ' + govies_filepath)
    try:
        spreads = read_govies(govies_filepath)
        spreads_gov = spreads["central government fundamental spreads"].stack().rename('spread').to_frame()
        spreads_gov.index.names = ['duration', 'country_code']
        spreads_gov.index = spreads_gov.index.reorder_levels([1, 0])
    except ValueError:
        print('No govies found: ' + govies_filepath)
        spreads_gov = None
        pass
    return spreads_gov


def add_to_db(ref_date, db, data_type='rfr'):
    """ Call this if a set is missing """
    url = eiopa_link(ref_date, data_type=data_type)
    set_id = db.get_set_id(url)

    files = download_EIOPA_rates(url, ref_date)
    if data_type == 'rfr':
        df = extract_spot_rates(files[data_type])
    elif data_type == 'meta':
        df = extract_meta(files[data_type])
    elif data_type == 'spreads':
        df = extract_spreads(files[data_type])
    elif data_type == 'govies':
        df = extract_govies(files[data_type])
    else:
        raise KeyError

    if df is not None:
        df = df.reset_index()
        df['url_id'] = set_id
        df['ref_date'] = ref_date.strftime('%Y-%m-%d')
        df.to_sql(data_type, con=db.conn, if_exists='append', index=False)
        set_types = {'govies': 'rfr', 'spreads': 'rfr', 'meta':'rfr'}
        db.update_catalog(
            url_id=set_id,
            dict_vals={
                'set_type': set_types.get(data_type, data_type),
                'primary_set': True,
                'ref_date': ref_date.strftime('%Y-%m-%d')}
        )
    return None


def get_rfr(ref_date, db):
    # Try to SELECT the rates from DB:
    rates_sql = "SELECT * FROM rfr WHERE ref_date = '" + ref_date.strftime('%Y-%m-%d') + "'"
    df = pd.read_sql(rates_sql, con=db.conn)

    if df.empty:
        add_to_db(ref_date, db, 'rfr')
        df = pd.read_sql(rates_sql, con=db.conn)
    df = df.drop(columns=['url_id', 'ref_date'])
    return df


def get_meta(ref_date, db):
    # Try to SELECT the rates from DB:
    sql = "SELECT * FROM meta WHERE ref_date = '" + ref_date.strftime('%Y-%m-%d') + "'"
    df = pd.read_sql(sql, con=db.conn)

    if df.empty:
        add_to_db(ref_date, db, 'meta')
        df = pd.read_sql(sql, con=db.conn)
    df = df.drop(columns=['url_id', 'ref_date'])
    return df



def get_spreads(ref_date, db):
    # Try to SELECT the rates from DB:
    spreads_sql = "SELECT * FROM spreads WHERE ref_date = '" + ref_date.strftime('%Y-%m-%d') + "'"
    df = pd.read_sql(spreads_sql, con=db.conn)

    if df.empty:
        add_to_db(ref_date, db, data_type='spreads')
        df = pd.read_sql(spreads_sql, con=db.conn)

    df = df.drop(columns=['url_id', 'ref_date'])
    return df


def get_govies(ref_date, db):
    # Try to SELECT the rates from DB:
    govies_sql = "SELECT * FROM govies WHERE ref_date = '" + ref_date.strftime('%Y-%m-%d') + "'"
    df = pd.read_sql(govies_sql, con=db.conn)
    if df.empty:
        add_to_db(ref_date, db, data_type='govies')
        df = pd.read_sql(govies_sql, con=db.conn)
    df = df.drop(columns=['url_id', 'ref_date'])
    return df


def get(ref_date, data_type='rfr'):
    # TODO: expand this to include other types:
    # Check if DB exists, if not, create it:
    workspace = get_workspace()
    database = workspace['database']
    db = EiopaDB(database)

    if data_type == 'rfr':
        return get_rfr(ref_date, db)
    elif data_type == 'meta':
        return get_meta(ref_date, db)
    elif data_type == 'spreads':
        return get_spreads(ref_date, db)
    elif data_type == 'govies':
        return get_govies(ref_date, db)
    else:
        return None


def full_rebuild():
    dr = pd.date_range(date(2016, 1, 31), date(2021, 7, 31), freq='M')
    workspace = get_workspace()
    database = workspace['database']
    db = EiopaDB(database)
    for ref_date in dr:
        rfr = get_rfr(ref_date, db)
        meta = get_rfr(ref_date, db)
        spr = get_spreads(ref_date, db)
        gov = get_govies(ref_date, db)
    return "Database successfully rebuilt"


def refresh():
    """ Update the local DB with any new dates not already included """
    return "Still #TODO"
