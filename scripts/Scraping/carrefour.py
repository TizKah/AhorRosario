from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import time, os
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from database_manage import insert_into_db

ACTUAL_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

TIME_LOAD = 2

def bs4_find_price(product_html,price_id):
    # Obtenemos el HTML del WebElement dado por Selenium
    html = product_html.get_attribute('innerHTML')

    # Parseamos el html para analizarlo con bs4
    soup = BeautifulSoup(html, 'html.parser')

    # Buscamos el precio y lo pasamos a texto legible
    price_span = soup.find(price_id["tag"], class_=price_id["class"])
    price_text = price_span.text.strip()
    return price_text

def load_products(browser):
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(TIME_LOAD)
    total_height = browser.execute_script("return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight );")
    middle_height = total_height / 2
    browser.execute_script(f"window.scrollTo(0, {middle_height});")
    browser.execute_script(f"window.scrollTo(0, 0);")
    browser.execute_script(f"window.scrollTo(0, {middle_height});")

def scrap_category_page(browser,enlace,categories_names):
    xpath = {
        "cookie button": "//button[text()='Aceptar todo']",
        "products": "//div[contains(@class, 'valtech-carrefourar-product-summary-status-0-x-container')]",
        "description": ".//span[contains(@class, 'vtex-product-summary-2-x-productBrand') or contains(@class, 'vtex-product-summary-2-x-brandName')]",
        "image":".//img[@class='vtex-product-summary-2-x-imageNormal vtex-product-summary-2-x-image']"
    }
    price_id = {"tag":"span",
                "class":"valtech-carrefourar-product-price-0-x-currencyContainer"}

    browser.get(enlace)
    time.sleep(TIME_LOAD)
    
    load_products(browser)

    products = []
    products_html = []
    # VER CASO FINAL DE CATEGORIA
    products_html = browser.find_elements(By.XPATH,xpath["products"])
    if(len(products_html)<16):
        time.sleep(TIME_LOAD)
        products_html = browser.find_elements(By.XPATH,xpath["products"])

    for product_html in products_html:
        product = {}
        try:
            product["description"] = product_html.find_element(By.XPATH,xpath["description"]).text
            product["price"] = bs4_find_price(product_html,price_id)
            product["brand"] = 'Unknowed'
            product["image"] = get_image_url(product_element=product_html, image_xpath=xpath["image"])
            product["market"] = "Carrefour"
            products.append(product)
        except:
            pass
 
    insert_into_db(products=products,categories_names=categories_names)

def next_page(enlace,page):
    return enlace + f"?page={page}"

#Devuelve la url de la imagen de un producto
def get_image_url(product_element,image_xpath):
    scroll_js_code = "arguments[0].scrollIntoView();"
    try:
        image = product_element.find_element(By.XPATH, image_xpath).get_attribute('src')
    except:
        while not image:
            product_element.execute_script(scroll_js_code, product_element)
            image = product_element.find_element(By.XPATH, image_xpath).get_attribute('src')
            time.sleep(TIME_LOAD)
    return image


def scrap_category(browser,original_link,subcategory_urls):
    xpath = {
        "cookie button": "//button[text()='Aceptar todo']",
        "category number": "//div[contains(@class, 'vtex-button__label flex items-center justify-center h-100 ph5')]"
    }
    categories_names = {}
    categories_names['category'] = get_category(original_link)

    for subcategory_url in subcategory_urls:
        browser.get(subcategory_url)

        load_products(browser)
        WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.XPATH,xpath["category number"]))
        )

        categories_names['subcategory'] = get_category(subcategory_url)
        try:
            final_category_number = int(browser.find_elements(By.XPATH,xpath["category number"])[-2].text)
        except:
            final_category_number = 1

        for page in range(1,final_category_number+1):
            #os.system('cls')
            print(f"Categoría: {categories_names['category']}\nSubcategoría: {categories_names['subcategory']}\nPágina: {page}.\n")
            link = next_page(subcategory_url,page)
            scrap_category_page(browser,link,categories_names)

def start_browser():
    service = Service(executable_path=f'{ACTUAL_DIRECTORY}/chromedriver.exe')
    chrome_options = webdriver.ChromeOptions() 
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument('--log-level=1')
    browser = webdriver.Chrome(service=service, options=chrome_options)
    browser.get("https://www.carrefour.com.ar/")
    return browser    

def start_scrap():
    browser = start_browser()
    os.system('cls')
    print("Obteniendo enlaces...\n")
    urls = get_category_links(browser)
    print("Enlaces obtenidos con éxito.\n")

    """ for original_link in urls["category"]:
        print("-- CAMBIANDO CATEGORÍA -- \n")
        category_name = get_category(original_link)
        browser.quit() """
        #scrap_category(browser,original_link,urls["subcategory"][category_name])
    with ThreadPoolExecutor(max_workers=3) as executor:
        for original_link in urls["category"]:
            category_name = get_category(original_link)
            executor.submit(thread_scrap_category, original_link,urls["subcategory"][category_name])

    print("Scrapeo finalizado con éxito.\n")
    browser.quit()

# Devuelve un dict con dos arreglos con urls. Uno con el de la categoría y otro con las subcategorías
def get_category_links(browser):
    xpath = {
        "categories button": "//div[contains(@role,'button')]",
        "categories class":"//div[contains(@class,'vtex-menu-2-x-styledLinkContent vtex-menu-2-x-styledLinkContent--MenuCategoryFirstItem flex justify-between nowrap')]",
        "cookies button": "//button[text()='Aceptar todo']",
        "category url": "//a[contains(span,'Ver todo')]",
        "subcategory url": "//a[contains(@class,'vtex-menu-2-x-styledLink vtex-menu-2-x-styledLink--MenuCategorySecondItem-hasSubmenu vtex-menu-2-x-styledLink--highlight vtex-menu-2-x-styledLink--MenuCategorySecondItem-hasSubmenu--highlight no-underline pointer t-small c-emphasis pointer')]"
    }

    urls = {
        "category": [],
        "subcategory": {}
    }

    WebDriverWait(browser, 20).until(
    EC.presence_of_element_located((By.XPATH,xpath["categories button"]))
    )
    categories_visibility = browser.find_elements(By.XPATH, xpath["categories button"])[1]
    categories_visibility.click()
    categories = browser.find_elements(By.XPATH,xpath["categories class"])

    time.sleep(5)
    browser.find_elements(By.XPATH, xpath["cookies button"])[1].click()

    for category in categories:
        category.click()
        try:
            time.sleep(TIME_LOAD)
            enlace_element = browser.find_element(By.XPATH,xpath["category url"])
            category_url = enlace_element.get_attribute('href')
            category_url = remove_order_param(category_url)
            urls["category"].append(category_url)
            
            category_name = get_category(category_url)
            urls["subcategory"][category_name] = []
            
            subcategory_url_elements = browser.find_elements(By.XPATH, xpath["subcategory url"])
            for subcategory_url_element in subcategory_url_elements:
                subcategory_url = subcategory_url_element.get_attribute('href')
                subcategory_url = remove_order_param(subcategory_url)
                urls["subcategory"][category_name].append(subcategory_url)
        except:
            pass

    return urls

def get_category(url):
    url_parts = url.split("/")

    # Filtrar elementos vacíos
    not_empty_parts = [part for part in url_parts if part]

    # La categoría sería el último elemento no vacío
    if not_empty_parts:
        category = not_empty_parts[-1]
        return category
    else:
        print("Error obteniendo la categoría.")
        return None
    
def remove_order_param(url):
    url_parts = url.split('?')
    new_url = url_parts[0]
    return new_url

def thread_scrap_category(original_link,subcategory_urls):
    category_name = get_category(original_link)
    print(f"Iniciando scraping para la categoría: {category_name}")
    browser = start_browser()
    scrap_category(browser, original_link, subcategory_urls)

    browser.quit()



start_scrap()