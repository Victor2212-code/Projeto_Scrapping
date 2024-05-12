# import re
# import time
# import logging
# from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# # Configuração do logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# def scroll_to_bottom(driver):
#     old_position = driver.execute_script("return window.pageYOffset;")
#     logging.info("Iniciando o scroll da página para baixo.")
#     while True:
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(1)  # Pausa reduzida para evitar espera desnecessária
#         new_position = driver.execute_script("return window.pageYOffset;")
#         if new_position == old_position:
#             break
#         old_position = new_position
#     logging.info("Scroll da página concluído.")

# def select_city_by_text_and_proceed(driver, city_text, button_selector):
#     try:
#         city_element = WebDriverWait(driver, 10).until(
#             EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{city_text}')]"))
#         )
#         city_element.click()
#         logging.info(f"Cidade '{city_text}' selecionada com sucesso.")

#         go_shopping_button = WebDriverWait(driver, 10).until(
#             EC.element_to_be_clickable((By.CSS_SELECTOR, button_selector))
#         )
#         go_shopping_button.click()
#         logging.info("Botão 'Ir às Compras' clicado com sucesso.")
#     except Exception as e:
#         logging.error(f"Erro ao tentar selecionar a cidade pelo texto e prosseguir: {e}")

# def get_product_data(url, search_query, city_text, config):
#     chrome_options = Options()
#     chrome_options.add_argument("--window-size=1920,1080")
#     chrome_options.add_argument("--disable-gpu")
#     chrome_options.add_argument("--no-sandbox")
#     chrome_options.add_argument("--disable-dev-shm-usage")

#     service = Service(ChromeDriverManager().install())
#     driver = webdriver.Chrome(service=service, options=chrome_options)
#     driver.get(url)
#     logging.info(f"Acessando a URL: {url}")

#     try:
#         if city_text and 'text_city_selector' in config:
#             select_city_by_text_and_proceed(driver, city_text, '.btn-primary.btn.btn-default.btn_store_selection')

#         search_input = WebDriverWait(driver, 15).until(
#             EC.visibility_of_element_located((By.CSS_SELECTOR, config['search_input_selector']))
#         )
#         search_input.clear()

#         # Adiciona uma pausa antes de enviar a pesquisa para garantir que o campo esteja interativo
#         time.sleep(5)

#         search_input.send_keys(search_query + Keys.ENTER)
#         logging.info(f"Realizando pesquisa para: {search_query}")

#         WebDriverWait(driver, 20).until(
#             EC.visibility_of_all_elements_located((By.CSS_SELECTOR, config['results_container_selector']))
#         )

#         scroll_to_bottom(driver)

#         soup = BeautifulSoup(driver.page_source, 'lxml')
#         products = parse_products(soup, config)
#         logging.info(f"Produtos extraídos: {len(products)} itens encontrados.")
#         return products

#     except Exception as e:
#         logging.error(f"Ocorreu um erro durante a extração dos dados: {e}")
#         return []
#     finally:
#         driver.quit()
#         logging.info("Driver do navegador encerrado.")

# def parse_products(soup, config):
#     product_cards = soup.select(config['product_list_selector'])
#     products = []
#     for card in product_cards:
#         name_container = card.select_one(config['name_selector'])
#         price_container = card.select_one(config['price_selector'])
#         link_container = card.select_one(config['link_selector'])

#         name = clean_text(name_container.get_text(strip=True)) if name_container else 'No Name'
#         price = clean_text(price_container.get_text(strip=True)) if price_container else 'No Price'
#         link = link_container['href'] if link_container else '#'

#         product = {
#             'name': name,
#             'price': price,
#             'details': f"{config['base_url']}{link if link.startswith('/') else '/' + link}"
#         }
#         products.append(product)
#     return products

# def clean_text(text):
#     text = re.sub(r'\xa0', ' ', text)
#     text = re.sub(r'\s+', ' ', text).strip()
#     return text

# # Configurações para ambos os supermercados
# configs = {
#     'supermercadoA': {
#         'base_url': "https://loja.supermercadosavenida.com.br", # LINK 
#         'product_list_selector': 'ul.product-grid > li', # onde esta todos os prodos em formato de tabela 
#         'name_selector': 'div.product-card-name-container', # nome do produto
#         'price_selector': 'span.new-price', # preco do produto
#         'link_selector': 'a[href]', # link do site 
#         'search_input_selector': 'input[name="search"]', # input para pesquisar 
#         'results_container_selector': '.product-listing__results', # onde estão todos os produtos 
#         'text_city_selector': None
#     },
#     'supermercadoB': {
#         'base_url': "https://www.amigao.com",
#         'product_list_selector': 'li.item.product.product-item',
#         'name_selector': 'div.product-content',
#         'price_selector': 'span.price',
#         'link_selector': 'a[href]',
#         'search_input_selector': 'input[id="search"]',
#         'results_container_selector': 'div.column main',
#         'text_city_selector': True
#     }
# }

# # Exemplo de como iniciar a busca
# resultsA = get_product_data(configs['supermercadoA']['base_url'], "salgadinho", None, configs['supermercadoA'])
# resultsB = get_product_data(configs['supermercadoB']['base_url'], "café", "Ourinhos", configs['supermercadoB'])

# Teste para o mercado são judas

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def scroll_to_load_products(url, product_name):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url)
    print("Site carregado.")
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.TAG_NAME, 'body')))  # Assegura que o corpo da página está visível

    try:
        # Fecha o modal se presente
        try:
            modal_close = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'close')))
            modal_close.click()
            print("Modal fechado.")
        except Exception as e:
            print("Modal não encontrado ou já fechado:", e)

        # Encontra e interage com o campo de busca
        search_box = driver.find_element(By.CSS_SELECTOR, 'input[type="search"]')
        search_box.clear()
        search_box.send_keys(product_name)
        search_box.send_keys(Keys.RETURN)
        print(f"Busca pelo produto '{product_name}' realizada.")
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.container')))  # Espera até que os resultados sejam visíveis

        # Executa a rolagem contínua até o final da página ou até que uma condição específica seja atingida
        num_products = 0
        while True:
            # Rolagem para baixo
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)  # Espera a página carregar mais produtos
            
            # Verifica se o número de produtos aumentou
            new_num_products = len(driver.find_elements(By.CSS_SELECTOR, 'div.item'))
            if new_num_products == num_products:
                print("Nenhum novo produto carregado, fim da rolagem.")
                break
            num_products = new_num_products
            print(f"{num_products} produtos carregados até agora.")

        # Extrai informações dos produtos
        products = driver.find_elements(By.CSS_SELECTOR, 'div.item')
        print(f"Extraindo dados de {len(products)} produtos.")
        for product in products:
            name = product.find_element(By.CLASS_NAME, 'ellipsis-2').text
            price = product.find_element(By.CLASS_NAME, 'text-center').text
            link = product.find_element(By.CLASS_NAME, 'link-nome-produto').get_attribute('href')
            print(f'Nome: {name}, Preço: {price}, Link: {link}')
    except Exception as e:
        print("Erro durante a extração de dados dos produtos:", e)
    finally:
        driver.quit()

# URL do site e produto a buscar
url = "https://compreonline.supersaojudas.com.br/loja6/"
product_name = "energetico"

scroll_to_load_products(url, product_name)





# Código rodando o mercado lavilla 
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.service import Service
# import time

# def get_product_data(url, search_term):
#     options = Options()
#     options.add_argument("--window-size=1920,1080")
#     options.headless = False  # Execute sem headless para diagnóstico

#     service = Service(ChromeDriverManager().install())
#     driver = webdriver.Chrome(service=service, options=options)

#     driver.get(url)

#     wait = WebDriverWait(driver, 20)

#     try:
#         print("Procurando campo de busca...")
#         search_box = wait.until(EC.visibility_of_element_located((By.NAME, "search")))
#         search_box.clear()
#         search_box.send_keys(search_term + Keys.RETURN)

#         print("Busca enviada, aguardando carregamento dos produtos...")
#         wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.list-product-item")))
#         print("Produtos carregados.")

#         produtos = []
#         product_elements = driver.find_elements(By.CSS_SELECTOR, "div.list-product-item")
#         for produto in product_elements:
#             nome = produto.find_element(By.CSS_SELECTOR, ".txt-desc-product-itemtext-muted.txt-desc-product-item").text
#             preço = produto.find_element(By.CSS_SELECTOR, ".area-bloco-preco.bloco-preco.pr-0.ng-star-inserted").text
#             url = produto.find_element(By.CSS_SELECTOR, "a.list-product-link").get_attribute('href')
#             produtos.append({"nome": nome, "preço": preço, "url": url})
#             print(f"Capturado: {nome}, {preço}, {url}")

#         return produtos
#     except Exception as e:
#         print(f"Erro ao raspar dados: {e}")
#     finally:
#         driver.quit()

# # Teste da função
# if __name__ == "__main__":
#     result = get_product_data("https://www.sitemercado.com.br/supermercadolavilla/ourinhos-loja-ourinhos-jardim-matilde-r-do-expedicionario/", "sorvete")
#     print(result)

# Teste pão de açucar 
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import NoSuchElementException, TimeoutException
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.service import Service
# import time

# def get_product_data(url, search_term):
#     options = Options()
#     options.add_argument("--window-size=1920,1080")
#     options.headless = True  # Set to True for faster execution without UI

#     service = Service(ChromeDriverManager().install())
#     driver = webdriver.Chrome(service=service, options=options)
#     driver.get(url)
#     wait = WebDriverWait(driver, 20)

#     try:
#         print("Procurando campo de busca...")
#         search_box = wait.until(EC.visibility_of_element_located((By.NAME, "search")))
#         search_box.clear()
#         search_box.send_keys(search_term + Keys.RETURN)

#         print("Busca enviada, aguardando carregamento dos produtos...")
#         wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.MuiGrid-root gridstyles-sc-6scn59-0 cinTPm MuiGrid-container MuiGrid-spacing-xs-2")))
# # MuiGrid-root gridstyles-sc-6scn59-0 cinTPm MuiGrid-container MuiGrid-spacing-xs-2
#         # Scroll down logic
#         last_height = driver.execute_script("return document.body.scrollHeight")
#         while True:
#             driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#             time.sleep(5)  # Allow time for page to load
#             new_height = driver.execute_script("return document.body.scrollHeight")
#             if new_height == last_height:
#                 break
#             last_height = new_height

#         products = []
#         product_elements = driver.find_elements(By.CSS_SELECTOR, "div.MuiGrid-root gridstyles-sc-6scn59-0 cinTPm MuiGrid-container MuiGrid-spacing-xs-2")
#         print(f"Number of product containers found: {len(product_elements)}")

#         for product in product_elements:
#             try:
#                 name = product.find_element(By.CSS_SELECTOR, ".product-cardstyles__Text-sc-1uwpde0-7.hXaJKO").text
#                 price = product.find_element(By.CSS_SELECTOR, ".placeholderstyles__PlaceholderContainer-sc-1m777zk-0.sealsstyles__SealsStyled-sc-173rinj-0.iawOji").text
#                 product_url = product.find_element(By.CSS_SELECTOR, "a.product-cardstyles__Link-sc-1uwpde0-9.bSQmwP.hyperlinkstyles__Link-j02w35-0.coaZwR").get_attribute('href')
#                 products.append({"name": name, "price": price, "url": product_url})
#                 print(f"Captured: {name}, {price}, {product_url}")
#             except NoSuchElementException:
#                 print("One or more elements were not found within a product element.")
#                 continue

#         return products
#     except TimeoutException:
#         print("The page timed out while loading the search results.")
#     except Exception as e:
#         print(f"An error occurred: {e}")
#     finally:
#         driver.quit()

# # Test the function
# if __name__ == "__main__":
#     result = get_product_data("https://www.paodeacucar.com/?utm_source=bing&utm_medium=cpc&utm_campaign=pda-institucional-sp-marca&utm_term=institucional-paodeacucar-search-sp&utm_content=home-cpc-keyword-conversao&msclkid=02cb5bd9145312c6a0883deb2cb989bc", "papel higienico")
#     print(result)