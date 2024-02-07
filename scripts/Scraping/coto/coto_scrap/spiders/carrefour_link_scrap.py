from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import time, os

ACTUAL_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
categories_class = 'vtex-menu-2-x-styledLinkContent vtex-menu-2-x-styledLinkContent--MenuCategoryFirstItem flex justify-between nowrap'




TIME_LOAD = 2

def get_links():
    service = Service(executable_path='C:/Users/Tiziano/coto_scrap/coto_scrap/spiders/chromedriver.exe')
    #chrome_options = webdriver.ChromeOptions() 
    #chrome_options.add_argument('--headless=new')
    #chrome_options.add_argument("--window-size=1920,1080")
    #chrome_options.add_argument('--log-level=1')
    browser = webdriver.Chrome(service=service)
    browser.get("https://www.carrefour.com.ar/")

    categories_links = []
    WebDriverWait(browser, 20).until(
    EC.presence_of_element_located((By.XPATH,"//div[contains(@role,'button')]"))
    )
    categories_visibility = browser.find_elements(By.XPATH, "//div[contains(@role,'button')]")[1]
    categories_visibility.click()
    categories = browser.find_elements(By.XPATH,f"//div[contains(@class,'{categories_class}')]")

    time.sleep(5)
    cookies_button = browser.find_elements(By.XPATH, "//button[text()='Aceptar todo']")[1]
    cookies_button.click()

    for categorie in categories:
        categorie.click()
        # Obtener el contenido HTML de la página después de que haya cargado
        # Encontrar el elemento <a> que contiene el <span> con el texto "VER TODO"
        try:
            time.sleep(TIME_LOAD)
            enlace_element = browser.find_element(By.XPATH,"//a[contains(span,'Ver todo')]")

            # Obtener el atributo href del elemento <a>
            if enlace_element:
                enlace = enlace_element.get_attribute('href')
                categories_links.append(enlace)
            else:
                print('No se encontró el enlace.')
        except:
            pass

    browser.quit()

    return categories_links

