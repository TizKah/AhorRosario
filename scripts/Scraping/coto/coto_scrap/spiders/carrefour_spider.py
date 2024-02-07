import scrapy
import csv
from coto_scrap.spiders.carrefour_link_scrap import get_links
import time


class CarreforSpider(scrapy.Spider):
    name = "carrefour"
    custom_settings = {'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    #start_urls = get_links()
    start_urls = [
        "https://www.carrefour.com.ar/Electro-y-tecnologia"
    ]


    """ def parse(self, response):
        with open('contenido_pagina.txt', 'w', encoding='utf-8') as file:
            file.write(response.body.decode('utf-8')) """

    def parse(self, response):
        time.sleep(15)
        xpath_price = "//span[@class='valtech-carrefourar-product-price-0-x-currencyCode']/following-sibling::span[@class='valtech-carrefourar-product-price-0-x-currencyInteger'] | //span[@class='valtech-carrefourar-product-price-0-x-currencyDecimal']/following-sibling::span[@class='valtech-carrefourar-product-price-0-x-currencyFraction']"
        xpath_products = "//div[contains(@class, 'valtech-carrefourar-product-summary-status-0-x-container valtech-carrefourar-product-summary-status-0-x-productNotAdded flex flex-column h-100')]"
        products = []
        products_html = response.xpath('//*[contains(@class, "valtech-carrefourar-product-summary-status-0-x-container")]')

        print(products_html)

        for product_html in products_html:
            product = {}
            #product_description = product_html.xpath(".//*[contains(@class, 'descrip_full')]/text()").get()
            #product["description"] = product_description
            product["description"] = "X"

            product_price = product_html.xpath(xpath_price).get().strip()
            product["price"] = product_price
            print(product_price)
            
            product["supermercado"] = "Carrefour"

            products.append(product)

        self.write_to_csv(products)

    def write_to_csv(self, products):
        with open('output_carrefour.csv', mode='a', newline='', encoding='utf-8') as file:
            fieldnames = ['description', 'price','supermercado']
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            writer.writeheader()
            for product in products:
                writer.writerow(product)


