import asyncio 
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from parse_cleaner import ParseCleaner

async def extract(url: str):
    browser_cfg = BrowserConfig(headless=True) 
    crawler_cfg = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        word_count_threshold=20,
        target_elements=["h1","h2","h3","title","p"]
    ) 

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        #usiamo l'url passato come argomento
        result = await crawler.arun(
            url = url, 
            config = crawler_cfg
        )

        if not result.success:
            return "Errore nel recupero della pagina."
        cleaner = ParseCleaner()
        final_result = cleaner.clean_string(result.markdown)
        
        return final_result