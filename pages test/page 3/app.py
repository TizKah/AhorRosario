from flask import Flask, render_template, jsonify
import sqlite3

app = Flask(__name__)

def query_database(query):
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    return result

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/busqueda')
def search():
    return render_template('busqueda.html')

@app.route('/get_products')
def get_products():
    query = 'SELECT * FROM products'
    results = query_database(query)
    products = [{'description': row[1], 'price': row[2], 'image': row[3], 'brand': row[4], 'market': row[5]} for row in results]
    return jsonify(products)

if __name__ == '__main__':
    app.run(debug=True)
