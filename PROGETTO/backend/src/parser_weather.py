<<<<<<< HEAD
import asyncio 
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from cleaner import Cleaner

=======
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from cleaner import WeatherCleaner
>>>>>>> 022602799c6b3e51b43cca3537bb15455ae15ef0

async def extract(url: str):
    browser_cfg = BrowserConfig(headless=True) 
    crawler_cfg = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
<<<<<<< HEAD
        word_count_threshold=20,
        target_elements=["h1","h2","h3","title","span","p"]
    ) 

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        #usiamo l'url passato come argomento
        result = await crawler.arun(
            url=url, 
            config=crawler_cfg
        )

        final_result = Cleaner.parsed_clean_to_string(result.markdown)
        
    return {"html":result.html,"parsed":final_result}
=======
        word_count_threshold=1,
        css_selector="main#MainContent",
        excluded_tags=["nav", "footer", "header", "script", "style", "aside", "form", "button", "iframe", "svg"],
        remove_overlay_elements=True
    ) 

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(url=url, config=crawler_cfg)

        final_result = WeatherCleaner.clean_weather_data(result.cleaned_html)

    return {"html": result.html, "parsed": final_result}
>>>>>>> 022602799c6b3e51b43cca3537bb15455ae15ef0
