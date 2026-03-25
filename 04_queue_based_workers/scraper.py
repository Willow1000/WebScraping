import asyncio
import aiohttp
import time
import random

# Maximum number of concurrent workers scraping the queue
NUM_WORKERS = 10
# Maximum retries for a failed request
MAX_RETRIES = 3

async def worker(name, queue, session):
    """Consumer worker that pulls URLs from the queue and processes them."""
    while True:
        # Get a task from the queue
        task = await queue.get()
        url, retry_count = task
        
        try:
            print(f"[{name}] Processing {url} (Attempt {retry_count + 1})")
            
            # Simulate an async HTTP request
            # We use a mocked endpoint or public test API here
            async with session.get(url, timeout=5) as response:
                # Deliberately mock some random failures to demonstrate retries
                if random.random() < 0.2:
                    raise Exception("Random network timeout simulation")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"[{name}] Success: {url} -> Parsed {len(data)} items.")
                else:
                    raise Exception(f"HTTP Status {response.status}")
                    
        except Exception as e:
            print(f"[{name}] Error on {url}: {e}")
            if retry_count < MAX_RETRIES:
                # Exponential backoff
                backoff_time = 2 ** retry_count
                print(f"[{name}] Requeueing {url}. Backing off for {backoff_time}s...")
                await asyncio.sleep(backoff_time)
                # Put back into the queue with incremented retry count
                await queue.put((url, retry_count + 1))
            else:
                print(f"[{name}] Max retries reached for {url}. Dropping task.")
        finally:
            # Notify the queue that the task is done (crucial for queue.join())
            queue.task_done()

async def main():
    # Setup the queue
    queue = asyncio.Queue()
    
    # We will use JSONPlaceholder as a sample target API that returns quickly
    base_url = "https://jsonplaceholder.typicode.com/posts/{}/comments"
    total_urls = 50
    
    # Producer: Add tasks to the queue
    for i in range(1, total_urls + 1):
        url = base_url.format(i)
        # Each item in the queue is a tuple: (URL, retry_count)
        queue.put_nowait((url, 0))
        
    print(f"Enqueued {total_urls} URLs to scrape.")
    
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        # Create worker tasks
        workers = []
        for i in range(NUM_WORKERS):
            task = asyncio.create_task(worker(f"Worker-{i+1}", queue, session))
            workers.append(task)
            
        print(f"Started {NUM_WORKERS} consumer workers.")
        
        # Wait until the queue is fully processed (all task_done() are called)
        await queue.join()
        
        # Once queue is empty and done, cancel the infinite worker loops
        for w in workers:
            w.cancel()
        
        # Gather to suppress cancellation errors gracefully
        await asyncio.gather(*workers, return_exceptions=True)
        
    end_time = time.time()
    print(f"\nAll tasks completed in {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    # Handle the Event Loop gracefully to avoid noisy cancellation logs
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Scraping manually interrupted.")
