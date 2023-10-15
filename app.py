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

def allowed_filesize(filename):
    file_size = round(((os.stat(filename).st_size) / (1024*1024)), 2)
    
    return (file_size <= 5.00)

@app.route('/', methods=['GET'])
def route():
    return  'This is a service by Simple Wallet'

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
        
        # Check file size
        if allowed_filesize(filename) is False:
            return {'status': False, 'message': 'Ukuran gambar terlalu besar! Maks. 5 MB'}, 400
        
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
            return {'status': False, 'message': 'Maaf, gambar ini tidak bisa diproses.'}, 400

        return {'status': True, 'items': json.dumps(result_list)}, 200
    
    return {'status': False, 'message': 'File bukan berupa gambar'}, 400


if __name__ == '__main__':
    app.run()