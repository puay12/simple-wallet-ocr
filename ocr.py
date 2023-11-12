import pytesseract
import cv2
import numpy as np
import re

def image_preprocessing(img_path):
    image = cv2.imread(img_path)

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Scale and pad image
    factor = 1000 / gray.shape[0]
    processed_image = cv2.resize(gray, None, fx=factor, fy=factor)
    processed_image = cv2.copyMakeBorder(processed_image, 10, 10, 10, 10,
                                cv2.BORDER_CONSTANT, value=[255, 255, 255])

    # Apply dilation and erosion to remove some noise
    kernel = np.ones((1, 1), np.uint8)
    processed_image = cv2.dilate(processed_image, kernel, iterations=1)
    processed_image = cv2.erode(processed_image, kernel, iterations=1)
    
    return processed_image


def get_string(processed_image):
    
    return pytesseract.image_to_string(
        processed_image, lang='ind', config='--psm 6 --oem 3 --tessdata-dir /home/forge/ocr-simplewallet-staging.agileteknik.com/tessdata/')


def text_preprocessing(data):
    # Lower the case
    data = data.lower()

    # Remove any leading and trailing whitespaces
    data = data.strip()

    # String Split
    data = data.split("\n")
    
    return data


def get_items(data):
    item_name_list = []
    item_price_list = []
    
    start_index = get_start_index(data)
    end_index = get_end_index(data)

    if((start_index != None) & (end_index != None)):
        item_temp = list(data[start_index:end_index])

        for item in item_temp:
            temps = item.split()

            if len(temps) > 0:
                get_item_price_list(item=item, temps=temps, item_price_list=item_price_list)
                get_item_name_list(item=item, temps=temps, item_name_list=item_name_list)

    return item_name_list, item_price_list

def get_item_price_list(item, temps, item_price_list):
    length = len(temps)
    price = remove_special_chars(temps[(length-1)])
    
    if contain_discount(item) is False:
        if price_separated_possibility(temps):
            if len(temps[(length-2)]) > 3:
                if len(temps[(length-1)]) == 1:
                    item_price_list.append(int(remove_special_chars(temps[(length-2)])))
                else:
                    item_price_list.append(int(price))
            else:
                item_price_list.append(int(concat_text(get_separated_price(temps)).replace(' ', '')))
        else:
            if (price.isnumeric()) & (len(price) != 2):
                if 'x' not in temps:
                    item_price_list.append(int(price))
    else:
        item_price_length = len(item_price_list)
        
        if price_separated_possibility(temps):
            disc_price = int(remove_special_chars(concat_text(get_separated_price(temps)).replace(' ', '')))
        else:
            disc_price = int(remove_special_chars(temps[(length-1)]))

        item_price_list[(item_price_length-1)] = item_price_list[(item_price_length-1)] - disc_price 
    
    return

def get_item_name_list(item, temps, item_name_list):
    container = []
    
    collect_separated_item_names(container, item, temps)

    if len(container) > 1:
        item_name_list.append(concat_text(container))
    elif len(container) == 1:
        if any_digit(item) is False:
            prev_item_name = item_name_list[len(item_name_list)-1]
            item_name_list[len(item_name_list)-1] = concat_text([prev_item_name, container[0]])
        else:
            item_name_list.append(container[0])

    return

def collect_separated_item_names(container, item, temps):
    for temp in temps:
        if temp.isalnum():
            if temp.isnumeric():
                continue
            else:
                if contain_discount(item) is False:
                    if (temp != 'x'):
                        container.append(temp)
    return

def get_start_index(data):
    start_index = None

    for index, text in enumerate(data):
        temp = text.split()

        if len(temp) > 0:
            if ('npwp' not in text) & (('jalan' not in text) & ('jln' not in text)):
                if does_price_exist(temp):
                    start_index = index
                    break
        else:
            continue

    return start_index

def get_end_index(data):
    end_index = None

    for index, text in enumerate(data):
        if ('solaria' in data) | ('\'olaria' in data):
            if ('items' in text) | ('ems' in text):
                end_index = index
                break
        else:
            if ('harga jual' in text) | ('total' in text) | ('otal' in text) | ('tom' in text):
                if any_digit(text):
                    end_index = index
                    break

    return end_index

def does_price_exist(data):
    length = len(data)
    price = data[(length-1)]

    if (contain_dot_comma(price)) & (len(price) < 11) & (contain_discount(data) is False) & (any_digit(price)):
        if (any_digit(data[(length-2)])) | (data[(length-2)].isalnum()):
            return True
    else:
        if (price.isnumeric()) & (len(price) == 3) & (any_digit(data[(length-2)])):
            return True
        elif is_former_index_price(data):
            return True
        else:
            return False

def is_former_index_price(text):
    length = len(text)
    former_index = text[(length-2)]

    return (any_digit(former_index)) & (contain_dot_comma(former_index) & (len(remove_special_chars(former_index)) < 11) & (len(remove_special_chars(former_index)) > 3))

def price_separated_possibility(text):
    length = len(text)

    return (contain_dot_comma(text[(length-2)])) & (any_digit(text[(length-2)]))

def get_separated_price(price):
    length = len(price)

    return [remove_special_chars(price[(length-2)]), price[(length-1)]]

def concat_text(data):
    return ' '.join(data)

def remove_special_chars(text):
    result = re.sub('[^A-Za-z0-9]+', '', text)
    
    if (bool(re.match('[a-zA-Z\s]', result))) & ((len(re.findall('[0-9]', result)) > 2) | (len(re.findall('[0-9]', result)) == 1)):
        result = re.sub('[a-zA-Z\s]', '', result)
    
    return result

def contain_dot_comma(text):
    return (',' in text) | ('.' in text)

def contain_discount(text):
    return ('diskon' in text) | ('disc' in text) | ('hemat' in text) | ('pot.' in text)

def any_digit(text):
    return any(map(str.isdigit, text))
