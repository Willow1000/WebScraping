import asyncio
from playwright.async_api import async_playwright
import time

MAX_CONCURRENT_PAGES = 5

async def scrape_product(context, url, semaphore, index):
    """Scrape a single product page using a shared browser context and concurrency limits."""
    # The semaphore ensures only MAX_CONCURRENT_PAGES run this block at any given time
    async with semaphore:
        # Create a new page in the existing context
        page = await context.new_page()
        try:
            print(f"[{index}] Starting to scrape: {url.split('/')[-2]}")
            
            # Use appropriate wait_until conditions to speed up scraping (e.g., domcontentloaded instead of networkidle)
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            
            # Wait for specific element to be visible
            await page.wait_for_selector(".product_main h1")
            
            title = await page.locator(".product_main h1").inner_text()
            price = await page.locator("p.price_color").inner_text()
            stock = await page.locator("p.instock.availability").inner_text()
            
            print(f"[{index}] Finished: {title[:20]}... - {price}")
            return {
                "title": title,
                "price": price,
                "stock": stock.strip()
            }
        except Exception as e:
            print(f"[{index}] Failed on {url}: {e}")
            return None
        finally:
            # Always close pages to avoid memory leaks
            await page.close()

async def main():
    urls = [
        "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
        "http://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html",
        "http://books.toscrape.com/catalogue/soumission_998/index.html",
        "http://books.toscrape.com/catalogue/sharp-objects_997/index.html",
        "http://books.toscrape.com/catalogue/sapiens-a-brief-history-of-humankind_996/index.html",
        "http://books.toscrape.com/catalogue/the-requiem-red_995/index.html",
        "http://books.toscrape.com/catalogue/the-dirty-little-secrets-of-getting-your-dream-job_994/index.html",
        "http://books.toscrape.com/catalogue/the-coming-woman-a-novel-based-on-the-life-of-the-infamous-feminist-victoria-woodhull_993/index.html",
        "http://books.toscrape.com/catalogue/the-boys-in-the-boat-nine-americans-and-their-epic-quest-for-gold-at-the-1936-berlin-olympics_992/index.html",
        "http://books.toscrape.com/catalogue/the-black-maria_991/index.html",
    ]
    
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_PAGES)
    start_time = time.time()
    
    async with async_playwright() as p:
        print("Launching browser...")
        browser = await p.chromium.launch(headless=True)
        
        # Use a single context for sharing cookies/cache across pages
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        )
        
        # Block loading of images and CSS to significantly speed up scraping
        await context.route("**/*", lambda route: 
            route.abort() if route.request.resource_type in ["image", "stylesheet", "media", "font"] 
            else route.continue_()
        )
        
        tasks = []
        for i, url in enumerate(urls, 1):
            tasks.append(scrape_product(context, url, semaphore, i))
            
        print(f"Gathering {len(urls)} scraping tasks with concurrency limit {MAX_CONCURRENT_PAGES}...")
        results = await asyncio.gather(*tasks)
        
        valid_results = [r for r in results if r]
        print(f"\nSuccessfully scraped {len(valid_results)}/{len(urls)} items.")
        
        await context.close()
        await browser.close()
        
    end_time = time.time()
    print(f"Total time taken: {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    asyncio.run(main())
