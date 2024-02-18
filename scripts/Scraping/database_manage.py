
import pytz, datetime, sqlite3, os
from unity_parser import limpiar_descripcion, extraer_cantidad_y_unidad


ACTUAL_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

def get_date():
    tz_argentina = pytz.timezone('America/Argentina/Buenos_Aires')
    return datetime.datetime.now(tz_argentina)

# Inserta datos en la tabla
def insert_into_db(products, categories_names, page_url):
    e = 'database is locked'
    while e == 'database is locked' or e == 'brand':
        conn = sqlite3.connect(f'{ACTUAL_DIRECTORY}/products.db', timeout=10)
        try:
            conn.execute('''
            CREATE TABLE IF NOT EXISTS products (
                local_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT,
                price REAL,
                brand TEXT,
                image TEXT,
                market TEXT,
                quantity INTEGER,
                unity TEXT,
                date DATATIME,
                category TEXT,
                subcategory TEXT,
                page_url TEXT
            );
            ''')
            for product in products:
                product['quantity'], product['unity'] = extraer_cantidad_y_unidad(product['description'])
                product['description'] = limpiar_descripcion(product['description'])
                conn.execute('''
                INSERT INTO products (description, price, brand, image, market, quantity, unity, date, category, subcategory, page_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                ''', (product['description'], product['price'], product['brand'], product['image'], product['market'],
                    product['quantity'],product['unity'], get_date(),categories_names['category'],categories_names['subcategory'], page_url))

            conn.commit()
            e = 'done!'
            
        except Exception as e:
            with open(f"{ACTUAL_DIRECTORY}/log.txt", "a+") as f:
                f.write(f""" -- Error en base de datos --\n 
                        Categoría: {categories_names['category']}\n
                        Subcategoría: {categories_names['subcategory']}\n
                        Error: {e}\n""")
            if e == 'brand':
                product['brand'] = 'Error'
        
        conn.close()