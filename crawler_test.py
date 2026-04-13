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
            url = "https://en.wikipedia.org/wiki/ChatGPT",
            config= crawler_cfg
        )

        file = open("crawler_result_test.txt","w")
        file.write(result.markdown)
        file.close()
        ParseCleaner.parsed_clean("crawler_result_test.txt","clean_test.txt",'UTF-8')
asyncio.run(main())