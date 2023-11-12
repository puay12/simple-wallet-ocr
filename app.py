from flask import Flask, request, flash
from werkzeug.utils import secure_filename
import os
import ocr
import json

app = Flask(__name__, static_url_path='/images')
UPLOAD_FOLDER = 'images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return ('.' in filename) and (filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS)

def allowed_filesize(filename):
    file_size = round(((os.path.getsize(filename)) / (1024*1024)), 2)

    return (file_size <= 5.00)

def save_file(file):
    # Save File
    filename = secure_filename(file.filename)
    
    # Save File to /images
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    return filepath

def delete_file(filepath):
    # delete file from /images
    if os.path.isfile(filepath):
        os.remove(filepath)

@app.route('/', methods=['GET'])
def route():
    return  {'status': True, 'message': 'This is a OCR service by Simple Wallet'}, 200

@app.route('/api/v1/simplewallet/user/scan-ocr', methods=['POST'])
def receipt():
    # Check if file exists in request
    if 'image' not in request.files:
        return {'status': False, 'message': 'FILE_NOT_FOUND'}, 400

    file = request.files['image']

    if file.filename == '':
        return {'status': False, 'message': 'FILE_NOT_FOUND'}, 400

    if file and allowed_file(file.filename):
        # Save File
        filepath = save_file(file)
        
        # Check file size
        if allowed_filesize(filepath) is False:
            delete_file(filepath)

            return {'status': False, 'message': 'Ukuran gambar terlalu besar! Maks. 5 MB'}, 400

        processed_img = ocr.image_preprocessing(filepath)
        data = ocr.get_string(processed_img)
        print(data)
        data = ocr.text_preprocessing(data)
        item_name_list, item_price_list = ocr.get_items(data)

        # delete file from /images
        delete_file(filepath)

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

        return {'status': True, 'items': result_list}, 200

    return {'status': False, 'message': 'File bukan berupa gambar'}, 400


if __name__ == '__main__':
    app.run()
