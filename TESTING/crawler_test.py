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
                "https://www.nbcnews.com/science/space/artemis-ii-astronauts-return-nasa-moon-mission-rcna273651",
                "https://www.nbcnews.com/world/europe/europe-celebrates-orban-defeat-hungary-election-putin-trump-maga-rcna331478",
                "https://www.nbcnews.com/sports/golf/masters-2026-rory-mcilroy-holds-win-second-straight-masters-rcna330988",
                "https://www.nbcnews.com/pop-culture/pop-culture-news/britney-spears-voluntarily-checks-into-treatment-facility-rcna331449",
                "https://www.nbcnews.com/business/markets/oil-prices-surge-trump-says-us-will-blockade-strait-hormuz-rcna330824"
            ],

            config= wiki_crawler_cfg
        )

        file = open("crawler_result_test.md","w",encoding = 'UTF-8')
        res = ""
        for r in result:
            res = res+r.markdown
        file.write(res)
        file.close()
        ParseCleaner.parsed_clean("crawler_result_test.md","clean_test.txt",'UTF-8')
asyncio.run(main())