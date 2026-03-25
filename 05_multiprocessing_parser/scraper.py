import time
import json
import random
import multiprocessing
from bs4 import BeautifulSoup
from concurrent.futures import ProcessPoolExecutor

# Mocked massive dataset of raw HTML to simulate what an async extractor would have downloaded
def generate_mock_html(doc_id):
    """Generate a large dummy HTML document."""
    elements = []
    for i in range(1000):
        elements.append(f"<div class='item'><span class='id'>{doc_id}-{i}</span><span class='value'>{random.randint(1,10000)}</span></div>")
    html = f"<html><body>{''.join(elements)}</body></html>"
    return html

# ----------------- CPU BOUND TASK ----------------- #
def parse_html_document(payload):
    """
    A purely CPU-bound function that parses HTML.
    This runs in a separate process, avoiding the Python Global Interpreter Lock (GIL).
    """
    doc_id, html_content = payload
    soup = BeautifulSoup(html_content, 'html.parser')
    
    results = []
    items = soup.find_all('div', class_='item')
    for item in items:
        # Heavy DOM traversal and text extraction
        item_id = item.find('span', class_='id').text
        value = int(item.find('span', class_='value').text)
        
        # Simulate some data cleaning/transformation
        cleaned_value = value * 2.5
        
        results.append({
            'doc_id': doc_id,
            'item_id': item_id,
            'value': cleaned_value
        })
        
    return results
# -------------------------------------------------- #

def main():
    print("Generating massive mock dataset in memory (simulating async downloads)...")
    total_docs = 100
    mocked_data = [(i, generate_mock_html(i)) for i in range(total_docs)]
    
    print(f"Generated {total_docs} documents. Total size: ~{sum(len(d[1]) for d in mocked_data) / 1024 / 1024:.2f} MB")
    
    # 1. Sequential Processing (Single Core) - For comparison
    print("\nStarting Sequential Processing (Single Core)...")
    start_time = time.time()
    sequential_results = []
    for data in mocked_data:
        res = parse_html_document(data)
        sequential_results.extend(res)
    seq_time = time.time() - start_time
    print(f"Sequential processing took: {seq_time:.2f} seconds. Parsed {len(sequential_results)} items.")
    
    
    # 2. Parallel Processing (Multi-Core) - Bypassing GIL
    # Automatically uses the number of logical cores available on the machine
    num_cores = multiprocessing.cpu_count()
    print(f"\nStarting Parallel Processing using {num_cores} cores...")
    start_time = time.time()
    
    parallel_results = []
    # ProcessPoolExecutor manages the pool of worker processes
    with ProcessPoolExecutor(max_workers=num_cores) as executor:
        # map() chunks the iterable and distributes them to the workers
        for result_batch in executor.map(parse_html_document, mocked_data):
            parallel_results.extend(result_batch)
            
    par_time = time.time() - start_time
    print(f"Parallel processing took: {par_time:.2f} seconds. Parsed {len(parallel_results)} items.")
    
    # Calculate performance gain
    speedup = seq_time / par_time
    print(f"\nOptimization Result: Multiprocessing was {speedup:.2f}x faster than sequential execution.")
    print("By separating extraction (I/O bound) from processing (CPU bound), we optimize the entire pipeline throughput.")

if __name__ == "__main__":
    main()
