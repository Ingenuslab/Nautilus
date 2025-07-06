from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import os
import subprocess

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

    if engine not in SEARCH_ENGINES:
        return jsonify({'error': f"Search engine '{engine}' is not supported. Supported engines: {', '.join(SEARCH_ENGINES.keys())}"}), 400

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
            for result in soup.find_all('div', class_='web-result'):
                title_tag = result.find('h2', class_='result__title')
                link_tag = result.find('a', class_='result__url')
                snippet_tag = result.find('a', class_='result__snippet')

                title = title_tag.text.strip() if title_tag else 'No title'
                link = link_tag['href'] if link_tag else 'No link'
                snippet = snippet_tag.text.strip() if snippet_tag else 'No snippet'
                results.append({'title': title, 'link': link, 'snippet': snippet})

        return page_content

    except Exception as e:
        return jsonify({'error': f"Search failed: {e}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)