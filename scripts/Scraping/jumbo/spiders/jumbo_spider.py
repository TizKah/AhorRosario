import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import json
import re

from scrapy_selenium import SeleniumRequest
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


class MySpider(CrawlSpider):
    name = "jumbo"
    allowed_domains = ["jumbo.com.ar"]
    start_urls = []
    xpath = {
        "product card": "//article[contains(@class,'vtex-product-summary-2-x-element pointer pt3 pb4 flex flex-column h-100')]",
        "price": ".//div[@class='jumboargentinaio-store-theme-1dCOMij_MzTzZOCohX1K7w']/text()",
        "brand": ".//span[@class='vtex-product-summary-2-x-productBrandName']",
        "description": ".//span[@class='vtex-product-summary-2-x-productBrand vtex-product-summary-2-x-brandName t-body']/text()",
        "image": ".//img[@class='vtex-product-summary-2-x-imageNormal vtex-product-summary-2-x-image']",
        "next button": "//button[@class='vtex-button bw1 ba fw5 v-mid relative pa0 lh-solid br2 min-h-small t-action--small bg-action-primary b--action-primary c-on-action-primary hover-bg-action-primary hover-b--action-primary hover-c-on-action-primary pointer ']"
    }

    
    def start_requests(self):
        init_url = 'https://www.jumbo.com.ar/'
        yield scrapy.Request(url=init_url, callback=self.get_categories)


    def get_categories(self, response):
        script_content = response.xpath("//template[@data-field='extensions']/script").get()
        json_string = script_content.replace("<script>","").replace("</script>","")
        data = json.loads(json_string)
        categories = []

        for element in data['store.home/$after_footer/footer-layout.desktop/footer-oculto']['content']['opciones'][:7]:
            if 'correspondeA' in element.keys():
                if element['correspondeA'] == 'DEPARTAMENTO' or element['correspondeA'] == 'CATEGORIA' or element['correspondeA'] == 'SUBCATEGORIA':
                    categories.append(element['URL'])
                    yield scrapy.Request(url=element['URL'],callback=self.generate_all_category_pages,cb_kwargs=dict(category_url=element['URL']))
                    #print(element['URL'])

        #print("----->" , self.start_urls)
        #for url in self.start_urls:
        #    yield scrapy.Request(url=url,callback=self.get_products)


    def generate_all_category_pages(self,response,category_url):
        pages = response.xpath("//span[@class='discoargentina-search-result-custom-1-x-span-selector-pages']")
        text_html = pages.get()
        #print(text_html)
        if text_html is not None:
            text_re = r'Página <!-- -->(\d+)<!-- --> de <!-- -->(\d+)' if "<!-- -->" in text_html else r'Página (\d+) de (\d+)'
            match = re.search(text_re, text_html)  
            actual_products = int(match.group(1))
            max_products = int(match.group(2))
        else:
            max_products = 0

        if max_products != 0:
            max_products = min(max_products, 50)
            for page_number in range(1,max_products+1):
                new_url = category_url + f"?page={page_number}"
                #print(category_url + f"?page={page_number}")
                #self.start_urls.append(category_url + f"?page={page_number}")
                yield SeleniumRequest(url=new_url,callback=self.get_products)


    def get_products2(self,response):
        driver = response.request.meta["driver"]

        for x in range(0, 10):
            # scroll down by 10000 pixels
            ActionChains(driver) \
                .scroll_by_amount(0, 10000) \
                .perform()
        
        products_element = driver.find_element(By.XPATH,self.xpath["product card"])
        for product in products_element:
            item = scrapy.Item()
            #item["price"] = product.xpath(self.xpath["price"]).get()
            price =  driver.find_element(By.XPATH,self.xpath["price"]).text
            #item["description"] = product.xpath(self.xpath["description"]).text
            description =  driver.find_element(By.XPATH,self.xpath["description"]).text
            #item["brand"] = product.xpath(self.xpath["brand"]).text
            brand =  driver.find_element(By.XPATH,self.xpath["brand"]).text
            #item["market"] = "Jumbo"
            market = "Jumbo"
            #item["image"] = product.xpath(self.xpath["image"]).text
            image =  driver.find_element(By.XPATH,self.xpath["image"]).text

            yield {"price":price,"description":description,"brand":brand,"image":image}

    def get_products(self,response):
        products_element = response.xpath(self.xpath["product card"])
        for product in products_element:
            item = scrapy.Item()
            #item["price"] = product.xpath(self.xpath["price"]).get()
            price = product.xpath(self.xpath["price"]).get()
            #item["description"] = product.xpath(self.xpath["description"]).get()
            description = product.xpath(self.xpath["description"]).get()
            #item["brand"] = product.xpath(self.xpath["brand"]).get()
            brand = product.xpath(self.xpath["brand"]).get()
            #item["market"] = "Jumbo"
            market = "Jumbo"
            #item["image"] = product.xpath(self.xpath["image"]).get()
            image = product.xpath(self.xpath["image"]).get()

            yield {"price":price,"description":description,"brand":brand,"image":image}
'''
    def parse_item(self, response):
        self.logger.info("Hi, this is an item page! %s", response.url)

        item = scrapy.Item()
        item["price"] = response.xpath(self.xpath["price"]).get()
        item["description"] = response.xpath(self.xpath["description"]).get()
        item["brand"] = response.xpath(self.xpath["brand"]).get()
        item["market"] = "Jumbo"
        item["image"] = response.xpath(self.xpath["image"]).get()

        url = response.xpath('//td[@id="additional_data"]/@href').get()
        return response.follow(
            url, self.parse_additional_page, cb_kwargs=dict(item=item)
        )

    def parse_additional_page(self, response, item):
        item["additional_data"] = response.xpath(
            '//p[@id="additional_data"]/text()'
        ).get()
        return item
'''