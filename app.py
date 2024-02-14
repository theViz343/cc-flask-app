from flask import Flask, request
import csv

app = Flask(__name__)

lookup={}

@app.route('/load/"', methods=['GET'])
def load_data():
    with open('lookup.csv', mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            lookup[row[0]] = row[1]
    return lookup

@app.route("/", methods=['POST'])
def process_file():
    f = request.files['inputFile']
    f_name = f.filename.split('.')[0]
    result = "File not found."
    if lookup:
        result = lookup[f_name]
    else:
        load_data()
        result = lookup[f_name]
    return result