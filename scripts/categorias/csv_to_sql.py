import sqlite3
import csv
import os

# Ruta donde se encuentran los archivos CSV
csv_folder = os.path.join(os.getcwd(), 'csv')

def create_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT,
            price FLOAT,
            image TEXT,
            brand TEXT,
            market TEXT
        )
    ''')
    conn.commit()

def insert_data(conn, filename):
    file_path = os.path.join(csv_folder, filename)
    with open(file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            # Obtener el valor de brand, si no existe, asignar None
            brand = row.get('brand', None)
            
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO products (description, price, image, brand, market)
                VALUES (?, ?, ?, ?, ?)
            ''', (row['description'], row['price'], row['image'], brand, row['market']))
            conn.commit()

def main():
    conn = sqlite3.connect('products.db')  # Conexión a la base de datos SQLite
    create_table(conn)  # Crear tabla si no existe

    # Cargar datos de los archivos CSV a la base de datos
    insert_data(conn, 'coto.csv')
    insert_data(conn, 'carrefour.csv')
    insert_data(conn, 'jumbo.csv')

    conn.close()

if __name__ == '__main__':
    main()