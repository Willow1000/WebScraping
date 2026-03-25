import asyncio
import aiohttp
from bs4 import BeautifulSoup
import time

# Target: http://books.toscrape.com/catalogue/page-{i}.html

async def fetch_page(session, url, page_num, retries=3):
    """Fetch HTML content asynchronously with retry logic."""
    for attempt in range(retries):
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    return html, page_num
                else:
                    print(f"Failed to fetch {url}: Status {response.status} (Attempt {attempt+1}/{retries})")
        except Exception as e:
            print(f"Error fetching {url}: {e} (Attempt {attempt+1}/{retries})")
        
        # Exponential backoff
        await asyncio.sleep(1 * (2 ** attempt))
        
    return None, page_num

def parse_html(html, page_num):
    """CPU-bound task to parse HTML and extract data using BeautifulSoup."""
    soup = BeautifulSoup(html, 'html.parser')
    books = soup.select('article.product_pod')
    results = []
    for book in books:
        title = book.h3.a['title']
        price = book.select_one('p.price_color').text
        results.append({'title': title, 'price': price, 'page': page_num})
    return results

async def main():
    base_url = "http://books.toscrape.com/catalogue/page-{}.html"
    total_pages = 50 
    
    # Manage TCP connection limits to avoid overloading the server or hitting OS socket limits
    connector = aiohttp.TCPConnector(limit=50)
    
    start_time = time.time()
    
    all_books = []
    
    print(f"Starting async scraper for {total_pages} pages...")
    
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for i in range(1, total_pages + 1):
            url = base_url.format(i)
            tasks.append(fetch_page(session, url, i))
            
        # Execute all HTTP requests concurrently
        responses = await asyncio.gather(*tasks)
        
        print("HTTP requests completed. Parsing HTML...")
        for html, page_num in responses:
            if html:
                # For highly CPU-bound workloads, consider asyncio.to_thread or ProcessPoolExecutor.
                # BeautifulSoup parsing is relatively lightweight here.
                books = parse_html(html, page_num)
                all_books.extend(books)
                
    end_time = time.time()
    print(f"Successfully scraped {len(all_books)} books from {total_pages} pages.")
    print(f"Total execution time: {end_time - start_time:.2f} seconds.")
    print(f"Average speed: {total_pages / (end_time - start_time):.2f} pages/second.")

if __name__ == "__main__":
    asyncio.run(main())
