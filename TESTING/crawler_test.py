import asyncio 
from crawl4ai import AsyncWebCrawler,BrowserConfig,CrawlerRunConfig,CacheMode
from cleaner import Cleaner
from token_compare import TokenCompare
import json

async def fun(url):

    browser_cfg = BrowserConfig(headless=False) 

    wiki_crawler_cfg = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        word_count_threshold=20,
        target_elements=["h1","h2","h3","title","p"],
        # excluded_selector="[href]",
        remove_forms=True
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

        final_result = Cleaner.parsed_clean_to_string(result.markdown)
        file = open("result.md","w",encoding='UTF-8')
        file.write(result.markdown)
        file.close()

        
    return {"html":result.html,"parsed":final_result}


json_file = open("./gs_data/wikipedia_gs.json","r",encoding='UTF-8')
json_list = json.load(json_file)
index = 3
url = json_list[index].get("url")
gs_text = json_list[index].get("gold_text")
res = asyncio.run(fun(url))
TokenCompare.build_eval_from_parsed_gs_string(
    res["parsed"],
    gs_text,
    tokens_file="tokens_result.txt",
    print_stats_flag=True,
    print_diff=True
)