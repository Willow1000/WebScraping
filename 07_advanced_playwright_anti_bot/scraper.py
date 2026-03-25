import asyncio
import random
from playwright.async_api import async_playwright

# A list of realistic User-Agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.15",
]

# Simulated Proxy list (In a real scenario, these would be valid proxy URLs)
PROXIES = [
    # {"server": "http://proxy1.example.com:8080"},
    # {"server": "http://proxy2.example.com:8080"}
]

async def intercept_request(route, request):
    """
    Blocks unnecessary resources like images, media, and fonts to speed up page load.
    Also removes common bot-specific headers.
    """
    # Block analytics and media
    if request.resource_type in ["image", "media", "font", "stylesheet"]:
        await route.abort()
        return
        
    # Example: Block common tracking domains
    if "google-analytics.com" in request.url or "doubleclick.net" in request.url:
        await route.abort()
        return
        
    # Strip or modify headers to bypass basic WAFs
    headers = request.headers
    if "webdriver" in headers:
        del headers["webdriver"]
        
    await route.continue_(headers=headers)

async def scrape_target(p, url, proxy=None):
    """Scrape a page using advanced Playwright configurations."""
    user_agent = random.choice(USER_AGENTS)
    
    # Launch browser args tailored for stealth
    browser = await p.chromium.launch(
        headless=True,
        args=[
            "--disable-blink-features=AutomationControlled", # Hides webdriver flag
            "--disable-web-security",
            "--disable-features=IsolateOrigins,site-per-process",
        ],
        proxy=proxy
    )
    
    context = await browser.new_context(
        user_agent=user_agent,
        viewport={"width": 1920, "height": 1080},
        locale="en-US",
        timezone_id="America/New_York"
    )
    
    # Override standard automation properties via CDP
    await context.add_init_script("""
        // Pass the webdriver flage
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        // Spoof languages
        Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
        // Spoof plugins
        Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
    """)

    page = await context.new_page()
    
    # Enable request interception
    await page.route("**/*", intercept_request)

    print(f"Scraping {url} as {user_agent[:40]}...")
    try:
        # We use a known bot-test page
        response = await page.goto(url, wait_until="networkidle", timeout=20000)
        
        # Human-like mouse movement and scrolling
        await page.mouse.move(100, 100)
        await asyncio.sleep(0.5)
        await page.mouse.move(500, 500)
        await page.evaluate("window.scrollBy(0, document.body.scrollHeight/2)")
        
        title = await page.title()
        status = response.status if response else "Unknown"
        print(f"Success! Status: {status} | Title: {title}")
        
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
    finally:
        await context.close()
        await browser.close()


async def main():
    print("=== Advanced Playwright Execution ===")
    
    urls = [
        "https://bot.sannysoft.com/",
        "https://antoinevastel.com/bots/",
    ]
    
    async with async_playwright() as p:
        # Run sequentially or concurrently based on use case.
        # Running sequentially here to demonstrate distinct configurations.
        for url in urls:
            # Randomly select a proxy if we had real ones
            # proxy = random.choice(PROXIES) if PROXIES else None
            proxy = None
            await scrape_target(p, url, proxy)
            # Random backoff between requests to same domain
            delay = random.uniform(1.5, 3.5)
            print(f"Waiting {delay:.2f}s before next request...\n")
            await asyncio.sleep(delay)

if __name__ == "__main__":
    asyncio.run(main())
