# High-Performance Web Scraping Portfolio

This repository contains 7 specialized web scraping projects that showcase advanced Python techniques for data extraction, processing, and pipeline architecture. These projects demonstrate my ability to handle high-volume I/O bound tasks, bypass bot protections, manage CPU-bound parsing, and build resilient systems.

## 🚀 Key Technologies Used
- **Asynchronous Frameworks**: `asyncio`, `aiohttp`, `aiofiles`
- **Browser Automation**: `Playwright` (Async), `Selenium`, `selenium-stealth`
- **Parsing**: `BeautifulSoup4` (bs4)
- **Concurrency & Parallelism**: `multiprocessing.Pool`, `ProcessPoolExecutor`, `asyncio.Queue`
- **Database**: `SQLite3`

---

## 📂 Projects Overview

### 1. `01_async_beautifulsoup`
**Focus: High-Volume I/O Bound Tasks**
Utilizes `aiohttp` and `asyncio.gather` alongside `BeautifulSoup` to send concurrent HTTP requests without blocking the event loop. Ideal for rapidly scraping thousands of static HTML pages.

### 2. `02_playwright_concurrency`
**Focus: Parallel Browser Contexts**
Uses Playwright's `async_api` and `asyncio.Semaphore`. It runs multiple single-page contexts in parallel while tightly controlling the concurrency limit to avoid server detection and local resource exhaustion. It also intercepts network requests to block unnecessary assets (CSS/Images) for massive speed gains.

### 3. `03_selenium_stealth`
**Focus: Bypassing Basic Defenses**
Uses `selenium` interwoven with `selenium-stealth`. Modifies browser fingerprints (disabling `navigator.webdriver`, spoofing languages/plugins) and simulates human interactions like random waits and scrolling.

### 4. `04_queue_based_workers`
**Focus: Resilience & Retry Logic**
Implements a robust Producer/Consumer pattern using `asyncio.Queue`. Workers process items continuously and handle failed requests gracefully using exponential backoff retry mechanisms, preventing complete pipeline failure on temporary network issues.

### 5. `05_multiprocessing_parser`
**Focus: CPU-Bound Processing (Bypassing GIL)**
Scraping is I/O-heavy, but parsing large DOMs is CPU-heavy. This project demonstrates separating concerns: keeping I/O in async/threads, and farming out heavy `BeautifulSoup` parsing arrays to `concurrent.futures.ProcessPoolExecutor` to utilize all machine cores.

### 6. `06_pipeline_architecture`
**Focus: Enterprise System Design**
A fully decoupled pipeline demonstrating:
1. **Extractor Phase**: Async downloads utilizing `aiohttp`.
2. **Processor Phase**: Multicore HTML parsing utilizing `multiprocessing`.
3. **Loader Phase**: Synchronous bulk inserts to an `SQLite` database.

### 7. `07_advanced_playwright_anti_bot`
**Focus: Advanced Browser Stealth & Resource Management**
Bends Playwright to behave like a human. Injects custom JavaScript via CDP to spoof fingerprints, rotates User-Agents, dynamically overrides headers, and intercepts resources simultaneously. Highly effective for scraping heavily gated Single Page Applications (SPAs).

---

## ⚙️ How to Run

1. **Install Requirements**:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Run Individual Scrapers**:
   Navigate to the project directory and run the relevant `scraper.py` or `main.py`.
   ```bash
   python 01_async_beautifulsoup/scraper.py
   python 06_pipeline_architecture/main.py
   ```

---
*Developed to showcase expertise in Python scraping, concurrency management, and scalable data pipeline architectures.*
