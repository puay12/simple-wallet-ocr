from flask import Flask, request
from werkzeug.utils import secure_filename
import os
import ocr
import json
import sys

app = Flask(__name__, static_url_path='/images')
UPLOAD_FOLDER = 'images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return ('.' in filename) and (filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS)

@app.route('/', methods=['GET'])
def hello():
    return 'Hello World!'

@app.route('/api/v1/simplewallet/user/getReceiptItems', methods=['POST'])
def receipt():
    if 'file' not in request.files:
        return {'status': False, 'message': 'FILE_NOT_FOUND'}, 400

    file = request.files['image']
    
    if file.filename == '':
        return {'status': False, 'message': 'FILE_NOT_FOUND'}, 400
    
    if file and allowed_file(file.filename):
        # Save File
        filename = secure_filename(file.filename)
        # Save File to /images
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        data = ocr.get_string(filepath)
        data = ocr.text_preprocessing(data)
        item_name_list, item_price_list = ocr.get_items(data)

        result_list = []

        if((item_name_list!=[]) & (item_price_list!=[])):
            if len(item_name_list) == len(item_price_list):
                for i in range(len(item_name_list)):
                    result_list.append({
                        'name': item_name_list[i],
                        'price': item_price_list[i]
                    })

        if result_list == []:
            return {'status': False, 'message': 'Maaf, Gambar ini Tidak Bisa Diproses.'}, 400

        return {'status': True, 'items': json.dumps(result_list)}, 200
    
    return {'status': False, 'message': 'File Hanya Boleh Berupa Gambar'}, 400


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)