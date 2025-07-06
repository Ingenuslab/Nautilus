from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import os
import subprocess
import requests

app = Flask(__name__)

# API Keys from environment variables
SERPAPI_API_KEY = os.environ.get("SERPAPI_API_KEY", "8051c0c47ffb12b02ad36bfb001c30ecb1d8e8ce189db48559f978d3266fd377")
SEARCHAPI_API_KEY = os.environ.get("SEARCHAPI_API_KEY", "zx3XnaKEKkfXoPtDrpoYrfkr")

SEPER_API_KEY = os.environ.get("SEPER_API_KEY", "09cfd839f5b9d175338c2d1e42f01ad0a4dbe255")
GOOGLE_CSE_API_KEY = os.environ.get("GOOGLE_CSE_API_KEY")
GOOGLE_CSE_CX = os.environ.get("GOOGLE_CSE_CX")

app = Flask(__name__)

# Configuración para Selenium
CHROMEDRIVER_PATH = "/data/data/com.termux/files/usr/bin/chromedriver"
CHROMIUM_BINARY_PATH = "/data/data/com.termux/files/usr/lib/chromium/chrome"

# Diccionario de motores de búsqueda y sus URLs
SEARCH_ENGINES = {
    "google": "https://www.google.com/search?q=",
    "bing": "https://www.bing.com/search?q=",
    "duckduckgo": "https://duckduckgo.com/?q=",
    "yahoo": "https://search.yahoo.com/search?p="
}

def search_serpapi(query):
    if not SERPAPI_API_KEY:
        return {"error": "SERPAPI_API_KEY no configurada"}
    url = f"https://serpapi.com/search?engine=google&q={query}&api_key={SERPAPI_API_KEY}"
    response = requests.get(url)
    return response.json()

def search_searchapi(query):
    if not SEARCHAPI_API_KEY:
        return {"error": "SEARCHAPI_API_KEY no configurada"}
    url = f"https://www.searchapi.io/api/v1/search?engine=google&q={query}&api_key={SEARCHAPI_API_KEY}"
    response = requests.get(url)
    return response.json()



def search_seper(query):
    if not SEPER_API_KEY:
        return {"error": "SEPER_API_KEY no configurada"}
    url = f"https://google.serper.dev/search?q={query}&api_key={SEPER_API_KEY}"
    response = requests.get(url)
    return response.json()

def search_google_cse(query):
    if not GOOGLE_CSE_API_KEY or not GOOGLE_CSE_CX:
        return {"error": "GOOGLE_CSE_API_KEY o GOOGLE_CSE_CX no configuradas"}
    url = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_CSE_API_KEY}&cx={GOOGLE_CSE_CX}&q={query}"
    response = requests.get(url)
    return response.json()


@app.route('/scrape', methods=['GET'])
def scrape():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL parameter is required'}), 400

    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless") # Ejecutar en modo headless
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.binary_location = CHROMIUM_BINARY_PATH # Ruta al binario de Chromium

        service = Service(executable_path=CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(url)
        content = driver.page_source
        driver.quit()
        return jsonify({'method': 'Selenium', 'url': url, 'content': content})
    except Exception as e_selenium:
        return jsonify({'error': f"Selenium falló: {e_selenium}"}), 500

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    engine = request.args.get('engine', 'google').lower() # Motor de búsqueda por defecto: Google

    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400

    if engine == 'serpapi':
        result = search_serpapi(query)
    elif engine == 'searchapi':
        result = search_searchapi(query)
    elif engine == 'seper':
        result = search_seper(query)
    elif engine == 'google_cse':
        result = search_google_cse(query)
    else:
        # Fallback to Selenium-based search for traditional engines if no specific API is requested
        if engine not in SEARCH_ENGINES:
            return jsonify({'error': f"Search engine '{engine}' is not supported. Supported engines: {', '.join(SEARCH_ENGINES.keys())}, serpapi, searchapi, seper, google_cse"}), 400

        search_url = SEARCH_ENGINES[engine] + query

        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.binary_location = CHROMIUM_BINARY_PATH

            service = Service(executable_path=CHROMEDRIVER_PATH)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.get(search_url)
            page_content = driver.page_source
            driver.quit()

            soup = BeautifulSoup(page_content, 'html.parser')
            results = []

            if engine == "google":
                for g in soup.find_all('div', class_='g'):
                    anchors = g.find_all('a')
                    if anchors:
                        link = anchors[0]['href']
                        title = g.find('h3').text if g.find('h3') else 'No title'
                        snippet = g.find('span', class_='aCOpRe').text if g.find('span', class_='aCOpRe') else 'No snippet'
                        results.append({'title': title, 'link': link, 'snippet': snippet})
            elif engine == "duckduckgo":
                for result_item in soup.find_all('div', class_='web-result'):
                    title_tag = result_item.find('h2', class_='result__title')
                    link_tag = result_item.find('a', class_='result__url')
                    snippet_tag = result_item.find('a', class_='result__snippet')

                    title = title_tag.text.strip() if title_tag else 'No title'
                    link = link_tag['href'] if link_tag else 'No link'
                    snippet = snippet_tag.text.strip() if snippet_tag else 'No snippet'
                    results.append({'title': title, 'link': link, 'snippet': snippet})
            result = page_content

        except Exception as e:
            return jsonify({'error': f"Selenium search failed: {e}"}), 500

    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)