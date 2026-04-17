import asyncio 
from crawl4ai import AsyncWebCrawler,BrowserConfig,CrawlerRunConfig,CacheMode
from cleaner import Cleaner

async def fun(url):

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
            url =  url,
            config= wiki_crawler_cfg
        )

        # file = open("crawler_result_test.md","w",encoding = 'UTF-8')
        # res = ""
        # for r in result:
        #     res = res+r.markdown
        # file.write(res)
        # file.close()
        # Cleaner.parsed_clean_to_file("crawler_result_test.md","clean_test.md",'UTF-8')
        # print(Cleaner.get_title_from_html(result[0].html))
        final_result = Cleaner.parsed_clean_to_string(result.markdown)
        
    return {"html":result.html,"parsed":final_result}
#asyncio.run(main())