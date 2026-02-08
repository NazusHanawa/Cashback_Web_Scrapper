import requests
import difflib
import os

from playwright.sync_api import sync_playwright
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup


def get_platform_urls(platform_url, headers):
    parsed_url = urlparse(platform_url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

    response = requests.get(platform_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    html_as = soup.find_all("a")
    
    platform_urls = {}
    
    for html_a in html_as:
        url_path = html_a.get('href')

        if not url_path:
            continue
        
        slug = url_path.strip('/').split('/')[-1]
        slug = slug.replace("cupom", "").replace("desconto", "").replace("-", " ").strip()
        
        platform_urls[slug] = urljoin(base_url, url_path)
    
    return platform_urls

def get_platform_urls_with_js(platform_url, headers):
    parsed_url = urlparse(platform_url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=headers.get('User-Agent', ''))
        page = context.new_page()

        page.route("**/*.{png,jpg,jpeg,svg,gif,webp,css}", lambda route: route.abort())

        try:
            page.goto(platform_url, wait_until="networkidle", timeout=30000)

            html_content = page.content()
        except Exception as e:
            print(f"JS LOADING ERRO: {e}")
            return {}
        finally:
            browser.close()

    soup = BeautifulSoup(html_content, "html.parser")
    html_as = soup.find_all("a")
    
    platform_urls = {}
    
    for html_a in html_as:
        url_path = html_a.get('href')
        if not url_path:
            continue
        
        slug = url_path.strip('/').split('/')[-1]
        slug = slug.replace("cupom", "").replace("desconto", "").replace("-", " ").strip()
        
        platform_urls[slug] = urljoin(base_url, url_path)
    
    return platform_urls

def get_partnerships(stores, platform_urls, platform_id):
    partnerships = []
    for store in stores:
        store_id = store[0]
        store_name = store[1].lower()
        
        best_name = difflib.get_close_matches(store_name, platform_urls, n=1, cutoff=0.6)
        if not best_name:
            return False
        
        best_name = best_name[0]
        partnership_link = platform_urls[best_name]
        
        partnership = {
            "store_id": store_id,
            "platform_id": platform_id,
            "url": partnership_link
        }

        partnerships.append(partnership)
        
    return partnerships

