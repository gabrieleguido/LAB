import asyncio 
from crawl4ai import AsyncWebCrawler,BrowserConfig,CrawlerRunConfig,CacheMode
from parse_cleaner import ParseCleaner

async def main():

    browser_cfg = BrowserConfig(headless=False) 

    crawler_cfg = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            word_count_threshold=20,
            target_elements=["h1","h2","h3","title","p"]
        ) 

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(
            url = "https://it.uefa.com/uefachampionsleague/news/02a4-2060af553568-cd2fcc38c28e-1000--anteprima-liverpool-paris-saint-germain-champions-league",
            config= crawler_cfg
        )

        file = open("crawler_result_uefa.txt","w", encoding='utf-8')
        file.write(result.markdown)
        file.close()
        ParseCleaner.parsed_clean("crawler_result_uefa.txt","clean_uefa.txt",'UTF-8')

asyncio.run(main())