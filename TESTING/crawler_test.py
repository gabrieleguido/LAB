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
        result = await crawler.arun_many(
            urls = [
                "https://it.uefa.com/uefachampionsleague/news/02a4-2060af553568-cd2fcc38c28e-1000--anteprima-liverpool-paris-saint-germain-champions-league"
            ],

            config= wiki_crawler_cfg
        )

        file = open("crawler_result_test.md","w",encoding = 'UTF-8')
        res = ""
        for r in result:
            res = res+r.markdown
        file.write(res)
        file.close()
        ParseCleaner.parsed_clean("crawler_result_test.md","clean_test.md",'UTF-8')
asyncio.run(main())