# Usamos el CSV de Jumbo, dado que ya nos viene facilitada una columna de marcas scrapeada
# directamente desde la página, para luego utilizarlo para ordenar datos en otros scrapeos desordenados (sin marca)

import pandas as pd
import os, re, csv, sqlite3, argparse

ACTUAL_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
file_name = 'Coto 15-1.csv'

def get_brands():
    csv_file = 'output_jumbo.csv'
    df = pd.read_csv(csv_file)
    posibles_brands = set(df['brand'].unique())

    print(f"{len(posibles_brands)} marcas obtenidas con éxito.")
    return posibles_brands


def brand_giver(description, posibles_brands):
    words = [word.lower() for word in str(description).split()]

    # Buscar marcas completas
    for brand in posibles_brands:
        if str(brand).lower() in words:
            return brand
    return None

def main_brand_giver():
    posibles_brands = get_brands()

    # Leer el CSV
    df = pd.read_csv(file_name)

    # Aplicar la función a cada fila del DataFrame
    df["brand"] = df["description"].apply(lambda x: brand_giver(x, posibles_brands)).apply(pd.Series)


    # Obtener el total de productos
    total_productos = len(df)
    productos_con_medida = df[df["brand"].notnull()]
    porcentaje_con_medida = (len(productos_con_medida) / total_productos) * 100
    print(f"Porcentaje de productos que obtuvieron una marca: {porcentaje_con_medida:.2f}%")

    # Guardar el DataFrame modificado en un nuevo CSV
    df.to_csv('br_' + file_name, index=False)




def create_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT,
            price FLOAT,
            brand TEXT,
            market TEXT
        )
    ''')
    conn.commit()

def insert_data(conn, filename):
    with open(f"{ACTUAL_DIRECTORY}/{filename}", 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            # Obtener el valor de brand, si no existe, asignar None
            brand = row.get('brand', None)
            
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO products (description, price, brand, market)
                VALUES (?, ?, ?, ?)
            ''', (row['description'], row['price'], brand, row['supermercado']))
            conn.commit()

def main_csv_to_sql():
    conn = sqlite3.connect(f'{ACTUAL_DIRECTORY}/{file_name.split('.')[0]}.db')  # Conexión a la base de datos SQLite
    create_table(conn)  # Crear tabla si no existe

    # Cargar datos de los archivos CSV a la base de datos
    insert_data(conn, file_name)
    #insert_data(conn, 'carrefour.csv')
    #insert_data(conn, 'jumbo.csv')

    conn.close()


# Definir las unidades de medida
unidades_medida = [
    # Largo/Ancho
    #"cm", "m", "dm", "mm",
    
    # Líquido
    "l", "ml", "cc", "lt",
    
    # Pesos
    "kg", "kilos","kilo", "g", "gr",

    # Cantidades
    #"unidades", "u"
]

# Mapeo de conversiones de unidades
conversiones_unidades = {
    "lt": "l",
    # Agrega más conversiones según sea necesario
}
# Función para extraer cantidad y unidad de medida con expresiones regulares
def extraer_cantidad_y_unidad(description):
    # Patrón de búsqueda para cantidad y unidad
    patron = re.compile(r'(\d+(?:,\d*)?(?:\.\d*)?)\s*([a-zA-Z]+|$)')
    # Buscar todas las coincidencias en la descripción
    coincidencias = patron.findall(description)
    
    # Inicializar cantidad y unidad
    cantidad = None
    unidad = None
    
    if coincidencias:
        for match in coincidencias:
            num_str, possible_unidad = match
            # Reemplazar comas por puntos y convertir a float
            num_str = num_str.replace(',', '.')
            # Verificar si la posible unidad está en la lista de unidades permitidas
            if possible_unidad.lower() in unidades_medida:
                cantidad = float(num_str)
                unidad = possible_unidad.lower()
                # Normalizar la unidad si es necesario
                if unidad in conversiones_unidades:
                    unidad = conversiones_unidades[unidad]
                break
    
    # Buscar medidas con "X" y agregarlas a la descripción
    patron_medida_x = re.compile(r'(\d+)\s*[xX]\s*(\d+)\s*([a-zA-Z]+|$)')
    coincidencia_x = patron_medida_x.search(description)
    if coincidencia_x:
        medidas_x = coincidencia_x.groups()
        cantidad = f"{float(medidas_x[0])} x {float(medidas_x[1])}"
        unidad = medidas_x[2].lower() if medidas_x[2].lower() in unidades_medida else None

    return cantidad, unidad

# Función para eliminar la cantidad y la unidad de la descripción correctamente
def limpiar_descripcion(description):
    numXnum_re = r'(\d+)\s*[xX]\s*(\d+)\s*([a-zA-Z]+|$)'
    # Patrón de búsqueda para medidas con "X"
    patron_medida_x = re.compile(numXnum_re)
    # Eliminar la cantidad y la unidad de la descripción
    cleaned_description = re.sub(r'(\d+(?:,\d*)?(?:\.\d*)?)\s*([a-zA-Z]+|$)', '', description).strip()

    # Buscar medidas con "X" y agregarlas a la descripción limpiada
    coincidencia_x = patron_medida_x.search(description)
    if coincidencia_x:
        cleaned_description = re.sub(numXnum_re, '', description).strip()

    return cleaned_description.strip()


def main_unity_parser():

    # Leer el CSV
    file_name = 'archivo.csv'
    df = pd.read_csv(file_name)

    # Aplicar la función a cada fila del DataFrame
    df[["quantity", "unit"]] = df["description"].apply(extraer_cantidad_y_unidad).apply(pd.Series)

    # Eliminar la cantidad y la unidad de la columna "description" correctamente
    df["description"] = df["description"].apply(limpiar_descripcion)

    # Obtener el total de productos
    total_productos = len(df)
    productos_con_medida = df[df["quantity"].notnull()]
    porcentaje_con_medida = (len(productos_con_medida) / total_productos) * 100
    print(f"Porcentaje de productos con medida: {porcentaje_con_medida:.2f}%")

    # Guardar el DataFrame modificado en un nuevo CSV
    df.to_csv(f"{file_name.split('.')[0]}_unity_parsed.csv", index=False)



def main(brand_giver,csv_to_sql,unity_parser):
    if brand_giver:
        main_brand_giver()
    if csv_to_sql:
        main_csv_to_sql()
    if unity_parser:
        main_unity_parser()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ejecutar partes específicas del programa.')
    parser.add_argument('--brand_giver', action='store_true', help='Ejecutar la parte de brand_giver.')
    parser.add_argument('--csv_to_sql', action='store_true', help='Ejecutar la parte de csv_to_sql.')
    parser.add_argument('--unity_parser', action='store_true', help='Ejecutar la parte de unity_parser.')

    args = parser.parse_args()

    main(args.brand_giver, args.csv_to_sql, args.unity_parser)