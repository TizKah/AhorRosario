# Usamos el CSV de Jumbo, dado que ya nos viene facilitada una columna de marcas scrapeada
# directamente desde la página, para luego utilizarlo para ordenar datos en otros scrapeos desordenados (sin marca)

import pandas as pd
file_name = 'coto.csv'

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