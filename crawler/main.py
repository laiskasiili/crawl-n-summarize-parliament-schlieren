from multiprocessing.pool import ThreadPool

from constants import ROOT_URL, THREAD_PROCESSES

from crawler.utils_crawler import get_raw_items_from_main_table, process_item

# Config
table_url = ROOT_URL + "/politbusiness"
print("1) REQUESTING ITEMS... ({table_url})")
raw_items = get_raw_items_from_main_table(table_url)

print("2) DOWNLOADING ITEMS...")
with ThreadPool(processes=THREAD_PROCESSES) as pool:
    for item in pool.map(process_item, raw_items):
        print(f"Finished downloading item {item['id_item']}")

print("3) GENERATING SUMMARIES...")
