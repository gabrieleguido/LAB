import asyncio 
from crawl4ai import AsyncWebCrawler,BrowserConfig,CrawlerRunConfig,CacheMode

async def main():

    browser_cfg = BrowserConfig(headless=False) 

    crawler_cfg = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        word_count_threshold=20,
        
        # css_selector="#mw-content-text",
        # excluded_selector=".mw-editsection, .reflist, .navbox, .infobox," \
        # "#Notes, #See_also, #External_links, #References, #Citations" \
        # ".navbar, .stub, .plainlinks, .metadata, " \
        # ".vertical-navbox, .printfooter"
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
asyncio.run(main())