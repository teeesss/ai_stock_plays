import asyncio
import logging
import json
import re
from pathlib import Path
from curl_cffi import requests
from datetime import datetime

# V23.95: Live Blog Scraper (JIT Narrative)
# Extracts the latest high-alpha market update paragraph from CNBC Live.

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
log = logging.getLogger(__name__)

class LiveBlogScraper:
    def __init__(self):
        self.base_url = "https://www.cnbc.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        self.sources = {
            "Edward Jones": "https://www.edwardjones.com/us-en/market-news-insights/stock-market-news/daily-market-recap",
            "Briefing": "https://www.briefing.com/stock-market-update",
            "CNBC": "https://www.cnbc.com/id/100003114/device/rss/rss.html" # RSS as fallback to find URL
        }

    def scrape_edward_jones(self):
        """Scrapes the high-quality Edward Jones daily recap."""
        url = self.sources["Edward Jones"]
        try:
            resp = requests.get(url, headers=self.headers, impersonate="chrome120")
            if resp.status_code != 200: return None
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Edward Jones uses <li> tags for the dense recap points
            # We want the first one that is significant
            recap_items = soup.find_all('li')
            for item in recap_items:
                text = item.get_text().strip()
                # Look for the characteristic " - " separator
                if " - " in text or " – " in text:
                    if len(text) > 100:
                        # Clean up common encoding artifacts (non-ASCII dashes, smart quotes, etc)
                        text = re.sub(r'[^\x00-\x7F]+', ' ', text)
                        text = text.replace("  ", " ").strip()
                        return text
        except Exception as e:
            log.error(f"Edward Jones scrape failed: {e}")
        return None

    def scrape_briefing(self):
        """Scrapes Briefing.com (may require specific parsing if SPA)."""
        url = self.sources["Briefing"]
        try:
            resp = requests.get(url, headers=self.headers, impersonate="chrome120")
            # Briefing often hides content in JS, but sometimes has a meta description or lead p
            if resp.status_code != 200: return None
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Look for the primary market update text
            # Often in <p class="update-text"> or similar
            update = soup.find('p') # Fallback to first p if dense
            if update:
                text = update.get_text().strip()
                if len(text) > 100: return text
        except Exception as e:
            log.error(f"Briefing scrape failed: {e}")
        return None
    async def get_latest_live_blog_url(self):
        """Finds the URL for today's market live blog."""
        search_url = "https://search.cnbc.com/rs/search/view.html?partnerId=2000&keywords=Stock%20Market%20Today%20Live%20Updates"
        try:
            resp = requests.get(search_url, headers=self.headers, impersonate="chrome120")
            if resp.status_code != 200: return None
            
            # Find the latest link
            matches = re.findall(r'href="(https://www\.cnbc\.com/\d{4}/\d{2}/\d{2}/stock-market-today-live-updates\.html)"', resp.text)
            if matches: return matches[0]
            
            home_resp = requests.get(self.base_url, headers=self.headers, impersonate="chrome120")
            home_matches = re.findall(r'href="(/20\d{2}/\d{2}/\d{2}/stock-market-today-live-updates\.html)"', home_resp.text)
            if home_matches: return f"{self.base_url}{home_matches[0]}"
        except Exception as e:
            log.error(f"Failed to find live blog: {e}")
        return None

    def scrape_lead_paragraph(self, url):
        """Extracts the first dense paragraph from the live blog."""
        if not url: return None
        try:
            resp = requests.get(url, headers=self.headers, impersonate="chrome120")
            if resp.status_code != 200: return None
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, 'html.parser')
            lead_div = soup.find('div', class_='LiveBlog-leadParagraph')
            if lead_div: return lead_div.get_text().strip()
            payload = soup.find('div', class_='LiveBlogPayload-body')
            if payload:
                p = payload.find('p')
                if p: return p.get_text().strip()
        except Exception as e:
            log.error(f"Scrape failed: {e}")
        return None

    async def get_sovereign_narrative(self):
        """Main entry point for JIT Narrative (Multi-Source)."""
        # Priority 1: Edward Jones (Clean Recap)
        narrative = self.scrape_edward_jones()
        if narrative: 
            log.info("[MACRO] Sovereign Lead: Edward Jones Recap")
            return narrative, self.sources["Edward Jones"]
            
        # Priority 2: CNBC Live Blog (Real-time fallback)
        url = await self.get_latest_live_blog_url()
        if url:
            narrative = self.scrape_lead_paragraph(url)
            if narrative:
                log.info("[MACRO] Sovereign Lead: CNBC Live Blog")
                return narrative, url
        
        # Priority 3: Briefing (Fallback)
        narrative = self.scrape_briefing()
        if narrative:
            log.info("[MACRO] Sovereign Lead: Briefing.com")
            return narrative, self.sources["Briefing"]

        return None, None

if __name__ == "__main__":
    scraper = LiveBlogScraper()
    text, url = asyncio.run(scraper.get_sovereign_narrative())
    print("-" * 50)
    print(f"URL: {url}")
    print(f"NARRATIVE: {text}")
    print("-" * 50)
