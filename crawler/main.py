from multiprocessing.pool import ThreadPool
from constants import ROOT_URL, DATAJSON_FILE, DATAJSON_FRONTEND_FILE
from utils import get_raw_items_from_main_table, process_item, write_json
import shutil

table_url = ROOT_URL + "/politbusiness"
print(f"1) REQUEST ITEMS... ({table_url})")
raw_items = get_raw_items_from_main_table(table_url)

print("2) PROCESS ITEMS...")
# processed_items = [process_item(item) for item in raw_items]
with ThreadPool(processes=20) as pool:
    processed_items = [item for item in pool.map(process_item, raw_items)]

print("3) GENERATE data.json...")
write_json({"data": processed_items}, DATAJSON_FILE)

print("4) COPY data.json...")
shutil.copyfile(DATAJSON_FILE, DATAJSON_FRONTEND_FILE)

print("ALL DONE!")
