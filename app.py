from flask import Flask, request
import pandas as pd
import os

app = Flask(__name__)
image_lookup_dictionary = {}
csv_file_path = 'Face_Dataset.csv'

def load_image_data_to_dictionary():
    global image_lookup_dictionary
    image_data = pd.read_csv(csv_file_path)
    image_lookup_dictionary = dict(zip(image_data['Image'], image_data['Results']))

load_image_data_to_dictionary()

@app.route('/', methods=['POST'])
def image_recognition():
    if 'inputFile' not in request.files:
        return 'No file part', 400
    
    uploaded_image = request.files['inputFile']
    image_name = uploaded_image.filename
    image_base_name = os.path.splitext(image_name)[0]

    if image_base_name in image_lookup_dictionary:
        prediction = image_lookup_dictionary[image_base_name]
        return f"{image_name}:{prediction}", 200
    else:
        return f"{image_name}:Unknown", 404
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80,threaded=True)