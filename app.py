from flask import Flask, request
import csv

app = Flask(__name__)

@app.route("/", methods=['POST'])
def process_file():
    f = request.files['inputFile']
    f_name = f.filename.split('.')[0]
    result = "File not found."
    with open('lookup.csv', mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == f_name:
                result = f"{row[0]}:{row[1]}"
    return result