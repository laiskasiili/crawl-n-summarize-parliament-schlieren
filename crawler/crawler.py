from bs4 import BeautifulSoup
import json
import re
from utils import (
    delayed_fetch,
    get_author,
    get_url_parliament,
    assert_integrity_of_item,
    download_pdf,
)
import os

# Config
ROOT_URL = "https://www.schlieren.ch"
ITEM_DOWNLOAD_FOLDER = "./data/item_download"
PDF_DOWNLOAD_FOLDER = "./data/pdf_download"

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
n = len(table_data)
for k, row in enumerate(table_data, 1):
    url_item = ROOT_URL + re.search(r"href=\"(.*?)\"", row["title"]).groups()[0]
    id_item = url_item.split("/")[-1]
    path_item = os.path.join(ITEM_DOWNLOAD_FOLDER, f"{id_item}.json")

    # Check if already an item file exists. If this is the case, we can skip to next entry.
    if os.path.isfile(path_item):
        print(f"({k}/{n}) Item {id_item} already exists - SKIP")
        continue

    print(f"({k}/{n}) Processing item {id_item}...")
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
    download_tag = soup.find(
        lambda tag: tag.has_attr("href")
        and "_doc" in tag["href"]
        and "Download" not in tag.string
    )
    category = row.get("_kategorieId-sort")
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
        "date": row.get("_geschaeftsdatum-sort"),
        "title": title,
        "author": get_author(soup, category),
        "id_pdf": id_pdf,
        "url_pdf": url_pdf,
        "path_pdf": download_pdf(url_pdf, path_pdf),
        "follow_up_candidate": "beantwort"
        in f"{title.lower()}{download_tag.string.lower()}",
        "url_parliament": get_url_parliament(soup, ROOT_URL),
    }
    # Be a little defensive to know what we deal with
    assert_integrity_of_item(item)

    # Persist item as json
    with open(path_item, "w") as outfile:
        outfile.write(json.dumps(item, indent=4))
    print(f"    Processing finished. Item saved to {path_item}")

print("ALL DONE")
