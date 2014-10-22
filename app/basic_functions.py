import os

from math import ceil
from translit import transliterate
from wand.image import Image
from werkzeug import secure_filename

from app import app

image_dir = os.path.join(app.root_path, app.config['ITEM_IMAGE_FOLDER'])

def get_small_image_name(file_name):
    return '_small.'.join(file_name.split('.'))

def image_resize(imgsvpth, width=250, height=250):
    img = Image(filename = imgsvpth)
    aspect_ratio = 1.0 * img.height / img.width
    height = int(ceil(height * aspect_ratio))

    img.resize(width, height)
    return img    

def image_uniq_name(name):
    images_list = os.listdir(image_dir)
    
    if name not in images_list:
        return name

    name_counter = 1
    name_parts = name.split('.')
    new_name = name

    while new_name in images_list:
        new_name = "{}_{}.{}".format(
            name_parts[0],
            str(name_counter),
            name_parts[1])
        name_counter += 1

    return new_name

def jewel_uniq_name(name):
    """Creates uniq name_en for handicraft:
    transliterates name and if such name_en exists in database
    adds underline and first free number
    """
    name_en = transliterate(name)
    cnt = Jewel.query.filter(Jewel.name_en==name_en).count()
    if cnt > 0:
        i = 0
        while cnt > 0:
            i += 1
            cnt = Jewel.query.filter(Jewel.name_en=='{}_{}'.format(
                name_en, i)).count()
        rzlt = '{}_{}'.format(name_en, i)
    else:
        rzlt = name_en
    return rzlt    

def save_image(file_image):
    file_name = secure_filename('.'.join(map(
        transliterate, 
        file_image.filename.split('.')
        )))

    file_name = image_uniq_name(file_name)
    
    imgsvpth = os.path.join(image_dir, file_name)
    file_image.save(imgsvpth)
    
    small_img = image_resize(imgsvpth)
    small_file_name = get_small_image_name(file_name)
    small_img.save(filename=os.path.join(image_dir, small_file_name))
    
    return file_name