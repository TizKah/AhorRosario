from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import os, time, re, requests
from random import randint
from database_manage import insert_into_db

LOAD_TIME = 3

ACTUAL_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

def internet_connection():
    try:
        response = requests.get("https://www.jumbo.com.ar/", timeout=5) 
        return True
    except:
        return False
# --

#Scrapear productos por página
def category_products_page(browser,page_url,is_final_page,categories_names):
    browser.get(page_url)
    browser.execute_script("document.body.style.zoom='30%'")
    xpath = {
        "product card": "//article[contains(@class,'vtex-product-summary-2-x-element pointer pt3 pb4 flex flex-column h-100')]",
        "price": ".//div[@class='jumboargentinaio-store-theme-1dCOMij_MzTzZOCohX1K7w']",
        "brand": ".//span[@class='vtex-product-summary-2-x-productBrandName']",
        "description": ".//span[@class='vtex-product-summary-2-x-productBrand vtex-product-summary-2-x-brandName t-body']",
        "image": ".//img[@class='vtex-product-summary-2-x-imageNormal vtex-product-summary-2-x-image']",
        "next button": "//button[@class='vtex-button bw1 ba fw5 v-mid relative pa0 lh-solid br2 min-h-small t-action--small bg-action-primary b--action-primary c-on-action-primary hover-bg-action-primary hover-b--action-primary hover-c-on-action-primary pointer ']"
    }
    
    products_element = get_all_page_products_cards(browser=browser,xpath=xpath,is_final_page=is_final_page)

    products = []

    for product_element in products_element:
        product = get_product_info(browser=browser,xpath=xpath, product_element=product_element)
        if product!={}:
            products.append(product)

    if product!={}:
        insert_into_db(products=products,
                       categories_names=categories_names,
                       page_url=page_url)

#Scrapear productos de una categoría
def category_products(browser,link,categories_names):
    xpath = {
        "next button": "//button[@class='vtex-button bw1 ba fw5 v-mid relative pa0 lh-solid br2 min-h-small t-action--small bg-action-primary b--action-primary c-on-action-primary hover-bg-action-primary hover-b--action-primary hover-c-on-action-primary pointer ']",
        "text with pages numbers": "//span[@class='discoargentina-search-result-custom-1-x-span-selector-pages']"
    }

    browser.get(link)
    browser.execute_script("document.body.style.zoom='30%'")

    total_pages = get_products_pages_numbers(browser=browser,text_xpath=xpath["text with pages numbers"])["final"]
    if total_pages==0 or total_pages=='empty page':
        return
    
    # BUG DE PÁGINA AL PASAR PÁGINA 50
    if total_pages>50:
        total_pages=50

    for page_number in range(1,total_pages+1):
        """ print("Categoria: ", categories_names['category'], "\nSubcategoria: ", categories_names['subcategory'])
        print(str(page_number)," páginas cargadas de ", str(total_pages),"\n") """
        next_page_url = get_new_page_link(link=link,page_number=page_number)
        category_products_page(browser=browser,
                               page_url=next_page_url,
                               is_final_page=(page_number==total_pages),
                               categories_names=categories_names)




#Scrolea desde el inicio de la página hasta el final de la página
def scroll_complete_page(browser,height):
    browser.execute_script(f"window.scrollTo(0, 0);")
    browser.execute_script("window.scrollTo(0, window.scrollY + 500);")
    browser.execute_script(f"window.scrollTo(0, {height//2});")
    browser.execute_script("window.scrollTo(0, window.scrollY + 500);")
    browser.execute_script(f"window.scrollTo(0, {height});")
    browser.execute_script(f"window.scrollTo(0, 0);")

#Se encarga de cargar las cards y devuelve un array con los WebElement de los productos
def get_all_page_products_cards(browser,xpath,is_final_page):
    products_element = []
    scroll_to_element_js_code = "arguments[0].scrollIntoView({behavior: 'auto', block: 'center', inline: 'center'});"
    height = browser.execute_script("return document.body.scrollHeight")
    while len(products_element)<20:
        
        """ if not internet_connection():
            print("Error de conexión, reiniciando página...")
            browser.refresh()
            continue """

        """ browser.execute_script("window.scrollTo(0, window.scrollY + 500);")
        browser.execute_script("window.scrollTo(0, window.scrollY + 500);")
        browser.execute_script(f"window.scrollTo(0, {height//2});")
        browser.execute_script("window.scrollTo(0, window.scrollY + 500);") """
        """ products_element= WebDriverWait(browser, 50).until(
            EC.presence_of_all_elements_located((By.XPATH, xpath["product card"]))
        )
        """
        products_element = browser.find_elements(By.XPATH, xpath["product card"])
        try:
            browser.execute_script(scroll_to_element_js_code, products_element[-1])
        except:
            pass 
        #scroll_complete_page(browser=browser,height=height)
        browser.execute_script(f"window.scrollTo(0, {height});")
        #browser.execute_script("window.scrollTo(0, window.scrollY + 500);")
        
        """ print(f"Cargados {len(products_element)} elementos\n") """
        if is_final_page:
            break
    return products_element

#Parsea la url de una categoría para pasar a la siguiente página
def get_new_page_link(link,page_number):
    return link + f"?page={page_number}"

#Devuelve un dict con la página "actual" y la página "final" de la categoría actual
def get_products_pages_numbers(browser, text_xpath):
    empty_page_html = 'La página que estás buscando no existe.'
    total_height = browser.execute_script("return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight );")
    middle_height = total_height // 2
    while not 'text_element' in locals():
        browser.execute_script(f"window.scrollTo(0, {middle_height});")
        browser.execute_script(f"window.scrollTo(0, {randint(0,middle_height)});")
        try:
            text_element = browser.find_element(By.XPATH, text_xpath)
        except Exception as e:
            print(f"Error en get_products_number: \n {e}")

            if empty_page_html in browser.page_source:
                print("Página vacía, pasando a la siguiente...")
                return {"actual":'empty page',
                        "final":'empty page'}
            
            browser.refresh()
            #time.sleep(LOAD_TIME)
    
    actual_products=-1
    max_products=0
    while max_products==0 and actual_products==-1:
        text_html = text_element.get_attribute('innerHTML')
        text_re = r'Página <!-- -->(\d+)<!-- --> de <!-- -->(\d+)' if "<!-- -->" in text_html else r'Página (\d+) de (\d+)'
        match = re.search(text_re, text_html)  
        actual_products = int(match.group(1))
        max_products = int(match.group(2))

    products_numbers = {"actual":actual_products,
                        "final":max_products}
    return products_numbers

#Devuelve un diccionario con toda la información del producto
def get_product_info(browser,xpath,product_element):
    scroll_to_element_js_code = "arguments[0].scrollIntoView({behavior: 'auto', block: 'center', inline: 'center'});"
    browser.execute_script(scroll_to_element_js_code, product_element)
    product = {}
    while True:
        try:
            product["price"] = product_element.find_element(By.XPATH, xpath["price"]).text
            while product["price"] == '' or product["price"]== '$NaN':
                product["price"] = product_element.find_element(By.XPATH, xpath["price"]).text
            product["description"] = product_element.find_element(By.XPATH, xpath["description"]).text
            product["brand"] = product_element.find_element(By.XPATH, xpath["brand"]).text
            product["market"] = "Jumbo"      
            product["image"] = get_image_url(product_element=product_element, image_xpath=xpath["image"])
            break
        except Exception as e:
            print(f"Error encontrado creando product:\n {e}")
            break
    return product

#Devuelve la url de la imagen de un producto
def get_image_url(product_element,image_xpath):
    scroll_js_code = "arguments[0].scrollIntoView();"
    try:
        image = product_element.find_element(By.XPATH, image_xpath).get_attribute('src')
    except:
        while not image:
            product_element.execute_script(scroll_js_code, product_element)
            image = product_element.find_element(By.XPATH, image_xpath).get_attribute('src')
            print("Esperando imagen de producto...")
            #time.sleep(LOAD_TIME)
    return image

# Devuelve el nombre de la categoría de la url dada
def get_category_name(url):
    url_parts = url.split("/")
    category_name = url_parts[-2]
    return category_name

# Devuelve el nombre de la subcategoría de la url dada
def get_subcategory_name(url):
    url_parts = url.split("/")
    subcategory_name = url_parts[-1]
    return subcategory_name

# Devuelve un dict con dos arreglos con urls. Uno con el de la categoría y otro con las subcategorías
def get_category_links(browser):
    xpath = {
        "categories button": "//div[contains(@class,'vtex-menu-2-x-styledLinkContent vtex-menu-2-x-styledLinkContent--header-category flex justify-between nowrap')]",
        "categories class":"//a[contains(@class,'vtex-menu-2-x-styledLink vtex-menu-2-x-styledLink--menu-item-secondary no-underline pointer t-body c-on-base pointer')]",
    }

    categories_visibility = WebDriverWait(browser, 20).until(
        EC.element_to_be_clickable((By.XPATH,xpath["categories button"]))
    )

    categories = []
    while(len(categories)==0):
        categories_visibility = WebDriverWait(browser, 20).until(
            EC.element_to_be_clickable((By.XPATH,xpath["categories button"]))
        )
        time.sleep(LOAD_TIME)
        actions = ActionChains(browser) 
        actions.move_to_element(categories_visibility).perform()
        categories = browser.find_elements(By.XPATH,xpath["categories class"])
        if len(categories)==0:
            print("Problemas obteniendo enlaces, recargado página...")
            browser.refresh()


    urls = [category.get_attribute('href') for category in categories]
    return {"text":urls,"elements":categories}

def get_subcategory_links(browser,urls_element):
    xpath = {
        "alone subcategory class": "//a[@class='vtex-menu-2-x-styledLink vtex-menu-2-x-styledLink--item-submenu-list-custom no-underline pointer t-body c-on-base pointer']",
        "not alone subcategory class": "//a[@class='vtex-menu-2-x-styledLink vtex-menu-2-x-styledLink--item-submenu-list no-underline pointer t-small fw5 c-on-base pointer']",
        "categories button": "//div[contains(@class,'vtex-menu-2-x-styledLinkContent vtex-menu-2-x-styledLinkContent--header-category flex justify-between nowrap')]",
    }

    subcategory_urls = []
    
    categories_visibility = WebDriverWait(browser, 20).until(
        EC.element_to_be_clickable((By.XPATH,xpath["categories button"]))
    )
    time.sleep(LOAD_TIME)
    actions = ActionChains(browser) 
    actions.move_to_element(categories_visibility).perform()
    
    for url_element in urls_element:
        actions = ActionChains(browser) 
        actions.move_to_element(url_element).perform()
        time.sleep(LOAD_TIME*3)

        alone_subcategory_urls_element = browser.find_elements(By.XPATH, xpath["alone subcategory class"])
        not_alone_subcategory_urls_element = browser.find_elements(By.XPATH, xpath["not alone subcategory class"])
        subcategory_urls_element = alone_subcategory_urls_element + not_alone_subcategory_urls_element
        subcategory_urls.extend(element.get_attribute('href') for element in subcategory_urls_element)

    return subcategory_urls

#Inicia el navegador con posibles configuraciones
def start_browser(headless):
    service = Service(executable_path=f'{ACTUAL_DIRECTORY}/chromedriver.exe')
    chrome_options = webdriver.ChromeOptions() 
    if headless:
        chrome_options.add_argument('--headless=new')
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument('--log-level=1')
    chrome_options.add_argument('--blink-settings=imagesEnabled=false')
    chrome_options.add_argument(f'--disk-cache-dir={ACTUAL_DIRECTORY}/cache')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    browser = webdriver.Chrome(service=service, options=chrome_options)
    return browser 


# ERROR DE LA PÁGINA: https://www.jumbo.com.ar/Bebidas/Champagnes?page=3
# ERROR DE LA PÁGINA:  https://www.jumbo.com.ar/tiempo-libre/libreria?page=50
# BUG DE PÁGINA AL PASAR PÁGINA 50 -> si total_page>50 entonces total_page=50

# -- Implementación de Threads --
import threading
MAX_CONCURRENT_THREADS = 2  # Puedes ajustar este número según tus necesidades
thread_semaphore = threading.Semaphore(MAX_CONCURRENT_THREADS)

def scrape_subcategory(url, categories_names):
    with thread_semaphore:
        browser = start_browser(True)
        print("Categoria: ", categories_names['category'], "\nSubcategoria: ", categories_names['subcategory'])
        try:
            category_products(browser=browser, link=url, categories_names=categories_names)
        except Exception as e:
            with open(f"{ACTUAL_DIRECTORY}/log.txt", "a+") as f:
                f.write(f"""Categoría: {categories_names['category']}\n
                        Subcategoría: {categories_names['subcategory']}\n
                        Error: {e}\n""")

        browser.quit()


def scrap_with_threads(browser,subcategory_urls):
    browser.quit()
    threads = []
    for url in subcategory_urls:
        print(url)
        categories_names = {
            'category': get_category_name(url=url).upper(),
            'subcategory': get_subcategory_name(url=url).upper()
        }

        thread = threading.Thread(target=scrape_subcategory, args=(url, categories_names))
        threads.append(thread)
        thread.start()
        #subcategory_urls.remove(url)

    for thread in threads:
        thread.join()

def scrap_without_threads(browser,subcategory_urls):
    for url in subcategory_urls: 
        categories_names = {
            'category': get_category_name(url=url).upper(),
            'subcategory': get_subcategory_name(url=url).upper()
        }

        os.system('cls')
        print("Categoria: ", categories_names['category'], "\nSubcategoria: ", categories_names['subcategory'])
        try:
            category_products(browser=browser, link=url, categories_names=categories_names)
        except Exception as e:
            with open(f"{ACTUAL_DIRECTORY}/log.txt", "a+") as f:
                f.write(f"""Categoría: {categories_names['category']}\n
                        Subcategoría: {categories_names['subcategory']}\n
                        Error: {e}\n""")

        #subcategory_urls.remove(url)
    
    browser.quit()

def start_scrap(threads):
    browser = start_browser(True)
    browser.get("https://www.jumbo.com.ar/")
    subcategory_urls = manage_category_links(browser=browser)
    print(subcategory_urls)
    if threads:
        scrap_with_threads(browser=browser,subcategory_urls=subcategory_urls)
    else:
        scrap_without_threads(browser=browser,subcategory_urls=subcategory_urls)


def manage_category_links(browser):
    os.system('cls')
    print("Obteniendo enlaces...\n")
    subcategory_urls = []
    try:
        with open('jumbo_links.txt','r') as urls_file:
            for line in urls_file:
                subcategory_urls.append(line.strip().replace('\n', ''))
    except:
        urls = get_category_links(browser)
        subcategory_urls = get_subcategory_links(browser=browser, urls_element=urls["elements"])
        with open('jumbo_links.txt','w+') as urls_file:
            for url in subcategory_urls:
                if url!="https://www.jumbo.com.ar/-":
                    urls_file.write("%s\n" % url)
    print("Enlaces obtenidos con éxito.\n")
    return subcategory_urls

start_scrap(threads=True)