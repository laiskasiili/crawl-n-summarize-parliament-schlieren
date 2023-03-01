import requests
from functools import wraps
import time
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from constants import (
    POSTULAT,
    PROTOKOLL,
    BESCHLUSSANTRAG,
    INTERPELLATION,
    VORLAGE,
    ANTRAG,
    BESCHLUSS,
    KLEINE_ANFRAGE,
    MOTION,
)
import re
import os


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
    driver = webdriver.Firefox(options=opts)
    driver.implicitly_wait(implicit_wait_time_s)
    driver.get(url)
    return driver.page_source


def get_author(soup, category):
    # category Vorlage has no author field on website and is always from author Stadtrat.
    if category in [VORLAGE]:
        return "Stadtrat"
    if category in [BESCHLUSS, PROTOKOLL]:
        return "Parlament"
    if category in [ANTRAG]:
        return "Büro Parlament"
    return (
        soup.find("dt", string=re.compile("Verfasser")).next_sibling.get_text().strip()
    )


def get_url_parliament(soup):
    # Some items do have parliament url, others do not.
    parliament_url = ""
    td_tags = soup.find_all("td", class_="icms-datatable-col-name")
    if len(td_tags) > 0:
        parliament_url = td_tags[0].find("a")["href"]
    return parliament_url


def assert_integrity_of_item(item):
    """Assert that item dicts do not contain None and only the
    specified subset of categories."""
    assert None not in set(item.values())
    assert item["category"] in set(
        [
            POSTULAT,
            PROTOKOLL,
            BESCHLUSSANTRAG,
            INTERPELLATION,
            VORLAGE,
            ANTRAG,
            BESCHLUSS,
            KLEINE_ANFRAGE,
            MOTION,
        ]
    )


def download_pdf(url, path):
    # Only download pdf if it does not already exists.
    if not os.path.isfile(path):
        print(f"    Downloading pdf to {path}")
        with open(path, "wb") as f:
            f.write(instant_fetch(url))
    else:
        print(f"    Already exists - skipping download for {path}")
    return path
