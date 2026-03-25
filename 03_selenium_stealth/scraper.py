from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
import time
import random

def setup_stealth_driver():
    """Configure a Selenium webdriver with stealth capabilities to avoid detection."""
    options = Options()
    options.add_argument("start-maximized")
    
    # Crucial flags to disable automation traits
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Headless mode is often detected, but `--headless=new` in newer Chrome versions is much stealthier
    options.add_argument("--headless=new")
    
    driver = webdriver.Chrome(options=options)

    # Apply stealth tactics: override webdriver properties, languages, plugins, etc.
    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )
    
    return driver

def main():
    driver = setup_stealth_driver()

    print("Navigating to target bot detection test page...")
    # This site tests browser fingerprints and bot characteristics
    driver.get("https://bot.sannysoft.com/")
    
    # Simulate human reading behavior (delays and scrolling)
    print("Simulating human interaction (scrolling)...")
    for i in range(3):
        scroll_amount = random.randint(300, 700)
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        sleep_time = random.uniform(1.0, 2.5)
        print(f"  Scrolled {scroll_amount}px, waiting {sleep_time:.2f}s...")
        time.sleep(sleep_time)
        
    # Take a screenshot to visualize what the bot test page sees
    driver.save_screenshot("stealth_result.png")
    print("Screenshot saved to stealth_result.png. Check this to see our fingerprint results!")
    
    # Extract data from the page to show it successfully loaded
    try:
        table_rows = driver.find_elements(By.CSS_SELECTOR, "table tr")
        print("\n--- Fingerprint Results (Partial) ---")
        for row in table_rows[:8]:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 2:
                print(f"{cols[0].text.ljust(25)} : {cols[1].text}")
    except Exception as e:
        print(f"Error parsing page: {e}")

    # Proper teardown
    time.sleep(2)
    driver.quit()
    print("Session closed successfully.")

if __name__ == "__main__":
    main()
