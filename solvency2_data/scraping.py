"""
Returns links for EIOPA files

"""
import re
import urllib as urllib

import bs4 as bs
import requests
import datetime
urls_dict = {
    "rfr": [
        "https://www.eiopa.europa.eu/tools-and-data/risk-free-interest-rate-term-structures_en",
        "https://www.eiopa.europa.eu/risk-free-rate-previous-releases-and-preparatory-phase",
    ],
    "sym_adj": [
        "https://www.eiopa.europa.eu/tools-and-data/symmetric-adjustment-equity-capital-charge_en"
    ],
}


def get_links(urls: str, r: str) -> list:
    """
    Looks for linkes where target file can be downloaded

    Args:
        urls: urls to search in
        r: href to search for

    Returns:
        list of valid links

    """
    valid_links = []
    for page in urls:
        if len(valid_links) == 0:
            resp = requests.get(page)
            soup = bs.BeautifulSoup(resp.text, "lxml")
            for link in soup.find_all("a", {"href": r}):
                if link.get("href")[0]=="/":
                    # correct relative urls
                    link_before_redirect = "https://www.eiopa.europa.eu" + link.get("href")
                else:
                    link_before_redirect = link.get("href")
                # Check if there is a redirect:
                valid_links.append(link_before_redirect)

    if len(valid_links) > 0:
        return valid_links[0]
    else:
        return None


def lookthrough_redirect(url: str) -> str:
    """ Get the file behind the redirect link """
    try:
        resp = urllib.request.urlopen(url)
        file_url = resp.geturl()
    except:
        file_url = url
    return file_url



def eiopa_link(ref_date: str, data_type: str = "rfr") -> str:
    """
    This returns the link for downloading the selected type of data for a given date
    Utilises regex to allow for variability in EIOPA publications

    Example:

    from datetime import date
    import pandas as pd
    dr = pd.date_range(date(2016,1,31), date(2021,7,31), freq='M')
    rfr_links = {i.strftime('%Y%m%d'): eiopa_link(i) for i in dr}
    sym_adj_links = {i.strftime('%Y%m%d'): eiopa_link(i, 'sym_adj') for i in dr}

    Args:
        ref_date: reference date
        data_type: type of the dataset

    Returns:
        valid link of dataset

    """
    data_type_remap = {"spreads": "rfr", "govies": "rfr", "meta": "rfr"}
    data_type = data_type_remap.get(data_type, data_type)
    urls = urls_dict.get(data_type)
    # Change format of ref_date string for EIOPA Excel files from YYYY-mm-dd to YYYYmmdd:
    print(ref_date)
    reference_date = ref_date.replace('-', '')
    ref_date_datetime = datetime.datetime.strptime(ref_date, '%Y-%m-%d')
    if data_type == "rfr":
        # eiopa uses two naming conventions for the files
        filename1 = ".*"+ref_date_datetime.strftime("%B%%20%Y")+"(%E2%80%8B)?"
        filename2 = ".*EIOPA_RFR_" + reference_date + ".zip"
        r = re.compile(filename1+"|"+filename2)
    elif data_type == "sym_adj":
        str_year = ref_date_datetime.strftime("%Y")
        str_month = ref_date_datetime.strftime("%B").lower()
        # Regex to find the file :
        # ._ required for ._march_2019
        # Only matches on first 3 letters of months since some mis-spellings
        words_in_link = ['symmetric', 'adjustment', 'equity', 'capital', 'charge']
        r = re.compile(".*(?i:eiopa)(?:[-, _]|%20)"
                       + "(?:[-, _]|%20)".join(words_in_link)
                       + "(?:[-, _]|%20)" + "(?i:" + str_month[:3]+ ")"
                       + "[a-z]{0,"
                       + str(len(str_month) - 3)
                       + "}(?:[-, _]|%20)"
                       + str_year
                       + "(?:.xlsx|$)"
        )

    valid_link = get_links(urls, r)
    valid_link = lookthrough_redirect(valid_link)

    if not valid_link:
        manual_links = {
            'sym_adj':
                {
                    '2020-06-30': 'https://www.eiopa.europa.eu/sites/default/files/symmetric_adjustment/eiopa_symmetric_adjustment_equity_capital_charge_16_06_2020.xlsx',
                    '2020-07-31': 'https://www.eiopa.europa.eu/sites/default/files/symmetric_adjustment/eiopa_symmetric_adjustment_equity_capital_charge_14_07_2020.xlsx'
                }
        }
        valid_link = manual_links.get(data_type).get(ref_date)

    if not valid_link:
        raise FileNotFoundError("Error: no EIOPA file found for date: " + ref_date + '; Source: ' + data_type)

    return valid_link
