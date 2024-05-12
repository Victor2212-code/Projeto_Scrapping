import re
import time
import logging
from collections import defaultdict
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException

# Configuração básica do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuração do WebDriver
def setup_driver(headless=False):
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    if headless:
        chrome_options.add_argument("--headless")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Função para rolar a página até o fim
def scroll_to_bottom(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Ajuste conforme necessário para garantir o carregamento da página
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

# Limpeza e normalização do texto
def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

# Normalização do preço
def normalize_price(price):
    cleaned_price = re.sub(r'[^\d,]', '', price).replace(',', '.')
    try:
        return float(cleaned_price)
    except ValueError:
        logging.error(f"Erro ao converter preço: {price}")
        return None  # Use None to indicate an issue

# Extração de palavras-chave significativas
def extract_keywords(name):
    words = re.split(r'\W+', name.lower())
    keywords = [word for word in words if len(word) > 2 and word not in {'de', 'com', 'para', 'por'}]
    return set(keywords)

# Obtenção dos dados dos produtos
def get_product_data(url, search_query, config):
    driver = setup_driver()
    driver.get(url)
    try:
        if 'São Judas' in config['market_name']:
            try:
                close_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.close"))
                )
                close_button.click()
                logging.info("Pop-up closed at Supermercado São Judas.")
            except TimeoutException:
                logging.warning("No close button found at Supermercado São Judas.")

        search_input = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, config['search_input_selector']))
        )
        search_input.clear()
        search_input.send_keys(search_query + Keys.ENTER)
        
        WebDriverWait(driver, 30).until(
            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, config['product_list_selector']))
        )
        scroll_to_bottom(driver)
        
        return parse_products(driver, config, search_query)
    except Exception as e:
        logging.error(f"Error while executing the search at {config['market_name']}: {e}")
        return []
    finally:
        driver.quit()

# Parse dos produtos na página
def parse_products(driver, config, search_query):
    products = []
    search_keywords = extract_keywords(search_query)
    product_cards = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, config['product_list_selector']))
    )
    for card in product_cards:
        try:
            name = clean_text(card.find_element(By.CSS_SELECTOR, config['name_selector']).text)
            product_keywords = extract_keywords(name)
            if search_keywords & product_keywords:  # Verifica se há interseção significativa de palavras-chave
                raw_price = card.find_element(By.CSS_SELECTOR, config['price_selector']).text
                price = normalize_price(raw_price) if raw_price else None
                link = card.find_element(By.CSS_SELECTOR, config['link_selector']).get_attribute('href')
                products.append({'market': config['market_name'], 'name': name, 'price': price, 'details': link})
        except NoSuchElementException:
            logging.warning("Product details incomplete, skipped.")
    return products

# Configuração dos supermercados
configs = {
    'supermercadoA': {
        'market_name': 'Supermercado Avenida',
        'base_url': "https://loja.supermercadosavenida.com.br",
        'product_list_selector': 'ul.product-grid > li',
        'name_selector': 'div.product-card-name-container',
        'price_selector': 'span.new-price',
        'link_selector': 'a[href]',
        'search_input_selector': 'input[name="search"]',
    },
    'supermercadoB': {
        'market_name': 'Supermercado São Judas',
        'base_url': "https://compreonline.supersaojudas.com.br/loja6/",
        'product_list_selector': 'div.item',
        'name_selector': '.ellipsis-2',
        'price_selector': 'div.text-center',
        'link_selector': 'a.link-nome-produto',
        'search_input_selector': 'input[type="search"]',
    },
    'supermercadoC': {
        'market_name': 'Supermercado Lavilla',
        'base_url': "https://www.sitemercado.com.br/supermercadolavilla/ourinhos-loja-ourinhos-jardim-matilde-r-do-expedicionario/",
        'product_list_selector': 'div.list-product-item',
        'name_selector': '.txt-desc-product-itemtext-muted.txt-desc-product-item',
        'price_selector': '.area-bloco-preco.bloco-preco.pr-0.ng-star-inserted',
        'link_selector': 'a.list-product-link',
        'search_input_selector': 'input[name="search"]',
    }
}

if __name__ == "__main__":
    search_term = "Bebida Energética Monster Energy Lata 473ml"
    all_products = []
    for market_id, config in configs.items():
        products = get_product_data(config['base_url'], search_term, config)
        all_products.extend(products)

    if all_products:
        # Agrupa produtos por preço
        price_to_products = {}
        for product in all_products:
            if product['price'] is not None:
                if product['price'] in price_to_products:
                    price_to_products[product['price']].append(product)
                else:
                    price_to_products[product['price']] = [product]

        # Encontra o menor preço
        lowest_price = min(price_to_products.keys())

        # Recupera todos os produtos com o menor preço
        cheapest_products = price_to_products[lowest_price]

        # Verifica quantos mercados diferentes têm esse preço
        markets_with_lowest_price = set(p['market'] for p in cheapest_products)

        # Formata a saída baseada no número de mercados com o mesmo preço mais baixo
        if len(markets_with_lowest_price) == 1:
            print("Lowest price found at a single market:")
        elif len(markets_with_lowest_price) == len(configs):
            print("All markets have the same lowest price:")
        else:
            print("Multiple markets have the same lowest price:")

        # Exibe os produtos
        for product in cheapest_products:
            print(f"Market: {product['market']} - Price: {product['price']}")
            print(f"Name: {product['name']}")
            print(f"Details: {product['details']}\n")
            print("------")
    else:
        print("No products found.")
