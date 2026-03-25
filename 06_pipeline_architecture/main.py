import asyncio
import aiohttp
import multiprocessing
import json
import sqlite3
import time
import os
from concurrent.futures import ProcessPoolExecutor
from bs4 import BeautifulSoup

# ==============================================================================
# 06_pipeline_architecture
# This project demonstrates a production-grade decoupled architecture.
# It splits the scraping process into three distinct phases:
# 1. Extractor (Async I/O): Downloads raw HTML blazing fast.
# 2. Processor (Multiprocessing CPU): Parses HTML utilizing all CPU cores.
# 3. Loader (Synchronous I/O): Saves clean data to SQLite database.
# ==============================================================================

DB_PATH = "scraped_data.db"

# --- 1. EXTRACTOR (Async I/O Bound) ---
async def fetch_page(session, url):
    """Fetch raw HTML asynchronously."""
    try:
        async with session.get(url, timeout=10) as response:
            if response.status == 200:
                html = await response.text()
                return (url, html)
    except Exception as e:
        print(f"[Extractor] Failed fetching {url}: {e}")
    return (url, None)

async def extractor_phase(urls):
    """Downloads all URLs and returns raw HTML."""
    print(f"[Phase 1: Extractor] Starting download of {len(urls)} pages...")
    start = time.time()
    raw_data = []
    
    connector = aiohttp.TCPConnector(limit=50)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [fetch_page(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        
    raw_data = [r for r in results if r[1] is not None]
    print(f"[Phase 1: Extractor] Downloaded {len(raw_data)} pages in {time.time() - start:.2f}s")
    return raw_data


# --- 2. PROCESSOR (CPU Bound) ---
def parse_html_payload(payload):
    """Parse a single HTML document (runs in separate process)."""
    url, html = payload
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract data (e.g., from books.toscrape.com)
    items = []
    articles = soup.select('article.product_pod')
    for article in articles:
        title = article.h3.a['title']
        price = article.select_one('p.price_color').text
        items.append((url, title, price))
        
    return items

def processor_phase(raw_data):
    """Parses raw HTML using multiple CPU cores to bypass GIL."""
    print(f"[Phase 2: Processor] Parsing {len(raw_data)} documents using {multiprocessing.cpu_count()} cores...")
    start = time.time()
    
    parsed_records = []
    with ProcessPoolExecutor() as executor:
        for result_batch in executor.map(parse_html_payload, raw_data):
            parsed_records.extend(result_batch)
            
    print(f"[Phase 2: Processor] Parsed {len(parsed_records)} items in {time.time() - start:.2f}s")
    return parsed_records


# --- 3. LOADER (Synchronous/DB I/O) ---
def setup_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_url TEXT,
            title TEXT,
            price TEXT
        )
    ''')
    conn.commit()
    return conn

def loader_phase(parsed_records):
    """Inserts clean data into the database in bulk."""
    print(f"[Phase 3: Loader] Inserting {len(parsed_records)} records into SQLite...")
    start = time.time()
    
    conn = setup_database()
    cursor = conn.cursor()
    
    # Bulk insert for speed
    cursor.executemany(
        'INSERT INTO inventory (source_url, title, price) VALUES (?, ?, ?)',
        parsed_records
    )
    
    conn.commit()
    conn.close()
    
    print(f"[Phase 3: Loader] Insert completed in {time.time() - start:.2f}s")


# --- MAIN ORCHESTRATOR ---
def main():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        
    print("=== STARTING DATA PIPELINE ===")
    overall_start = time.time()
    
    # Generate 50 pages of books.toscrape.com
    target_urls = [f"http://books.toscrape.com/catalogue/page-{i}.html" for i in range(1, 51)]
    
    # Run Phase 1
    raw_html_data = asyncio.run(extractor_phase(target_urls))
    
    if not raw_html_data:
        print("Extraction failed. Exiting.")
        return
        
    # Run Phase 2
    parsed_data = processor_phase(raw_html_data)
    
    # Run Phase 3
    loader_phase(parsed_data)
    
    print(f"=== PIPELINE COMPLETED in {time.time() - overall_start:.2f}s ===")

if __name__ == "__main__":
    main()
