import os, sqlite3, scrapy

ACTUAL_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
DATABASE_PATH = os.path.join(ACTUAL_DIRECTORY, '..', '..','..', 'products.db')

class JumboSpider(scrapy.Spider):
    name = "jumbo"
    #custom_settings = {'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    start_urls = [
        "https://www.jumbo.com.ar/hogar-y-textil?page=1"
    ]
 
    def parse(self, response):
        with open('html_response.txt', 'w+') as f:
            f.write(response.body.decode('utf-8'))
             
        """ products = []
        products_html = response.xpath("//li[contains(@class, 'clearfix')]")

        for product_html in products_html:
            product = {}
            product_description = product_html.xpath(".//*[contains(@class, 'descrip_full')]/text()").get()
            product["description"] = product_description

            product_price = product_html.xpath(".//*[contains(@class, 'atg_store_newPrice')]/text()").get().strip()
            product["price"] = product_price
            product["brand"] = 'Unknowed'
            
            product["image"] = product_html.xpath('.//span[@class="atg_store_productImage"]/img/@src').get()

            product["market"] = "Coto"

            products.append(product)

        self.insert_into_db(products)

        next_page = response.xpath("//a[@title='Siguiente']/@href").get()
        if next_page is not None:
            yield response.follow(next_page,self.parse) """

    def insert_into_db(self, products):
        conn = sqlite3.connect(DATABASE_PATH)
        conn.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT,
            price REAL,
            brand TEXT,
            image TEXT,
            market TEXT
        );
        ''')
        for product in products:
            conn.execute('''
            INSERT INTO products (description, price, brand, image, market)
            VALUES (?, ?, ?, ?, ?);
            ''', (product['description'], product['price'], product['brand'], product['image'], product['market']))

        conn.commit()
        conn.close()


