"""
Downloads rfr and stores in sqlite database for future reference

"""
import configparser
import os
import zipfile
import sqlite3
from sqlite3 import Error
import pandas as pd
import urllib
import bs4 as bs
import requests


def get_workspace():
    """ Get the workspace for saving xl and the database """
    # look in current directory for .cfg file
    # if not exists then take the .cfg file in the package directory
    config = configparser.RawConfigParser()
    fname = 'solvency2_data.cfg'
    if os.path.isfile(fname):
        config.read(fname)
    else:
        config.read(os.path.join(os.path.dirname(__file__), fname))
    path_db = config.get('Directories', 'db_folder')
    path_raw = config.get('Directories', 'raw_data')
    return {'db_folder': path_db, 'raw_data': path_raw}


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


def eiopa_rfr_link(rep_date):
    urls = ["https://www.eiopa.europa.eu/tools-and-data/risk-free-interest-rate-term-structures_en",
            "https://www.eiopa.europa.eu/risk-free-rate-previous-releases-and-preparatory-phase"]
    reference_date = rep_date.strftime('%Y%m%d')
    filename = "eiopa_rfr_" + reference_date
    zip_name = filename + ".zip"
    valid_links = []

    for page in urls:
        if len(valid_links) == 0:
            resp = requests.get(page)
            soup = bs.BeautifulSoup(resp.text, 'lxml')
            soup2 = soup.find('div', {"class": "group-related-resources"})
            links = []
            for link in soup2.findAll('a'):
                links.append(link.get("href"))
            valid_links = [link for link in links if filename in link]

    if len(valid_links) >= 1:
        valid_link = valid_links[0]
    else:
        raise FileNotFoundError("failure: data not found for this rep_date: " + reference_date)

    return valid_link


def download_EIOPA_rates(rep_date, raw_folder):
    """ Download and unzip the EIOPA files """

    url = eiopa_rfr_link(rep_date)
    zip_file = download_file(url, raw_folder)

    reference_date = rep_date.strftime('%Y%m%d')

    name_excelfile = "EIOPA_RFR_" + reference_date + "_Term_Structures" + ".xlsx"
    name_excelfile_spreads = "EIOPA_RFR_" + reference_date + "_PD_Cod" + ".xlsx"

    with zipfile.ZipFile(zip_file) as zipobj:
        zipobj.extract(name_excelfile,raw_folder)
        zipobj.extract(name_excelfile_spreads, raw_folder)
    return {'rfr': os.path.join(raw_folder, name_excelfile), 'spreads': os.path.join(raw_folder, name_excelfile_spreads)}


def extract_spot_rates(rfr_filepath):
    currency_codes_and_regions = {"EUR" : "Euro", "PLN" : "Poland", "CHF" : "Switzerland",
                                  "USD" : "United States", "GBP" : "United Kingdom", "NOK" : "Norway",
                                  "SEK" : "Sweden", "DKK" : "Denmark", "HRK" : "Croatia"}
    currency_dict = dict((v,k) for k,v in currency_codes_and_regions.items())

    rates_tables = {}
    for name, clean_name in {"RFR_spot_no_VA": 'base', "RFR_spot_with_VA": 'va',
                 "Spot_NO_VA_shock_UP": 'up', "Spot_NO_VA_shock_DOWN": 'down',
                 "Spot_WITH_VA_shock_UP": 'va_up', "Spot_WITH_VA_shock_DOWN": 'va_down'}.items():
        df = pd.read_excel(rfr_filepath,
                           sheet_name=name,
                           header=1,
                           index_col=1)
        to_drop = list(filter(lambda x: "Unnamed" in x, list(df.columns)))
        df = df.drop(to_drop, axis=1)
        df.loc["VA"].fillna(0, inplace=True)
        df = df.iloc[8:]
        df.index.names = ['Duration']
        df = df[currency_dict.keys()].rename(columns=currency_dict)
        rates_tables[clean_name] = df

    rates_tables = pd.concat(rates_tables).stack().rename('spot')
    rates_tables.index.names = ['scenario', 'duration', 'currency_code']
    rates_tables.index = rates_tables.index.reorder_levels([0,2,1])
    rates_tables = rates_tables.sort_index()
    return rates_tables


def extract_spreads(spread_filepath):
    spreads_dict = []
    # spreads_dict["financial fundamental spreads"] = {}
    currencies = ["EUR", "BGN", "HRK", "CZK", "DKK", "HUF", "LIC", "PLN", "NOK", "RON", "RUB", "SEK", "CHF",
                  "GBP", "AUD", "BRL", "CAD", "CLP", "CNY", "COP", "HKD", "INR", "JPY", "MYR", "MXN", "NZD",
                  "SGD", "ZAR", "KRW", "TWD", "THB", "TRY", "USD"]
    for name in currencies:
        df = pd.read_excel(spread_filepath,
                           sheet_name=name,
                           header=1,
                           usecols='W:AC',
                           nrows=30,
                           skiprows=8,
                           names=[0, 1, 2, 3, 4, 5, 6])
        df.index = range(1, 31)
        df['type'] = 'financial'
        df['currency_code'] = name
        spreads_dict.append(df)

    spreads = pd.concat(spreads_dict)
    spreads.index.rename('Duration', inplace=True)
    spreads = spreads.reset_index().set_index(['currency_code', 'Duration']).drop(columns='type')
    spreads = spreads.stack().rename('spread')
    spreads.index.names = ['currency_code', 'duration', 'cc_step']
    # Incrementing cc_step by 1 so can use 0 for risk free rate:
    spreads = spreads.reset_index('cc_step')
    spreads.cc_step = spreads.cc_step + 1
    spreads = spreads.set_index('cc_step', append=True)
    return spreads


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


def exec_sql(conn, sql):
    """ Execute sql in connection """
    try:
        c = conn.cursor()
        c.execute(sql)
    except Error as e:
        print(e)


def create_eiopa_db(database=r"eiopa.db"):
    annual_rfr = """ CREATE TABLE IF NOT EXISTS rfr_raw (
                                        ref_date TEXT,
                                        scenario TEXT,
                                        currency_code TEXT,
                                        duration INTEGER,
                                        spot REAL
                                    ); """

    annual_spreads = """CREATE TABLE IF NOT EXISTS spreads_raw (
                                    ref_date TEXT,
                                    currency_code TEXT,
                                    duration INTEGER,
                                    cc_step INTEGER,
                                    spread REAL
                                );"""

    # create a database connection
    conn = create_connection(database)

    # create tables
    if conn is not None:
        # create projects table
        exec_sql(conn, annual_rfr)

        # create tasks table
        exec_sql(conn, annual_spreads)
    else:
        print("Error! cannot create the database connection.")


def get_rfr(ref_date, path=None):
    # Check if DB exists, if not, create it:
    workspace = get_workspace()
    database = os.path.join(workspace['db_folder'], "eiopa.db")
    if not os.path.isfile(database):
        if not os.path.exists(workspace['db_folder']):
            os.makedirs(workspace['db_folder'])
        create_eiopa_db(database)

    # Try to SELECT the rates from DB:
    rates_sql = "SELECT * FROM rfr_raw WHERE ref_date = '" + ref_date.strftime('%Y-%m-%d') + "'"
    df = pd.read_sql(rates_sql, con=create_connection(database))

    if df.empty:
        files = download_EIOPA_rates(ref_date, workspace['raw_data'])
        rfr = extract_spot_rates(files['rfr'])
        rfr = rfr.reset_index()
        rfr['ref_date'] = ref_date.strftime('%Y-%m-%d')
        rfr.to_sql('rfr_raw', con=create_connection(database), if_exists='append', index=False)
        df = pd.read_sql(rates_sql, con=create_connection(database))

        # spreads = extract_spreads(files['spreads'])
        # sx = spreads.reset_index()
        # sx['rep_date'] = rep_date.strftime('%Y-%m-%d')
        # sx.to_sql('spreads_raw', con=create_connection(database), if_exists='append', index=False)

    return df
