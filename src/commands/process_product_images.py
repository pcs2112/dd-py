import os
import shutil
import re
from urllib.request import urlretrieve
from urllib.error import HTTPError
from src.db import get_db_connection
from src.config import get_config

app_config = get_config()

profile_db = get_db_connection('profile')
core_db = get_db_connection('core')

products_out_dir = f"{app_config['OUT_DIR']}/products"
products_in_dir = f"{app_config['IN_DIR']}/products"
cdn_base_url = app_config['CDN_BASE_URL']
log_filename = f"{app_config['OUT_DIR']}/build_product_images.log"


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
    result = cursor.fetchall()
    cursor.close()

    return result


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
        "   `productParentID` = %s "
        "GROUP BY `pc`.`colourID`"
    )

    cursor = profile_db.cursor()
    cursor.execute(query, (product_id,))
    result = cursor.fetchall()
    cursor.close()

    return result


def get_product_color_images(product_id):
    """
    :param int product_id: Product master ID
    :return: Returns a list of product colors images
    """
    query = (
        "SELECT "
        "   `productImageID`, `colourID`, `productImageFileOriginalHTTPLocation`, "
        "   `productImageFileMediumHTTPLocation`, `productImageFileThumbnailHTTPLocation`, `productImageIsDefault` "
        "FROM "
        "   `product-image` "
        "WHERE"
        "   `productID` = %s "
        "ORDER BY"
        "   `productImageSortOrder` ASC"
    )

    cursor = core_db.cursor()
    cursor.execute(query, (product_id,))
    result = cursor.fetchall()
    cursor.close()

    return result


def download_product_images(product_ids=''):
    # Remove the existing in dir
    # try:
    #     shutil.rmtree(products_in_dir)
    #     print(f'Emptied {products_in_dir}')
    # except FileNotFoundError:
    #     pass

    # Create the in dir
    # os.mkdir(products_in_dir)

    masters = get_all_master_products(product_ids)

    for product in masters:
        product_id = product[0]
        product_code = product[1]
        product_name = product[3]
        product_code_filename = product_code.replace('/', '-')

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

        # Product directory name
        in_product_dir = os.path.join(products_in_dir, product_code_filename)

        # Remove the product directory
        # try:
        #     shutil.rmtree(in_product_dir)
        # except FileNotFoundError:
        #     pass

        product_dir_created = False
        if os.path.isdir(in_product_dir):
            product_dir_created = True
        else:
            try:
                # Create the product directory
                os.mkdir(in_product_dir)
                product_dir_created = True
            except OSError:
                print("Creation of the directory %s failed" % in_product_dir)
                pass

        if product_dir_created:
            for color_id, color in colors_map.items():
                for color_image in color['images']:
                    for i in range(2, 4):
                        if color_image[i]:
                            normalized_img_url = color_image[i].replace(cdn_base_url, '').lstrip('/')
                            normalized_img_url = f"http:{cdn_base_url}/{normalized_img_url}"
                            filename = os.path.basename(normalized_img_url)
                            filename = f'{in_product_dir}/{filename}'

                            # Download image if it doesn't exist
                            if not os.path.isfile(filename):
                                try:
                                    urlretrieve(normalized_img_url, filename)
                                except HTTPError:
                                    continue


def build_product_images(product_ids=''):
    # Remove the existing out dir
    try:
        shutil.rmtree(products_out_dir)
        print(f'Emptied {products_out_dir}')
    except FileNotFoundError:
        pass

    # Create the out dir
    os.mkdir(products_out_dir)

    # Stores all the processing info
    logs = []

    masters = get_all_master_products(product_ids)

    for product in masters:
        product_id = product[0]
        product_code = product[1]
        product_name = product[3]
        product_code_filename = product_code.replace('/', '-')

        print(f'Processing product id={product_id} code={product_code} name={product_name}')

        colors = get_product_colors(product_id)
        colors_images = get_product_color_images(product_id)
        colors_map = {}

        for color in colors:
            color_id = color[0]
            colors_map[color_id] = {
                'color_id': color_id,
                'color_name': color[1],
                'images': [],
                'default_image_idx': 0
            }

        for color_image in colors_images:
            color_id = color_image[1]

            if color_id in colors_map:
                colors_map[color_id]['images'].append(color_image)
                if color_image[5] == 'yes':
                    colors_map[color_id]['default_image_idx'] = len(colors_map[color_id]['images']) - 1

        # Product directory name
        out_product_dir = os.path.join(products_out_dir, product_code_filename)

        # Remove the product directory
        try:
            shutil.rmtree(out_product_dir)
        except FileNotFoundError:
            pass

        product_dir_created = False
        try:
            # Create the product directory
            os.mkdir(out_product_dir)
            product_dir_created = True
        except OSError:
            print("Creation of the directory %s failed" % out_product_dir)
            pass

        if product_dir_created:
            images_processed = []

            # Iterate over each product color
            for color_id, color in colors_map.items():
                # Iterate over each product color image
                for idx, color_image in enumerate(color['images']):
                    color_image_id = color_image[0]
                    color_is_default = True if color['default_image_idx'] == idx else False

                    # Iterate over the image path fields in the product-image data
                    for i in range(2, 4):
                        if color_image[i]:
                            # Get the path for the color image
                            existing_path = os.path.join(
                                products_in_dir, color_image[i].replace(cdn_base_url, '').lstrip('/')
                            )
                            if os.path.isfile(existing_path):
                                # Get the existing file name from the path
                                existing_filename = os.path.basename(existing_path)

                                # Remove the product code reference from the existing file name
                                existing_filename = existing_filename.replace(
                                    f"{product_code.lower().replace('/', '')}_", ''
                                )

                                # Create the new file name
                                new_filename = re.sub('[^0-9a-zA-Z]+', '-', color['color_name'].lower())
                                new_filename = os.path.join(
                                    out_product_dir,
                                    f'{new_filename}_{color_id}_{color_image_id}_{existing_filename}'
                                )

                                # Copy the existing file into the new file
                                shutil.copyfile(existing_path, new_filename)

                                # Log image created
                                images_processed.append(new_filename)

                                # Create the default and hover image
                                if color_is_default and i == 3:
                                    ext = existing_filename.split(".")[-1]

                                    # Create the default image
                                    new_default_filename = os.path.join(
                                        out_product_dir,
                                        f'{product_code_filename}_default.{ext}'
                                    )

                                    shutil.copyfile(existing_path, new_default_filename)

                                    # Log image created
                                    images_processed.append(new_default_filename)

                                    # Create the hover image
                                    new_hover_filename = os.path.join(
                                        out_product_dir,
                                        f'{product_code_filename}_hover.{ext}'
                                    )

                                    shutil.copyfile(existing_path, new_hover_filename)

                                    # Log image created
                                    images_processed.append(new_hover_filename)

            # Generate product log
            images_processed_ct = len(images_processed)
            logs.append(
                f'product id={product_id} code={product_code} name={product_name} '
                f'images_count={images_processed_ct}\n'
            )

            if images_processed_ct > 0:
                for image_processed in images_processed:
                    logs.append(f"\t{image_processed.replace(app_config['OUT_DIR'], '')}\n")

                logs.append('\n')

    log_fh = open(log_filename, 'w')
    log_fh.writelines(logs)
    log_fh.close()
