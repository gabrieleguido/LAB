import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from cleaner import Cleaner
import json 
from token_compare import TokenCompare

async def extract(url: str,is_mensile = False):
    """return {"html": result.html, "parsed": final_result}"""
    browser_cfg = BrowserConfig(headless=True) 

    selettore_target = "body" if is_mensile else "main#MainContent"

    md_strategy = DefaultMarkdownGenerator(
        options={
            "ignore_links": True,     # Rimuove i link (toglie gli URL tecnici e i metadati delle mappe)
            "ignore_images": True,    # Rimuove le immagini
            "body_width": 0,          # Impedisce di andare a capo spezzando i token numerici
        }
    )

    crawler_cfg = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        word_count_threshold=0,
        css_selector=selettore_target,
        excluded_tags=["nav","noscript", "footer", "script", "style", "aside", "form", "button", "iframe", "svg","map"],
        excluded_selector=(
            ".skip-link, .accessibility-link, [id*='accessibility'], [class*='Accessibility'], "
            ".advertisement, [class*='DecisionAd'], .MapCard, .styles-map-container, [class*='MapCard'], "
            ".region-sidebar, #map-card-id"
        ),        
        remove_overlay_elements=True,
        exclude_external_links=True,
        exclude_internal_links=True,
        exclude_all_images=True,
        markdown_generator=md_strategy,
        delay_before_return_html=2.0
    ) 
    

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(url=url, config=crawler_cfg)


    final_result = Cleaner.parsed_clean_to_string(result.markdown,is_weather=True)
    return {"html": result.html, "parsed": final_result}

with open("weather_gs.json","r") as gs_json:
    gs_list = json.load(gs_json)
    for elem in gs_list:
        html = elem.get("html_text")
        url = elem.get("url")
        extracted_dict = asyncio.run(extract(f"raw:{html}","/tempo/mensile" in url))
        print(f"{url}------")
        TokenCompare.build_eval_from_parsed_gs_string(extracted_dict["parsed"],
                                                        elem.get("gold_text"),
                                                        print_stats_flag=True,
                                                        print_diff=True)


