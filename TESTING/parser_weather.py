import asyncio
import re
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from bs4 import BeautifulSoup
from cleaner import WeatherCleaner

async def extract(url: str):
    browser_cfg = BrowserConfig(headless=True) 
    crawler_cfg = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        word_count_threshold=1,
        css_selector="main#MainContent",
        excluded_tags=["nav", "footer", "header", "script", "style", "aside", "form", "button", "iframe", "svg"],
        remove_overlay_elements=True
    ) 

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(url=url, config=crawler_cfg)

        # Chiamata alla nuova funzione modulare
        final_result = WeatherCleaner.clean_weather_data(result.cleaned_html)

    return {"html": result.html, "parsed": final_result}