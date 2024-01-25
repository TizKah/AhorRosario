from selenium import webdriver
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from bs4 import BeautifulSoup



url_supermercado = 'https://www.cotodigital3.com.ar/sitios/cdigi/'

# Imprime el título y el enlace de la categoría
def print_categorias(titulo_categoria, enlace_categoria, url_categoria):
    print(f"Título: {titulo_categoria}")
    print(f"Enlace relativo: {enlace_categoria}")
    print(f"Enlace total: {url_categoria}")
    print("\n")

# Obtiene el HTML de la página cargada con browser real
def get_real_html():
    # Especifica la ubicación del chromedriver.exe
    chromedriver_path = r'C:\Users\Tiziano\Desktop\Scrap\chromedriver.exe'

    # Configura el controlador de Selenium con la ubicación del chromedriver
    driver = webdriver.Chrome(executable_path=chromedriver_path)

    # Cargar la página web con Selenium
    driver.get(url_supermercado)

    # Obtener el contenido de la página después de que se haya cargado completamente
    pagina_web = driver.page_source

    # Cerrar el controlador de Selenium
    driver.quit()

    return pagina_web

# Obtiene links a cada categoría
def get_urls_categorias():
    # Analizar la página web con BeautifulSoup
    pagina_web = get_real_html()
    soup = BeautifulSoup(pagina_web, 'html.parser')

    # Encuentra la lista de categorías en "categories-footer"
    categorias_footer = soup.find('ul', id='categories-footer')
    if categorias_footer:
        # Filtra los elementos que no son scripts
        categorias = [categoria for categoria in categorias_footer.find_all('li', recursive=False) if not categoria.find('script')]

        for categoria in categorias:
            if(categoria.text == "CATEGORÍAS"):
                continue
            # Accede al título de la categoría
            titulo_categoria = categoria.text.strip()

            # Busca el enlace
            enlace_categoria = categoria.find('a')
            # Accede al enlace de la categoría
            enlace_categoria = enlace_categoria['href']
            
            url_categoria = "https://www.cotodigital3.com.ar" + str(enlace_categoria)
            
            # Imprime el título y el enlace de la categoría
            print_categorias(titulo_categoria, enlace_categoria, url_categoria)
        
get_urls_categorias()