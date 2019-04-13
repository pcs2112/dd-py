import os
import shutil
import re
from src.utils import get_db_connection
from src.config import get_config

app_config = get_config()

profile_db = get_db_connection('profile')
core_db = get_db_connection('core')

out_dir = app_config['OUT_DIR']
in_dir = app_config['IN_DIR']
cdn_base_path = app_config['CDN_BASE_PATH']


def get_all_master_products(product_ids=''):
    """
    :return: Returns the list of all master products
    """
    query = (
        "SELECT "
        "   `productID`, `productCode`, `productIntegrationID`, `productName` "
        "FROM "
        "   `product` "
        "WHERE "
        "   `productParentID` = 0"
    )
    
    if product_ids:
        query = f'{query} AND `productID` IN ({product_ids})'
    
    cursor = profile_db.cursor()
    cursor.execute(query)
    
    return cursor.fetchall()


def get_product_colors(product_id):
    """
    :param int product_id: Product master ID
    :return: Returns a list of product colors
    """
    query = (
        "SELECT "
        "   `colourID`, `colourDesc` "
        "FROM "
        "   `product` AS `p` "
        "INNER JOIN `product-colour` AS `pc` ON `p`.`productColourID` = `pc`.`colourID` "
        "WHERE "
        "   `productParentID` = %s"
    )

    cursor = profile_db.cursor()
    cursor.execute(query, (product_id,))

    return cursor.fetchall()


def get_product_color_images(product_id):
    """
    :param int product_id: Product master ID
    :return: Returns a list of product colors images
    """
    query = (
        "SELECT "
        "   `productImageID`, `colourID`, `productImageFileOriginalHTTPLocation`, "
        "   `productImageFileMediumHTTPLocation`, `productImageFileThumbnailHTTPLocation` "
        "FROM "
        "   `product-image` "
        "WHERE"
        "   `productID` = %s"
    )
    
    cursor = core_db.cursor()
    cursor.execute(query, (product_id,))
    
    return cursor.fetchall()
    
    
def build_product_images(product_ids=''):
    masters = get_all_master_products(product_ids)
    
    for product in masters:
        product_id = product[0]
        product_code = product[1]
        product_name = product[3]
        
        out_dir_product_code = product_code.replace('/', '-')
        out_file_product_code = product_code.lower().replace('/', '')
        
        print(f'Processing product id={product_id} code={product_code} name={product_name}')
       
        colors = get_product_colors(product_id)
        colors_images = get_product_color_images(product_id)
        colors_map = {}
        
        for color in colors:
            color_id = color[0]
            colors_map[color_id] = {
                'color_id': color_id,
                'color_name': color[1],
                'images': []
            }
        
        for color_image in colors_images:
            color_id = color_image[1]
            if color_id in colors_map:
                colors_map[color_id]['images'].append(color_image)
        
        try:
            out_product_dir = os.path.join(out_dir, out_dir_product_code)
            
            try:
                shutil.rmtree(out_product_dir)
            except FileNotFoundError:
                pass
                
            os.mkdir(out_product_dir)

            for color_id, color in colors_map.items():
                for color_image in color['images']:
                    color_image_id = color_image[0]
                    
                    # Iterate over the image path fields in the product-image data
                    for i in range(2, 4):
                        existing_path = color_image[i]
                        if existing_path:
                            existing_path = os.path.join(in_dir, existing_path.replace(cdn_base_path, '').lstrip('/'))
                            exists = os.path.isfile(existing_path)
                            if exists:
                                filename = os.path.basename(existing_path).replace(f'{out_file_product_code}_', '')
                                new_filename = re.sub('[^0-9a-zA-Z]+', '-', color['color_name'].lower())
                                new_filename = os.path.join(out_product_dir, f'{new_filename}_{color_id}_{color_image_id}_{filename}')
                                shutil.copyfile(existing_path, new_filename)
        except OSError as e:
            print("Creation of the directory %s failed" % out_product_dir)
            raise e
