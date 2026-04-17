import asyncio 
from crawl4ai import AsyncWebCrawler,BrowserConfig,CrawlerRunConfig,CacheMode
from parse_cleaner import ParseCleaner

async def main():

    browser_cfg = BrowserConfig(headless=False) 

    crawler_cfg = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            target_elements=["h1","h2","h3","title","p","span"]
        ) 

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(
            url = "https://weather.com/it-IT/tempo/oggi/l/104b5c3a7e17868e40f84026b44fd565a02ee18193bb030a5cbd3076e58c01bc",
            config= crawler_cfg
        )

        file = open("crawler_result_weather.txt","w", encoding='utf-8')
        file.write(result.markdown)
        file.close()
        ParseCleaner.parsed_clean("crawler_result_weather.txt","clean_weather.txt",'UTF-8')

asyncio.run(main())