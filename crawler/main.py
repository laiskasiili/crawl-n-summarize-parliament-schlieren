from multiprocessing.pool import ThreadPool
from constants import ROOT_URL, DATAJSON_FILE, DATAJSON_FILE_FRONTEND
from utils import get_raw_items_from_main_table, process_item, write_json
import shutil
from datetime import datetime

table_url = ROOT_URL + "/politbusiness"
print(f"1) REQUEST ITEMS... ({table_url})")
raw_items = get_raw_items_from_main_table(table_url)

print("2) PROCESS ITEMS...")
# processed_items = [process_item(item) for item in raw_items]
with ThreadPool(processes=20) as pool:
    processed_items = [item for item in pool.map(process_item, raw_items)]

print("3) GENERATE data.json...")
datajson_items = []
for item in processed_items:
    datajson_items.append(
        {
            "date": item["date"],
            "author": item["author"],
            "category": item["category"],
            "title__display": f'<a target="_blank" href="{item["url_item"]}">{item["title"]}</a>',
            "title": item["category"] + item["title"],
            "summary__display": item["summary"] + f' <a target="_blank" href="{item["url_pdf"]}">(Original PDF)</a>',
            "summary": item["summary"],
        }
    )
write_json({"asof": datetime.now().strftime("%Y-%m-%d"), "data": datajson_items}, DATAJSON_FILE)

print("4) COPY data.json...")
shutil.copyfile(DATAJSON_FILE, DATAJSON_FILE_FRONTEND)

print("ALL DONE!")
