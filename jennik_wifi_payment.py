from playwright.sync_api import sync_playwright
import random
import time
import json
import requests


def run(playwright):
    try:

        browser = playwright.chromium.launch(headless=True)  
        page=browser.new_page()
        page.goto("https://jennik.easebill.pro/hotspot-login?username=&password=&dst=&popup=true&mac=E0%3A2B%3AE9%3A15%3A79%3A3A&station=6855ef6e44d795d7420d1eab&ip=172.16.255.192&chap-id=&chap-challenge=&link-login=http%3A%2F%2Fease.bill%2Flogin&link-orig=&error=")
        time.sleep(3)
        divs = page.locator("button")
        divs.nth(1).click()
        time.sleep(.5)
        inputs = page.locator("input")
        inputfield = inputs.nth(1).fill("0715207922")
        page.click("button:has-text('Pay')")
        time.sleep(30)  # Let it render
        browser.close()
    except Exception as e:
        print(f"An error occurred: {e}")    

def main():
    try:
        res = requests.get("https://google.com")
        print("You are already connected to the internet")
    except Exception as e:
        with sync_playwright() as p:
            run(p)
 
if __name__ == "__main__":
    main()
