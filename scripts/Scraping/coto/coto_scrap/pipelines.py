# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import sqlite3, os

ACTUAL_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
DATABASE_PATH = os.path.join(ACTUAL_DIRECTORY, '..', '..','..', 'products.db')

class CotoScrapPipeline:

    def __init__(self) -> None:
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.cur = self.conn.cursor()
        self.conn.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT,
            price REAL,
            brand TEXT,
            image TEXT,
            market TEXT
        );
        ''')
        self.conn.commit()

    def process_item(self, item, spider):
        self.conn.execute('''
        INSERT INTO products (description, price, brand, image, market)
        VALUES (?, ?, ?, ?, ?);
        ''', (
            item['description'],
            item['price'],
            item['brand'],
            item['image'],
            item['market']
            ))

        self.conn.commit()

    def close_spider(self, spider):
        # Close cursor & connection to database
        self.cur.close()
        self.conn.close()
