import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode,DefaultMarkdownGenerator


from cleaner import Cleaner
import json 
from token_compare import TokenCompare

async def extract(url: str):
    """return {"html": result.html, "parsed": final_result}"""
    browser_cfg = BrowserConfig(headless=True) 
    

    md_strategy = DefaultMarkdownGenerator(
        options={
            "ignore_links": True,     
            "ignore_images": True,    
            "body_width": 0,          
            "escape_html":False,
        },
    )

    crawler_cfg = CrawlerRunConfig(
        js_code="document.querySelectorAll('span').forEach(el => el.innerHTML += ' ');",
        cache_mode=CacheMode.BYPASS,
        word_count_threshold=0,
       
        target_elements=["div.Card--content--IOayG",
                         "div.DaybreakLargeScreen--gridWrapper--ZHESz"],
        excluded_tags=["div.adLabel","img","script","div.adLabel.BaseAd--adLabel--JGSp6","style",
        "span.video-label",
        "h2.adLabel", "span.DetailsTable--value--pWEVz","h2","head","legend"],
        exclude_external_links=True,
        exclude_internal_links=True,
        exclude_all_images=True,
        markdown_generator=md_strategy,
        delay_before_return_html=2.0
    ) 
    

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(url=url, config=crawler_cfg)


    final_result = Cleaner.parsed_clean_to_string(result.markdown)
    return {"html": result.html, "parsed": final_result}





