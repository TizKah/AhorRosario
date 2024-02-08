import re

# Definir las unidades de medida
unidades_medida = [
    # Largo/Ancho
    "cm", "m", "dm", "mm",
    
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