from flask import Flask, render_template
import csv

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/jumbo')
def jumbo():
    # Lee el archivo CSV y obtén los datos de los productos
    products = []
    with open('jumbo.csv', 'r', newline='', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            products.append(row)

    return render_template('jumbo.html', products=products)

@app.route('/coto')
def coto():
    # Lee el archivo CSV y obtén los datos de los productos
    products = []
    with open('coto.csv', 'r', newline='', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            products.append(row)

    return render_template('coto.html', products=products)


if __name__ == '__main__':
    app.run(host='192.168.0.12',port=5000)