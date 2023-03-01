from bs4 import BeautifulSoup
import json
import re
from utils import (
    delayed_fetch,
    get_author,
    get_url_parliament,
    assert_integrity_of_items,
)
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

# Config
ROOT_URL = "https://www.schlieren.ch"

# Obtain list of item urls from main table
table_url = ROOT_URL + "/politbusiness"
html = delayed_fetch(table_url)
soup = BeautifulSoup(html, features="html.parser")

# The website CMS adds all table data to the table's data-entities data attribute
# in json format. This makes it very convenient to retrieve all data at once without
# worrying about table pagination and other javascript shenanigans. Each row data object
# contains a title which is a text describing an a tag with href to the detail page. We use
# a simple regex expression here to obtain the links to all detail item pages.
table_data = json.loads(soup.find("table").attrs["data-entities"])["data"]
items = []
for d in table_data:
    items.append(
        {
            "category": d.get("_kategorieId-sort"),
            "date": d.get("_geschaeftsdatum-sort"),
            "url_item": ROOT_URL + re.search(r"href=\"(.*?)\"", d["title"]).groups()[0],
        }
    )


# Enrich item dictionaries with some more attributes from detail page.
# Due to mutable nature of dictionaries and lists, the items list is changed
# in place. ENrich the following:
# - author
# - title
# - url pdf download
# - flag if the item is a "follow-up" candidate ("Beantwortung")
# - url parliament

for k, item in enumerate(items):
    print(f"({k}) Processing item...")
    # We use delayed fetch here as well, because some items do
    # have links to the corresponding parliament meeting. This
    # information is again located in a table that is only
    # initialized via javascript after initial load.
    html = delayed_fetch(item["url_item"])
    soup = BeautifulSoup(html, features="html.parser")
    item["author"] = get_author(soup, item)
    item["title"] = (
        soup.find("dt", string="Beschreibung").next_sibling.get_text().strip()
    )
    # There are two a tags to download the pdf on the page, one of which is consistently labelled
    # "Download". We are interested in the other, because it might contain hints for a
    # follow-up candidate ifit contains the word "Beantwortung".
    download_tag = soup.find(
        lambda tag: tag.has_attr("href")
        and "_doc" in tag["href"]
        and "Download" not in tag.string
    )
    item["url_pdf"] = ROOT_URL + download_tag["href"]
    item["follow_up_candidate"] = (
        "beantwort" in f"{item['title'].lower()}{download_tag.string}"
    )
    item["url_parliament"] = ROOT_URL + get_url_parliament(soup)
    # Download pdf if it does not already exists and save file path


# Be a little defensive to know what we deal with
assert_integrity_of_items(items)

print("Done")
