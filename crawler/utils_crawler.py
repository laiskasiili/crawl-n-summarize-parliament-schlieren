import json
import os
import re
import time
from functools import wraps

import requests
from constants import CategoryContainer as CC
from selenium.webdriver import FirefoxOptions
from bs4 import BeautifulSoup
from utils import read_json, write_json
from constants import ITEM_DOWNLOAD_FOLDER, PDF_DOWNLOAD_FOLDER, ROOT_URL
from selenium import webdriver


def with_retry(max_retries=5, retry_wait=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            n_retries = 0
            while True:
                try:
                    html = func(*args, **kwargs)
                    break
                except Exception as e:
                    if n_retries < max_retries:
                        time.sleep(retry_wait)
                        n_retries += 1
                    else:
                        raise Exception(
                            f"Fetching failed after {max_retries} retries for {func.__name__} with args {args} and kwargs {kwargs}! Original exception: {e}"
                        )
            return html

        return wrapper

    return decorator


@with_retry(max_retries=5, retry_wait=3)
def instant_fetch(url):
    r = requests.get(url)
    if not r.ok:
        raise Exception(f"Fetching {url} failed: ({r.status_code}) {r.text}")
    return r.content


@with_retry(max_retries=5, retry_wait=3)
def delayed_fetch(url, implicit_wait_time_s=3):
    # Although selenium is a total overkill for this kind of scraping, we use it
    # here instead of standard requests because the table on the website
    # is initiated by javascript after page load which requests cannot handle.
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    with webdriver.Firefox(options=opts) as driver:
        driver.implicitly_wait(implicit_wait_time_s)
        driver.get(url)
        content = driver.page_source
    return content


def get_author(soup, category):
    # category Vorlage has no author field on website and is always from author Stadtrat.
    if category in [CC.VORLAGE]:
        return "Stadtrat"
    if category in [CC.BESCHLUSS, CC.PROTOKOLL]:
        return "Parlament"
    if category in [CC.ANTRAG]:
        return "Büro Parlament"
    return soup.find("dt", string=re.compile("Verfasser")).next_sibling.get_text().strip()


def get_url_parliament(soup, root_url):
    # Some items do have parliament url, others do not.
    parliament_url = ""
    td_tags = soup.find_all("td", class_="icms-datatable-col-name")
    if len(td_tags) > 0:
        parliament_url = root_url + td_tags[0].find("a")["href"]
    return parliament_url


def assert_integrity_of_item(item):
    """Assert that item dicts do not contain None and only the
    specified subset of categories."""
    assert None not in set(item.values())
    assert item["category"] in set(
        [
            CC.POSTULAT,
            CC.PROTOKOLL,
            CC.BESCHLUSSANTRAG,
            CC.INTERPELLATION,
            CC.VORLAGE,
            CC.ANTRAG,
            CC.BESCHLUSS,
            CC.KLEINE_ANFRAGE,
            CC.MOTION,
        ]
    )


def download_pdf(url, path):
    # Only download pdf if it does not already exists.
    if not os.path.isfile(path):
        with open(path, "wb") as f:
            f.write(instant_fetch(url))
    return path


def get_raw_items_from_main_table(table_url):
    # Obtain list of item urls from main table:
    # The website CMS adds all table data to the table's data-entities data attribute
    # in json format. This makes it very convenient to retrieve all data at once without
    # worrying about table pagination and other javascript shenanigans. Each row data object
    # contains a title which is a text describing an a tag with href to the detail page. We use
    # a simple regex expression here to obtain the links to all detail item pages
    html = delayed_fetch(table_url)
    soup = BeautifulSoup(html, features="html.parser")
    table_data = json.loads(soup.find("table").attrs["data-entities"])["data"]
    return table_data


def process_item(raw_item):
    url_item = ROOT_URL + re.search(r"href=\"(.*?)\"", raw_item["title"]).groups()[0]
    id_item = url_item.split("/")[-1]
    path_item = os.path.join(ITEM_DOWNLOAD_FOLDER, f"{id_item}.json")

    # Check if already an item file exists. If this is the case, we can skip to next entry.
    if os.path.isfile(path_item):
        return read_json(path_item)

    # Fetch soup from detail page of item:
    # We use delayed fetch here as well, because some items do
    # have links to the corresponding parliament meeting. This
    # information is again located in a table that is only
    # initialized via javascript after initial load.
    html = delayed_fetch(url_item)
    soup = BeautifulSoup(html, features="html.parser")
    # There are two a tags to download the pdf on the page, one of which is consistently labelled
    # "Download". We are interested in the other, because it might contain hints for a
    # follow-up candidate ifit contains the word "Beantwortung".
    download_tag = soup.find(lambda tag: tag.has_attr("href") and "_doc" in tag["href"] and "Download" not in tag.string)
    category = raw_item.get("_kategorieId-sort")
    title = soup.find("dt", string="Beschreibung").next_sibling.get_text().strip()
    url_pdf = ROOT_URL + download_tag["href"]
    id_pdf = url_pdf.split("/")[-1]
    path_pdf = os.path.join(PDF_DOWNLOAD_FOLDER, f"{id_pdf}.pdf")
    # Construct item dict
    item = {
        "id_item": id_item,
        "url_item": url_item,
        "path_item": path_item,
        "category": category,
        "date": raw_item.get("_geschaeftsdatum-sort"),
        "title": title,
        "author": get_author(soup, category),
        "id_pdf": id_pdf,
        "url_pdf": url_pdf,
        "path_pdf": download_pdf(url_pdf, path_pdf),
        "follow_up_candidate": "beantwort" in f"{title.lower()}{download_tag.string.lower()}",
        "url_parliament": get_url_parliament(soup, ROOT_URL),
    }
    # Be a little defensive to know what we deal with
    assert_integrity_of_item(item)

    # Persist item as json
    write_json(item, path_item)

    return item
