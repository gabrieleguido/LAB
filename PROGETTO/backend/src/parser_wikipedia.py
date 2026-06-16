import asyncio 
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, DefaultMarkdownGenerator
from cleaner import Cleaner
import re


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
            url=url, 
            config=crawler_cfg
        )

        final_result = result.markdown
        if final_result:
            # 1. IL BOOST PER IL 0.933: Trasforma [Testo](https://...) in "Testo"
            final_result = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', final_result)
            
            # 2. Rimuove le note residue es. [1], [23]
            final_result = re.sub(r'\[\d+\]', '', final_result)
            
            # 3. Rimuove i tasti di modifica
            final_result = re.sub(r'\[edit\]|\[modifica\]', '', final_result, flags=re.IGNORECASE)
            
            # 4. Compatta gli spazi
            final_result = re.sub(r' +', ' ', final_result)
            final_result = final_result.strip()
        
    return {"html":result.html,"parsed":final_result}