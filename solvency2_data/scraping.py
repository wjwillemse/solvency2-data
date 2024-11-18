"""
Returns links for EIOPA files

"""

import re
import urllib as urllib

import bs4 as bs
import requests
import datetime
from typing import Union

urls_dict = {
    "rfr": [
        "https://www.eiopa.europa.eu/tools-and-data/risk-free-interest-rate-term-structures/risk-free-rate-previous-releases-and-preparatory-phase_en",
        "https://www.eiopa.europa.eu/tools-and-data/risk-free-interest-rate-term-structures_en",
        "https://www.eiopa.europa.eu/risk-free-rate-previous-releases-and-preparatory-phase",
    ],
    "sym_adj": [
        "https://www.eiopa.europa.eu/tools-and-data/symmetric-adjustment-equity-capital-charge_en"
    ],
}


def get_links(urls: str, r: str, proxies: Union[dict, None] = None) -> list:
    """
    Retrieves valid download links from a list of URLs.

    Args:
        urls (str): A list of URLs to search for links.
        r (str): The pattern to match for links.
        proxies: None or a dictionary of proxies to pass in requests.get

    Returns:
        list: A list of valid download links.
    """
    raw_links = []
    for page in urls:
        if len(raw_links) == 0:
            resp = requests.get(page, proxies=proxies)
            soup = bs.BeautifulSoup(resp.text, "lxml")
            for link in soup.find_all("a", {"href": r}):
                if link.get("href")[0] == "/":
                    # correct relative urls
                    link_before_redirect = "https://www.eiopa.europa.eu" + link.get(
                        "href"
                    )
                else:
                    link_before_redirect = link.get("href")
                # Check if there is a redirect:
                raw_links.append(link_before_redirect)

    valid_links = []
    for url in raw_links:
        if check_if_download(url, proxies):
            valid_links.append(url)
        else:
            redirect = lookthrough_redirect(url)
            if check_if_download(redirect, proxies):
                valid_links.append(redirect)
    if len(valid_links) > 0:
        return valid_links[0]
    else:
        return None


def check_if_download(url: str, proxies: Union[dict, None] = None) -> bool:
    """
    Checks if the URL points to a downloadable resource.

    Args:
        url (str): The URL to check.
        proxies: None or a dictionary of proxies to pass in requests.get

    Returns:
        bool: True if the resource is downloadable, False otherwise.
    """
    headers = requests.head(url, proxies, timeout=10, verify=False).headers
    # downloadable = 'attachment' in headers.get('Content-Disposition', '')
    downloadable = headers.get("Content-Type") in [
        "application/zip",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ]
    return downloadable


def lookthrough_redirect(url: str) -> str:
    """
    Looks through redirects and returns the final URL.

    Args:
        url (str): The URL to look through.

    Returns:
        str: The final URL after following redirects.
    """
    try:
        resp = urllib.request.urlopen(url)
        file_url = resp.geturl()
    except ImportError:
        file_url = url
    return file_url


def eiopa_link(
    ref_date: str, data_type: str = "rfr", proxies: Union[dict, None] = None
) -> str:
    """
    Generates the link for downloading the selected type of data for a given date.

    Args:
        ref_date (str): The reference date in the format 'YYYY-MM-DD'.
        data_type (str, optional): The type of the dataset. Defaults to 'rfr'.

    Returns:
        str: The valid link to the dataset.

    Example:
        from datetime import date
        import pandas as pd
        dr = pd.date_range(date(2016, 1, 31), date(2023, 5, 31), freq='M')
        rfr_links = {i.strftime('%Y%m%d'): eiopa_link(i.strftime('%Y-%m-%d')) for i in dr}
        sym_adj_links = {i.strftime('%Y%m%d'): eiopa_link(i.strftime('%Y-%m-%d'), 'sym_adj') for i in dr}
    """
    data_type_remap = {"spreads": "rfr", "govies": "rfr", "meta": "rfr"}
    data_type = data_type_remap.get(data_type, data_type)
    urls = urls_dict.get(data_type)
    # Change format of ref_date string for EIOPA Excel files from YYYY-mm-dd to YYYYmmdd:
    reference_date = ref_date.replace("-", "")
    ref_date_datetime = datetime.datetime.strptime(ref_date, "%Y-%m-%d")
    str_year = ref_date_datetime.strftime("%Y")
    str_month = ref_date_datetime.strftime("%B").lower()
    if data_type == "rfr":
        # eiopa uses two naming conventions for the files
        filename1 = (
            ".*(?i:filename=)(?:%E2%80%8B)?"
            + "(?i:"
            + str_month
            + ")"
            + "(?:[-, _]|%20)"
            + str_year
            + ".*"
            ".*"
        )
        filename2 = ".*EIOPA_RFR_" + reference_date + ".zip"
        r = re.compile(filename1 + "|" + filename2)

    elif data_type == "sym_adj":
        # Regex to find the file :
        # ._ required for ._march_2019
        # Only matches on first 3 letters of months since some mis-spellings
        words_in_link = ["symmetric", "adjustment", "equity", "capital", "charge"]
        r = re.compile(
            ".*(?i:eiopa)(?:[-, _]|%20)"
            + "(?:[-, _]|%20)".join(words_in_link)
            + "(?:[-, _]|%20)"
            + "(?i:"
            + str_month[:3]
            + ")"
            + "[a-z]{0,"
            + str(len(str_month) - 3)
            + "}(?:[-, _]|%20)"
            + str_year
            + "(?:_[0-9]{0,1})?(?:.xlsx|$)"
        )

    valid_link = get_links(urls, r, proxies)

    problem_dates = {"rfr": ["2021-11-30"]}
    if ref_date in problem_dates.get(data_type, []):
        valid_link = False

    if not valid_link:
        manual_links = {
            "sym_adj": {
                "2020-06-30": "https://www.eiopa.europa.eu/system/files/2020-06/eiopa_symmetric_adjustment_equity_capital_charge_16_06_2020.xlsx",
                "2020-07-31": "https://www.eiopa.europa.eu/system/files/2020-07/eiopa_symmetric_adjustment_equity_capital_charge_14_07_2020.xlsx",
            },
            "rfr": {
                "2021-11-30": "https://www.eiopa.europa.eu/system/files/2021-12/eiopa_rfr_20211130.zip"
            },
        }
        valid_link = manual_links.get(data_type).get(ref_date)

    if not valid_link:
        raise FileNotFoundError(
            "Error: no EIOPA file found for date: "
            + ref_date
            + "; Source: "
            + data_type
        )

    return valid_link
