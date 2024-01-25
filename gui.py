import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import time  # Para simular el proceso de scraping

class SupermarketApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Supermarket App")

        # Lista de productos en el carrito
        self.shopping_cart = []

        # Crear widgets
        self.create_widgets()

    def create_widgets(self):
        # Botones
        scrape_button = tk.Button(self.master, text="Scrapear", command=self.scrape_data, width=20, height=2)
        scrape_button.pack(pady=20)

        eval_button = tk.Button(self.master, text="Evaluar Compra", command=self.evaluate_purchase, width=20, height=2)
        eval_button.pack(pady=20)

    def scrape_data(self):
        # Cierra la ventana del carrito si está abierta
        self.close_cart_window()

        # Muestra la interfaz de carga durante el scraping
        loading_window = tk.Toplevel(self.master)
        loading_window.title("Cargando...")
        loading_window.geometry("300x100")

        # Puedes realizar el scraping aquí
        # Simulamos un proceso de scraping que toma 5 segundos
        time.sleep(5)

        # Cierra la interfaz de carga después del scraping
        loading_window.destroy()
        messagebox.showinfo("Scrape Completado", "Los datos han sido actualizados.")

    def evaluate_purchase(self):
        # Cierra la ventana del carrito si está abierta
        self.close_cart_window()

        # Cierra la ventana principal
        self.master.destroy()

        # Ventana para evaluar compra
        evaluate_window = tk.Tk()
        evaluate_window.title("Evaluar Compra")
        evaluate_window.geometry("800x600")

        # Campos de entrada
        tk.Label(evaluate_window, text="Nombre del Producto:").pack(pady=5)
        product_name_entry = tk.Entry(evaluate_window, width=30)
        product_name_entry.pack(pady=5)

        tk.Label(evaluate_window, text="Peso/Cantidad:").pack(pady=5)
        quantity_entry = tk.Entry(evaluate_window, width=30)
        quantity_entry.pack(pady=5)

        tk.Label(evaluate_window, text="Marca:").pack(pady=5)
        brand_entry = tk.Entry(evaluate_window, width=30)
        brand_entry.pack(pady=5)

        # Botón de búsqueda
        search_button = tk.Button(evaluate_window, text="Buscar", command=lambda: self.search_products(evaluate_window, product_name_entry.get(), quantity_entry.get(),brand_entry.get()), width=20, height=2)
        search_button.pack(pady=10)

        # Frame para mostrar las "cards" de productos
        self.cards_frame = tk.Frame(evaluate_window)
        self.cards_frame.pack(pady=10)

        # Treeview para mostrar el carrito
        columns = ("Nombre", "Precio", "Marca", "Peso", "Eliminar")
        self.cart_treeview = ttk.Treeview(evaluate_window, columns=columns, show="headings")

        # Configurar encabezados de columna
        for col in columns:
            self.cart_treeview.heading(col, text=col)

        self.cart_treeview.pack(pady=10)

    def search_products(self, parent_window, product_name, quantity_name,brand_name):
        # Muestra la interfaz de búsqueda
        search_window = tk.Toplevel(parent_window)
        search_window.geometry("600x500")
        search_window.title("Resultados de la Búsqueda")

        # Puedes realizar la búsqueda aquí
        # Simulamos resultados de búsqueda
        products = [
            {"name": "Desodorante", "price": 10.50, "image": "image1.jpg", "marca":"rexona", "peso":"150"},
            {"name": "Desodorante", "price": 8.75, "image": "image2.jpg", "marca":"AXE", "peso":"190"},
            {"name": "Desodorante", "price": 12.00, "image": "image3.jpg", "marca":"rexona", "peso":"150"},
            {"name": "Desodorante", "price": 15.25, "image": "image4.jpg", "marca":"rexona", "peso":"150"},
            {"name": "Desodorante", "price": 9.99, "image": "image5.jpg", "marca":"rexona", "peso":"150"},
            {"name": "Desodorante", "price": 18.75, "image": "image6.jpg", "marca":"rexona", "peso":"150"},
            {"name": "harina", "price": 18.75, "image": "image6.jpg", "marca":"gallo", "peso":"1000g"}
        ]

        # Mostrar resultados de la búsqueda
        row = 0
        col = 0
        for product in products:
            if product_name.lower() in product["name"].lower() and quantity_name in product["peso"] and brand_name.lower() in product["marca"].lower():
                # Crear la "card" del producto
                frame = tk.Frame(search_window, padx=10, pady=10, relief=tk.SUNKEN, borderwidth=2)
                frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

                label_name = tk.Label(frame, text=product["name"], font=("Helvetica", 12, "bold"))
                label_name.pack()

                label_price = tk.Label(frame, text=f"Precio: {product['price']}", font=("Helvetica", 10))
                label_price.pack()

                label_brand = tk.Label(frame, text=f"Marca: {product['marca']}", font=("Helvetica", 10))
                label_brand.pack()

                label_peso = tk.Label(frame, text=f"Peso: {product['peso']}", font=("Helvetica", 10))
                label_peso.pack()

                # Botón para agregar al carrito
                add_button = tk.Button(frame, text="Agregar al Carrito", command=lambda p=product: self.add_to_cart(p, search_window), width=20, height=2)
                add_button.pack(pady=5)

                col += 1
                if col >= 3:  # Cambiar el número a la cantidad deseada de columnas
                    col = 0
                    row += 1

        # Ajustar el tamaño de la ventana
        search_window.update_idletasks()
        width = search_window.winfo_width() + 20  # Agregar un pequeño margen
        height = search_window.winfo_height() + 20
        search_window.geometry(f"{width}x{height}")

        # Cerrar la ventana de búsqueda al agregar al carrito
        tk.Button(search_window, text="Cerrar", command=search_window.destroy, width=20, height=2).grid(row=row + 1, column=0, columnspan=2, pady=10)


    def add_to_cart(self, product, parent_window):
        self.shopping_cart.append(product)
        self.update_cart_window()

        # Cierra la ventana de búsqueda
        parent_window.destroy()

    def update_cart_window(self):
        # Limpiar elementos anteriores del carrito
        self.cart_treeview.delete(*self.cart_treeview.get_children())

        # Mostrar elementos del carrito
        for item in self.shopping_cart:
            self.cart_treeview.insert("", "end", values=(item["name"], item["price"], item["marca"], item["peso"], "Eliminar",), tags=(item["name"],))

            # Agregar etiqueta de evento para el botón "Eliminar"
            self.cart_treeview.tag_bind(item["name"], "<ButtonRelease-1>", lambda event, p=item: self.remove_from_cart(p))

    def remove_from_cart(self, product):
        self.shopping_cart.remove(product)
        self.update_cart_window()

    def close_cart_window(self):
        # Cierra la ventana del carrito si está abierta
        if hasattr(self, 'cart_treeview') and self.cart_treeview.winfo_exists():
            self.cart_treeview.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("500x200")
    app = SupermarketApp(root)
    root.mainloop()
