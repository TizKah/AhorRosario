from flask import Flask, render_template
import csv

app = Flask(__name__)

@app.route('/')
def index():
    # Lee el archivo CSV y obtén los datos de los productos
    products = []
    with open('output_jumbo.csv', 'r', newline='', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            products.append(row)

    return render_template('index.html', products=products)

if __name__ == '__main__':
    app.run(debug=True)