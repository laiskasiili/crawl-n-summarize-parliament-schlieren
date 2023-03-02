from multiprocessing.pool import ThreadPool
from constants import ROOT_URL, THREAD_PROCESSES, DATAJSON_FILE
from utils import get_raw_items_from_main_table, process_item, write_json

table_url = ROOT_URL + "/politbusiness"
print(f"1) REQUESTING ITEMS... ({table_url})")
raw_items = get_raw_items_from_main_table(table_url)

print("2) PROCESSING ITEMS...")
with ThreadPool(processes=THREAD_PROCESSES) as pool:
    processed_items = [item for item in pool.map(process_item, raw_items)]

print("3) GENERATE data.json...")
write_json(processed_items, DATAJSON_FILE)
