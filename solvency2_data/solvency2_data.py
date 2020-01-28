# -*- coding: utf-8 -*-

"""Main module."""

__author__ = """De Nederlandsche Bank"""
__email__ = 'ECDB_berichten@dnb.nl'
__version__ = ''0.2.0''

from datetime import datetime, timedelta
from urllib.request import urlopen
import zipfile
import os
import numpy as np
from numpy.linalg import inv

class RiskFreeRate(dict):
    def __init__(self, input_date):
        self.update(read(input_date))

def RFR_reference_date(input_date = None, cache = {}):
    """Returns the closest reference date prior to an input_date
    The reference_date is put in a dict with the original input_date
    If no input_date is given then today() is used
    >>> RFR_reference_date(datetime(2018, 1, 1))
    {'input_date': datetime.datetime(2018, 1, 1, 0, 0), 'reference_date': '20171231'}
    >>> RFR_reference_date(datetime(2018, 8, 15))
    {'input_date': datetime.datetime(2018, 8, 15, 0, 0), 'reference_date': '20180731'}
    """
    
    reference_date = input_date
    
    if (reference_date is None) or (reference_date > datetime.today()):
        reference_date = datetime.today()
    
        if (reference_date.day < 5):
            reference_date = reference_date.replace(day = 1) - timedelta(days = 1)
    else:
        reference_date = reference_date + timedelta(days = 1)
    
    # to do : check if end of month
    reference_date = reference_date.replace(day = 1) - timedelta(days = 1)

    cache["input_date"] = input_date
    cache["reference_date"] = reference_date.strftime('%Y%m%d')
    
    return cache
   
def RFR_dict(input_date = None, cache = {}):
    """Returns a dict with url and filenames from the EIOPA website based on the input_date
    >>> RFR_dict(datetime(2018,1,1))
    {'input_date': datetime.datetime(2018, 1, 1, 0, 0), 
     'reference_date': '20171231', 
     'url': 'https://eiopa.europa.eu/Publications/Standards/', 
     'path_zipfile': '',
     'name_zipfile': 'EIOPA_RFR_20171231.zip', 
     'path_excelfile': '',
     'name_excelfile': 'EIOPA_RFR_20171231_Term_Structures.xlsx'}
    """
    
    cache = RFR_reference_date(input_date, cache)

    reference_date = cache['reference_date']
    cache['url'] = "https://eiopa.europa.eu/Publications/Standards/"
    cache['name_zipfile'] = "EIOPA_RFR_" + reference_date + ".zip"
    cache['name_excelfile'] = "EIOPA_RFR_" + reference_date + "_Term_Structures" + ".xlsx"
    cache['name_excelfile_spreads'] = "EIOPA_RFR_" + reference_date + "_PD_Cod" + ".xlsx"
    
    return cache
    
def download_RFR(input_date = None, cache = {}):
    """Downloads the zipfile from the EIOPA website and extracts the Excel file
    Returns the cache with info
    >>> download_RFR(datetime(2018,1,1))
    {'name_excelfile': 'EIOPA_RFR_20171231_Term_Structures.xlsx',
     'input_date': datetime.datetime(2018, 1, 1, 0, 0),
     'url': 'https://eiopa.europa.eu/Publications/Standards/', 
     'path_zipfile': '',
     'name_zipfile': 'EIOPA_RFR_20171231.zip', 
     'path_excelfile': '',
     'reference_date': '20171231',
     """
    cache = RFR_dict(input_date, cache)
    
    if not(os.path.isfile(cache["path_excelfile"] + cache["name_excelfile"])) or not(os.path.isfile(cache["path_excelfile"] + cache["name_excelfile_spreads"])):

        # download file
        request = urlopen(cache["url"] + cache["name_zipfile"])

        # save zip-file
        output = open(cache['path_zipfile'] + cache["name_zipfile"], "wb")
        output.write(request.read())
        output.close()

        # extract file from zip-file
        zip_ref = zipfile.ZipFile(cache['path_zipfile'] + cache["name_zipfile"])
        zip_ref.extract(cache["name_excelfile"], cache['path_excelfile'])
        zip_ref.extract(cache["name_excelfile_spreads"], cache['path_excelfile'])
        zip_ref.close()

        # remove zip file
        # os.remove(cache['path_zipfile'] + cache["name_zipfile"])
        
    return cache
    
import pandas as pd

countries_list = ['Euro', 'Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Cyprus',
       'Czech Republic', 'Denmark', 'Estonia', 'Finland', 'France', 'Germany',
       'Greece', 'Hungary', 'Iceland', 'Ireland', 'Italy', 'Latvia',
       'Liechtenstein', 'Lithuania', 'Luxembourg', 'Malta', 'Netherlands',
       'Norway', 'Poland', 'Portugal', 'Romania', 'Russia', 'Slovakia',
       'Slovenia', 'Spain', 'Sweden', 'Switzerland', 'United Kingdom',
       'Australia', 'Brazil', 'Canada', 'Chile', 'China', 'Colombia',
       'Hong Kong', 'India', 'Japan', 'Malaysia', 'Mexico', 'New Zealand',
       'Singapore', 'South Africa', 'South Korea', 'Taiwan', 'Thailand',
       'Turkey', 'United States']

currencies = ["EUR", "BGN", "HRK", "CZK", "DKK", "HUF", "LIC", "PLN", "NOK", "RON", "RUB", "SEK", "CHF", 
                 "GBP", "AUD", "BRL", "CAD", "CLP", "CNY", "COP", "HKD", "INR", "JPY", "MYR", "MXN", "NZD",
                 "SGD", "ZAR", "KRW", "TWD", "THB", "TRY", "USD"]

def read_spreads(xls, cache = {}):

    cache["financial fundamental spreads"] = {}
    for name in currencies:
        df = pd.read_excel(io = xls,
                           sheet_name = name, 
                           header = 1,
                           usecols = 'W:AC',
                           nrows = 30,
                           skiprows = 8,
                           names = [0, 1, 2, 3, 4, 5, 6])
        df.index = range(1,31)
        cache["financial fundamental spreads"][name] = df

    cache["non-financial fundamental spreads"] = {}
    for name in currencies: 
        df = pd.read_excel(io = xls,
                           sheet_name = name, 
                           header = 1,
                           usecols = 'W:AC',
                           nrows = 30,
                           skiprows = 48,
                           names = [0, 1, 2, 3, 4, 5, 6])
        df.index = range(1,31)
        cache["non-financial fundamental spreads"][name] = df

    cache["central government fundamental spreads"] = {}
    for name in ['FS_Govts']: 
        df = pd.read_excel(io = xls,
                           sheet_name = name, 
                           usecols = 'B:AF',
                           nrows = 54,
                           index_col = 0,
                           skiprows = 9)
        df.index = cache['RFR_spot_no_VA'].columns
        cache["central government fundamental spreads"] = df.T
 
    return cache


def read_spot(xls, cache = {}):
    """Reads the RFR spot from the Excel file
    Returns the cache with the dataframes
    >>> 
    """
    for name in ["RFR_spot_no_VA", "RFR_spot_with_VA", 
                 "Spot_NO_VA_shock_UP", "Spot_NO_VA_shock_DOWN", 
                 "Spot_WITH_VA_shock_UP", "Spot_WITH_VA_shock_DOWN"]:
        
        df = pd.read_excel(io = xls,
                           sheet_name = name, 
                           header = 1,
                           index_col = 1)
        df = df.drop('Unnamed: 0', axis = 1)
        df.loc["VA"].fillna(0, inplace = True)
        df = df.iloc[8:]
        df.index.names = ['Duration']
        cache[name] = df

    return cache

def read_meta(xls, cache = {}):
    """Reads the RFR metadata from the Excel file
    Returns the cache with the dataframe
    >>> 
    """

    df_meta = pd.read_excel(xls, 
                            sheet_name = "RFR_spot_with_VA",
                            header = 1,
                            index_col = 1, 
                            skipfooter = 150)
    
    df_meta = df_meta.drop('Unnamed: 0', axis = 1)
    df_meta.loc["VA"].fillna(0, inplace = True)
    df_meta = df_meta.iloc[0:8]
    df_meta.index.names = ['meta']
    df_meta.index = df_meta.index.fillna("Info")

    df_append = pd.DataFrame(index = ['reference date'], 
                             columns = df_meta.columns)
    df_append.loc['reference date'] = cache["reference_date"]
    df_meta = df_meta.append(df_append)
    
    cache['meta'] = df_meta

    return cache

def read(input_date = None, path = ""):
    cache = {'path_zipfile': path, 'path_excelfile': path}
    cache = download_RFR(input_date, cache)
    cache['path_excelfile'] = path
    xls = pd.ExcelFile(cache['path_excelfile'] + cache["name_excelfile"])
    cache = read_meta(xls, cache)
    cache = read_spot(xls, cache)
    xls_spreads = pd.ExcelFile(cache['path_excelfile'] + cache["name_excelfile_spreads"])
    cache = read_spreads(xls_spreads, cache)
    return cache

def big_h(u, v):
    """The big h-function according to 139 of the specs.
    """
    left = (u + v + np.exp(-u - v)) / 2
    diff = np.abs(u - v)
    right = (diff + np.exp(-diff)) / 2
    return left - right

def big_g(alfa, q, nrofcoup, t2, tau): 
    """This function calculates 2 outputs:
     output1: g(alfa)-tau where g(alfa) is according to 165 of the specs
     output(2): gamma = Qb according to 156 of the specs
    """
    n, m = q.shape 
    # construct m*m h-matrix
    h = np.fromfunction(lambda i, j: big_h(alfa * (i+1) / nrofcoup, alfa * (j+1) / nrofcoup), (m, m))
    # Solving b according to 156 of specs, note: p = 1 by construction
    res_1 = np.array([1 - np.sum(q[i]) for i in range(n)]).reshape((n, 1))
    # b = ((Q'HQ)^(-1))(1-Q'1) according to 156 of the specs
    b = np.matmul(inv(np.matmul(np.matmul(q, h), q.T)), res_1)
    # gamma variable is used to store Qb according to 156 of specs
    gamma = np.matmul(q.T, b)
    res_2 = sum(gamma[i, 0] * (i+1) / nrofcoup for i in range(0, m))
    res_3 = sum(gamma[i, 0] * np.sinh(alfa * (i+1) / nrofcoup) for i in range(0, m))
    kappa = (1 + alfa * res_2) / res_3
    return (alfa / np.abs(1 - kappa * np.exp(t2 * alfa)) - tau, gamma)

def optimal_alfa(alfa, q, nrofcoup, t2, tau, precision):

    new_alfa, gamma = big_g(alfa, q, nrofcoup, t2, tau)
    if new_alfa > 0: 
        # scanning for the optimal alfa is based on the scan-procedure taken from Eiopa matlab production code
        # in each for-next loop the next optimal alfa decimal is scanned for, starting with an stepsize of 0.1 (first decimal) followed
        # by the a next decimal through stepsize = stepsize/10
        stepsize = 0.1
#        for alfa in range(alfamin + stepsize, 20, stepsize):
        for i in range(0, 200):
            alfa = alfa + stepsize + i / 10
            new_alfa, gamma = big_g(alfa, q, nrofcoup, t2, tau)
            if new_alfa <= 0:
                break
        for i in range(0, precision - 1):
            alfa = alfa - stepsize
            for i in range(1, 11):
                alfa = alfa + stepsize / 10
                new_alfa, gamma = big_g(alfa, q, nrofcoup, t2, tau)
                if new_alfa <= 0:
                    break
            stepsize = stepsize / 10
    return (alfa, gamma)

def q_matrix(instrument, n, m, liquid_maturities, RatesIn, nrofcoup, cra, log_ufr):
    # Note: prices of all instruments are set to 1 by construction
    # Hence 1: if Instrument = Zero then for Zero i there is only one pay-off of (1+r(i))^u(i) at time u(i)
    # Hence 2: if Instrument = Swap or Bond then for Swap/Bond i there are pay-offs of r(i)/nrofcoup at time 1/nrofcoup, 2/nrofcoup, ...
    # u(i)-1/nrofcoup plus a final pay-off of 1+r(i)/nrofcoup at time u(i)
    q = np.zeros([n, m])
    if instrument == "Zero":
        for i, u in enumerate(liquid_maturities):
            q[i, u - 1] = np.exp(-log_ufr * u) * np.power(1 + RatesIn[u] - cra, u)
#    elif instrument == "Swap" or instrument == "Bond":
        # not yet correct
#        for i in range(0, n):
#            for j in range(1, u[i] * nrofcoup - 1):
#                q[i, j] = np.exp(-log_ufr * j / nrofcoup) * (r[i] - cra) / nrofcoup
#            q[i, j] = np.exp(-log_ufr * j / nrofcoup) * (1 + (r[i] - cra) / nrofcoup)
    return q

def smith_wilson(instrument = "Zero", 
                 liquid_maturities = [], 
                 RatesIn = {}, 
                 nrofcoup = 1, 
                 cra = 0, 
                 ufr = 0, 
                 min_alfa = 0.05, 
                 tau = 1, 
                 T2 = 60,
                 precision = 6,
                 method = "brute_force",
                 output_type = "zero rates annual compounding"):

    # Input:
    # Instrument = {"Zero", "Bond", "Swap"},
    # nrofcoup = Number of Coupon Payments per Year,
    # CRA = Credit Risk Adjustment in basispoints,
    # UFRac = Ultimate Forward Rate annual commpounded (perunage),
    # T2 = Convergence Maturity
    # DataIn = range (50 rows x 3 columns)
    # Column1: Indicator Vector indicating if corresponding maturity is DLT to qualify as credible input
    # Column2: Maturity Vector

    assert (instrument == "Zero" and nrofcoup ==1),"instrument is zero bond, but with nrofcoup unequal to 1."
    assert (method == "brute_force"), "Only brute force method is implemented."
    assert (instrument == "Zero"),"No other instruments implemented yet."

    n = len(liquid_maturities)               # the number of liquid rates
    m = nrofcoup * max(liquid_maturities)    # nrofcoup * maximum liquid maturity

    log_ufr = np.log(1 + ufr)
    tau = tau / 10000 
    cra = cra / 10000

    # Q' matrix according to 146 of specs;
    q = q_matrix(instrument, n, m, liquid_maturities, RatesIn, nrofcoup, cra, log_ufr)

    # Determine optimal alfa with corresponding gamma
    if method == "brute_force":
        alfa, gamma = optimal_alfa(min_alfa, q, nrofcoup, T2, tau, precision)
    alfa = np.round(alfa, 6)

    # Now the SW-present value function according to 154 of the specs can be calculated: p(v)=exp(-lnUFR*v)*(1+H(v,u)*Qb)
    #The G(v,u) matrix for maturities v = 1 to 121 according to 142 of the technical specs (Note: maturity 121 will not be used; see later)
    g = np.fromfunction(lambda i, j: np.where(j / nrofcoup > i, 
                                              alfa * (1 - np.exp(-alfa * j / nrofcoup) * np.cosh(alfa * i)), 
                                              alfa * np.exp(-alfa * i) * np.sinh(alfa * j / nrofcoup)), (121, m))

    # The H(v,u) matrix for maturities v = 1 to 121 according to 139 of the technical specs
    # h[i, j] = big_h(alfa * i, alfa * (j+1) / nrofcoup) -> strange, is different from earlier def
    h = np.fromfunction(lambda i, j: big_h(alfa * i / nrofcoup, alfa * (j+1) / nrofcoup), (122, m))

    # First a temporary discount-vector will be used to store the in-between result H(v,u)*Qb = #(v,u)*gamma (see 154 of the specs)
    temptempdiscount = np.matmul(h, gamma)
    # Calculating G(v,u)*Qb according to 158 of the specs
    temptempintensity = np.matmul(g, gamma)

    tempdiscount = np.zeros(121)
    tempintensity = np.zeros(121)
    for i in range(0, 121):
        tempdiscount[i] = temptempdiscount[i]
        tempintensity[i] = temptempintensity[i]

    #calculating (1'-exp(-alfa*u'))Qb as subresult for 160 of specs
    res1 = sum((1 - np.exp(-alfa * (i + 1) / nrofcoup)) * gamma[i, 0] for i in range(0, m))

    # yield intensities
    yldintensity = np.zeros(121)
    yldintensity[0] = log_ufr - alfa * res1 # calculating 160 of the specs
    yldintensity[1:] = log_ufr - np.log(1 + tempdiscount[1:]) / np.arange(1, 121) # calculating 158 of the specs for maturity 1 year

    # forward intensities # calculating 158 of the specs for higher maturities
    fwintensity = np.zeros(121)
    fwintensity[0] = log_ufr - alfa * res1 # calculating 160 of the specs
    fwintensity[1:] = log_ufr - tempintensity[1:] / (1 + tempdiscount[1:])  

    # discount rates 
    discount = np.zeros(121)
    discount[0] = 1
    discount[1:] = np.exp(-log_ufr * np.arange(1,121)) * (1 + tempdiscount[1:])

    # forward rates annual compounding
    forwardac = np.zeros(121)
    forwardac[0] = 0
    forwardac[1:] = discount[:-1] / discount[1:] - 1

    # zero rates annual compounding
    zeroac = np.zeros(121)
    zeroac[0] = 0
    zeroac[1:] = np.power(discount[1:], -1 / np.arange(1, 121)) - 1

    if output_type == "zero rates annual compounding":
        output = zeroac
    elif output_type == "forward rate annual compounding":
        output = forwardac
    elif output_type == "discount rates":
        output = fdiscount
    elif output_type == "forward intensities":
        output = fwintensity
    elif output_type == "yield intensities":
        output = yldintensity
    elif output_type == "alfa":
        output = alfa

    return output
    