import asyncio 
from crawl4ai import AsyncWebCrawler,BrowserConfig,CrawlerRunConfig,CacheMode
from parse_cleaner import ParseCleaner

async def main():

    browser_cfg = BrowserConfig(headless=False) 

    wiki_crawler_cfg = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        word_count_threshold=20,
        target_elements=["h1","h2","h3","title","p"]
        ) 
    weather_crawler_cfg = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        target_elements=["h1","h2","h3","title","p","span"]
        ) 

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(
            url = "https://weather.com/it-IT/tempo/oggi/l/104b5c3a7e17868e40f84026b44fd565a02ee18193bb030a5cbd3076e58c01bc",
            config= weather_crawler_cfg
        )

        file = open("crawler_result_test.md","w",encoding = 'UTF-8')
        file.write(result.markdown)
        file.close()
        ParseCleaner.parsed_clean("crawler_result_test.md","clean_test.txt",'UTF-8')
asyncio.run(main())