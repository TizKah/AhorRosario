import scrapy
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from coto_scrap.spiders.carrefour_link_scrap import get_links
import time

class CarreforSpider(scrapy.Spider):
    name = "carrefour"
    """custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    } """

    def start_requests(self):
        # Utiliza Selenium para cargar la página y obtener su contenido dinámico
        chrome_options = Options()
        #chrome_options.add_argument('--headless')  # Ejecución sin interfaz gráfica (headless)
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://www.carrefour.com.ar/Electro-y-tecnologia")
        time.sleep(15)  # Espera para asegurarse de que la página se cargue completamente

        # Crea una solicitud Scrapy con el contenido de la página cargada por Selenium
        yield scrapy.Request(url=driver.current_url, callback=self.parse_selenium_content)

        # Cierra el navegador después de obtener el contenido
        driver.quit()

    def parse_selenium_content(self, response):
        # Procesa el contenido de la página cargada por Selenium
        with open('html_response.txt', 'w+') as f:
            f.write(response.body.decode('utf-8'))

        xpath_price = "//span[@class='valtech-carrefourar-product-price-0-x-currencyCode']/following-sibling::span[@class='valtech-carrefourar-product-price-0-x-currencyInteger'] | //span[@class='valtech-carrefourar-product-price-0-x-currencyDecimal']/following-sibling::span[@class='valtech-carrefourar-product-price-0-x-currencyFraction']"
        xpath_products = "//article[contains(@class, 'vtex-product-summary-2-x-element vtex-product-summary-2-x-element--contentProduct pointer pt3 pb4 flex flex-column h-100')]"
        xpath_description = "//span[contains(@class, 'vtex-product-summary-2-x-productBrand vtex-product-summary-2-x-brandName t-body')]"
        products = []
        products_html = response.xpath(xpath_products)

        print(products_html)
        print('\nOLA Q ASE\n')

        for product_html in products_html:
            product = {}
            #product_description = product_html.xpath(".//*[contains(@class, 'descrip_full')]/text()").get()
            #product["description"] = product_description
            product["description"] = product_html.xpath(xpath_description)

            product_price = product_html.xpath(xpath_price).get().strip()
            product["price"] = product_price
            print(product_price)

            product["supermercado"] = "Carrefour"

            products.append(product)

        self.write_to_csv(products)

    def write_to_csv(self, products):
        with open('output_carrefour.csv', mode='a', newline='', encoding='utf-8') as file:
            fieldnames = ['description', 'price', 'supermercado']
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            # No escribas el encabezado en cada iteración
            # writer.writeheader()
            for product in products:
                writer.writerow(product)
