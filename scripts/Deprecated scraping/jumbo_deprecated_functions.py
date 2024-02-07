from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from random import randint



""" 

    DEPRECATED FUNCTION (old page version since 14/1/2024)

"""

#Devuelve la cantidad total de productos de la categoría actual
def get_products_numbers_DEPRECATED_VERSION(browser, text_xpath):
    total_height = browser.execute_script("return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight );")
    middle_height = total_height // 2
    while not 'text_element' in locals():
        browser.execute_script(f"window.scrollTo(0, {middle_height});")
        browser.execute_script(f"window.scrollTo(0, {randint(0,middle_height)});")
        try:
            text_element = browser.find_element(By.XPATH, text_xpath)
        except Exception as e:
            print(f"Error en get_products_number: \n {e}")

    max_products=0
    while max_products==0:
        text_html = text_element.get_attribute('innerHTML')
        text_re = r'Mostrando<!-- --> <strong>(\d+)<!-- --> de <!-- -->(\d+)</strong>' if "<!-- -->" in text_html else r'Mostrando <strong>(\d+) de (\d+)</strong>'
        match = re.search(text_re, text_html)  
        try:
            actual_products = int(match.group(1))
            max_products = int(match.group(2))
        except:
            pass
    print(str(actual_products)," productos cargados de ", str(max_products),"\n")
    products_numbers = {}
    products_numbers["actual"] = actual_products
    products_numbers["final"] = max_products
    return products_numbers

#Scrolea lentamente desde la última card analizada de la página hasta el pie
def soft_scroll_DEPRECATED_VERSION(browser,button_xpath,products_element,is_final_page):
    scroll_to_element_js_code = "arguments[0].scrollIntoView({behavior: 'auto', block: 'center', inline: 'center'});"
    browser.execute_script(scroll_to_element_js_code, products_element[len(products_element)//2])
    while True:
        # Desplazarse hacia abajo en pequeños pasos
        browser.execute_script("window.scrollTo(0, window.scrollY + 500);")
        current_position = browser.execute_script("return window.scrollY;")
        
        #Va a los últimos 5 elementos para la carga de los productos que quedan por cargar  
        if not 'next_button' in locals() and not is_final_page:
            next_button = WebDriverWait(browser, 20).until(
                EC.presence_of_element_located((By.XPATH,button_xpath))
            )
            browser.execute_script(scroll_to_element_js_code, next_button)
            if len(products_element)>=20:
                browser.execute_script(scroll_to_element_js_code, products_element[randint(-5,-1)])
            break

        height = browser.execute_script("return document.body.scrollHeight")
        if current_position + browser.execute_script("return window.innerHeight;") >= height:
            break

#Scrapear productos por página
def category_products_page_DEPRECATED_VERSION(browser,start,final,last_products_element,is_final_page):
    xpath = {
        "product card": "//article[contains(@class,'vtex-product-summary-2-x-element pointer pt3 pb4 flex flex-column h-100')]",
        "price": ".//div[@class='jumboargentinaio-store-theme-1dCOMij_MzTzZOCohX1K7w']",
        "brand": ".//span[@class='vtex-product-summary-2-x-productBrandName']",
        "description": ".//span[@class='vtex-product-summary-2-x-productBrand vtex-product-summary-2-x-brandName t-body']",
        "image": ".//img[@class='vtex-product-summary-2-x-imageNormal vtex-product-summary-2-x-image']",
        "next button": "//button[@class='vtex-button bw1 ba fw5 v-mid relative pa0 lh-solid br2 min-h-small t-action--small bg-action-primary b--action-primary c-on-action-primary hover-bg-action-primary hover-b--action-primary hover-c-on-action-primary pointer ']"
    }
    products_element_aux = WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, xpath["product card"]))
    )
    products = []
    products_element = array_union(array1=last_products_element,array2=products_element_aux)

    while len(products_element)!=final:
        print(f"FINAL: {final}\nELEMENTOS EN PRODUCTS_ELEMENT: {len(products_element)}")
        soft_scroll(browser=browser, button_xpath=xpath["next button"],products_element=products_element_aux,is_final_page=is_final_page)
        products_element_aux = WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, xpath["product card"]))
        )
        products_element = array_union(array1=last_products_element,array2=products_element_aux)

    for product_element in products_element[start:final-1]:
        product = get_product_info(browser=browser,xpath=xpath, product_element=product_element)
        products.append(product)

    write_to_csv(products=products)

    return products_element

#Scrapear productos de una categoría
def category_products_DEPRECATED_VERSION(browser,link):
    products_per_page = 20
    xpath = {
        "text with products quantity": "//p[@class='text-content']",
        "next button": "//button[@class='vtex-button bw1 ba fw5 v-mid relative pa0 lh-solid br2 min-h-small t-action--small bg-action-primary b--action-primary c-on-action-primary hover-bg-action-primary hover-b--action-primary hover-c-on-action-primary pointer ']",
    }

    browser.get(link)


    """ 
    Cantidad total de productos en la página puede ser pensada como el modulo 
    de products_per_page más un múltiplo de ese número.
    Es decir, la sobra de dividir el total_products por products_per_page, más actual_products_numbers*X

    Siendo X el número de vueltas hasta llegar al la penúltima página 
    """
    total_products = get_products_numbers(browser=browser,text_xpath=xpath["text with products quantity"])["final"]
    actual_products_number = 0
    is_final_page = 0
    products_element = []

    while not is_final_page:
        is_final_page = (actual_products_number + total_products%products_per_page) == total_products
        final = total_products if is_final_page else actual_products_number+products_per_page
        products_element = category_products_page(browser=browser,start=actual_products_number,final=final,last_products_element=products_element,is_final_page=is_final_page)
        actual_products_number += final
        if not is_final_page:
            click_see_more_button(browser=browser, button_xpath=xpath["next button"])
        actual_products_number = get_products_numbers(browser=browser,text_xpath=xpath["text with products quantity"])["actual"]

# Clickea el botón de "Mostrar más"
def click_see_more_button_DEPRECATED_VERSION(browser,button_xpath):
    next_button = WebDriverWait(browser, 20).until(
        EC.element_to_be_clickable((By.XPATH,button_xpath))
    )
    browser.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center', inline: 'center'});", next_button)
    next_button.click()

# Concatena dos arrays, ignorando los elementos repetidos
def array_union_DEPRECATED_VERSION(array1, array2):
    union = array1
    for item in array2:
        if item not in array1:
            union.append(item)
    return union


