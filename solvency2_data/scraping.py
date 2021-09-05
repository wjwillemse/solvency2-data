"""
Returns links for EIOPA files

"""
import re
import bs4 as bs
import requests

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
                valid_links.append(link.get("href"))
    if len(valid_links) > 0:
        return valid_links[0]
    else:
        return None


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
    reference_date = ref_date.strftime("%Y%m%d")
    if data_type == "rfr":
        filename = "eiopa_rfr_" + reference_date
        # Allow for extra 4 characters e.g. _0_0
        r = re.compile(".*" + filename + ".{0,4}.zip")
    elif data_type == "sym_adj":
        str_year = ref_date.strftime("%Y")
        str_month = ref_date.strftime("%B").lower()
        # Regex to find the file :
        # ._ required for ._march_2019
        # Only matches on first 3 letters of months since some mis-spellings
        r = re.compile(
            ".*eiopa[-, _]symmetric[-, _]adjustment[-, _]equity[-, _]capital[-, _]charge\.?[-, _]"
            + str_month[:3]
            + "[a-z]{0,"
            + str(len(str_month) - 3)
            + "}[-, _]"
            + str_year
            + ".*.xlsx"
        )

    valid_link = get_links(urls, r)
    if not valid_link:
        raise FileNotFoundError("Error: no EIOPA file found for: " + reference_date)

    return valid_link
