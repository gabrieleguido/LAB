import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode,DefaultMarkdownGenerator


from cleaner import Cleaner
import json 
from token_compare import TokenCompare

async def extract(url: str,is_mensile = False):
    """return {"html": result.html, "parsed": final_result}"""
    browser_cfg = BrowserConfig(headless=True) 

    # selettore_target = "body" if is_mensile else "main#MainContent"

    

    md_strategy = DefaultMarkdownGenerator(
        options={
            "ignore_links": True,     
            "ignore_images": True,    
            "body_width": 0,          
            "escape_html":False,
        },
        # content_source="raw_html"
    )

    crawler_cfg = CrawlerRunConfig(
        js_code="document.querySelectorAll('span').forEach(el => el.innerHTML += ' ');",
        cache_mode=CacheMode.BYPASS,
        word_count_threshold=0,
       
        target_elements=["div.Card--content--IOayG","#WxuAlmanac-sidebar-55970a51-ad13-4575-958b-4b455398fdef > section",
                         "div.DaybreakLargeScreen--gridWrapper--ZHESz"],
        excluded_tags=["div.adLabel","img","script","div.adLabel.BaseAd--adLabel--JGSp6","style",
        "span.video-label",
        "h2.adLabel", "span.DetailsTable--value--pWEVz"],
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

with open("weather_gs.json","r") as gs_json:
    gs_list = json.load(gs_json)
    sums = [0.0,0.0,0.0]
    for elem in gs_list:
        html = elem.get("html_text")
        url = elem.get("url")
        extracted_dict = asyncio.run(extract(f"raw:{html}","/tempo/mensile" in url))
        print(f"{url}------")
        stats = TokenCompare.build_eval_from_parsed_gs_string(extracted_dict["parsed"],
                                                        elem.get("gold_text"),
                                                        print_stats_flag=True,
                                                        print_diff=True)
        sums[0] += stats["precision"]
        sums[1] += stats["recall"]
        sums[2] += stats["f1"]
    
    print(sums[0]/len(gs_list))
    print(sums[1]/len(gs_list))
    print(sums[2]/len(gs_list))




