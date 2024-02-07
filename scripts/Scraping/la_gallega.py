from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support import expected_conditions as expect
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time, os, random, threading
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd


ACTUAL_DIRECTORY = os.path.dirname(os.path.realpath(__file__))




TIME_LOAD = 2


def nextPage(browser):
    try:
        browser.find_element(By.XPATH,"//input[@value='Siguiente']").click()
        return True
    except:
        return False


def getProductos(browser):
    WebDriverWait(browser, 20).until(
    EC.presence_of_element_located((By.XPATH,"//li[@class='cuadProd']"))
    )
    productosCaja = browser.find_elements(By.XPATH,"//li[@class='cuadProd']//div[@class='desc']")
    productos = []
    for producto in productosCaja:
        productos.append(producto.text)
    return productos


def getPrecios(browser):
    WebDriverWait(browser, 20).until(
    EC.presence_of_element_located((By.XPATH,"//li[@class='cuadProd']//div[@class='precio']"))
    )
    preciosCaja = browser.find_elements(By.XPATH,"//li[@class='cuadProd']//div[@class='precio']")
    precios = []
    for precio in preciosCaja:
        precios.append(precio.text)
    return precios


def configurarNavegador():
    service = Service(executable_path=f'{ACTUAL_DIRECTORY}/chromedriver.exe')
    #chrome_options = webdriver.ChromeOptions() 
    #chrome_options.add_argument('--headless=new')
    #chrome_options.add_argument("--window-size=1920,1080")
    #chrome_options.add_argument('--log-level=1')
    browser = webdriver.Chrome(service=service)
    browser.get("https://www.lagallega.com.ar/")
    categorias = getCategorias(browser,0)
    categorias.pop()
    
    nombreCategorias = []

    for i in range(1,len(categorias)):
        browser.get("https://www.lagallega.com.ar/")
        preciosList = []
        productosList = []
        categorias = getCategorias(browser,i)
        categorias.pop()
        categoria = categorias[i]
        nombreCategoria = categoria.text
        nombreCategorias.append(nombreCategoria)
        catPage = categoria.get_attribute("onclick")
        browser.execute_script(f"{catPage};")
        #categoria.click()
        time.sleep(TIME_LOAD)
        hayPagSiguiente = nextPage(browser)
        while(hayPagSiguiente):
            time.sleep(TIME_LOAD)
            precios = getPrecios(browser)
            preciosList += precios
            productos = getProductos(browser)
            productosList += productos
            hayPagSiguiente = nextPage(browser)


        productosDict = {'Nombre':productosList,'precio':preciosList}
        df_productos = pd.DataFrame(productosDict)
        nombreCategoriaFormat = nombreCategoria.strip().replace("/","-")
        df_productos.to_csv(f"{ACTUAL_DIRECTORY}/categorias/{nombreCategoriaFormat}.csv")

    categorias = {'categoria':nombreCategorias, 'Productos':productosDict}
        

    browser.quit()


def getCategorias(browser,i):
    WebDriverWait(browser, 20).until(
    EC.presence_of_element_located((By.XPATH,"//div[@id='Categorias']//dd"))
    )
    #browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    if(i>6):
        WebDriverWait(browser, 20).until(
        EC.presence_of_element_located((By.ID,"TxtVerMas"))
        )
        browser.find_element(By.ID,"TxtVerMas").click()
    return browser.find_elements(By.XPATH,"//div[@id='Categorias']//dd")



configurarNavegador()