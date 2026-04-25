import asyncio 
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from cleaner import Cleaner


async def extract(url: str):
    browser_cfg = BrowserConfig(headless=True) 
    crawler_cfg = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        word_count_threshold=20,
        target_elements=["h1","h2","h3","title","span","p"]
    ) 

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        #usiamo l'url passato come argomento
        result = await crawler.arun(
            url=url, 
            config=crawler_cfg
        )

        final_result = Cleaner.parsed_clean_to_string(result.markdown)
        
    return {"html":result.html,"parsed":final_result}