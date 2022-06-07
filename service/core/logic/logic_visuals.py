import warnings
import io
import pandas as pd
import numpy as np
import openpyxl
from datetime import datetime
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from fastapi.templating import Jinja2Templates

from service.core.logic.logic_system import conn_django, conn_public, sftp_sender, generate_top_nav_from_username, \
    conn_hana

import requests
import json
import os
import cv2
import urllib
from PIL import ImageFont, ImageDraw, Image

warnings.filterwarnings("ignore")

templates = Jinja2Templates(directory="resources/templates/visuals")


async def get_resizes_from_template_id(template_id):
    """
    Function gets available resizes for a certain template
    """

    resizes = {
        "basic": ['1080x1080', '1350x1080', '1920x1080'],
        "2_events": ['1080x1080', '1350x1080', '1920x1080']
    }

    return resizes[template_id]


async def get_html_form_template(template_id):
    resizes = await get_resizes_from_template_id(template_id)

    resize_selector = """
            <div class="input-container">
            <label for="resize">Выберите размер:</label>
            <select class="select" name="resize" id="resize">
                <option value="no" selected="selected">click me</option>
    """
    for resize in resizes:
        resize_selector += f'<option value="{resize}">{resize}</option>'

    resize_selector += """
            </select>
        </div>
        """

    templates = {
        "basic": """
        <div class="text-container">
            <p>Введите SKU и нажмите "Получить Данные".</p>
            <p>Скрипт подтянет название, цены и бренд.</p>
            <p>Название нужно будет разделить на Наименование и Описание.</p>
            <p>
            </p>
            <p>Заполнить остальные поля согласно инструкции и Сгенерировать.</p>
    
            <p>Для рассрочки стоит использовать точку вместо тире:</p>
            <p>
            </p>
            <p>РАССРОЧКА</p>
            <p>0·0·24</p>
    
            <p>Справочная схема:</p>
            <img src="https://www.technodom.kz/under/feed/tddmdui/resources/example_visuals.png">
        </div>
        <div class="input-container">
            <label for="resize">Выберите регион:</label>
            <select class="select" name="locale" id="locale">
                <option value="no" selected="selected">click me</option>
                <option value="KZ">Казахстан</option>
                <option value="KG">Киргизия</option>
            </select>
        </div>
        
        resize_selector
    
        
        <div class="input-container">
          <label for="sku" class="url-operator__label form-label">1. SKU:</label>
          <input class="form-input" type="text" id="sku" name="sku" required="">
        </div>
        
        <div class="input-container">
          <label for="title" class="url-operator__label form-label">2. Название:</label>
          <textarea class="url-operator__input form-input" type="text" id="title" onkeydown="this.style.width = ((this.value.length + 1) * 8) + 'px';" name="title" required=""></textarea>
        </div>
        <div class="input-container">
          <label for="title_bottom" class="url-operator__label form-label">2.1 Нижняя часть названия:</label>
          <textarea class="url-operator__input form-input" type="text" id="title_bottom" onkeydown="this.style.width = ((this.value.length + 1) * 8) + 'px';" name="title_bottom" required=""></textarea>
        </div>
        <div class="input-container">
          <label for="description" class="url-operator__label form-label">3. Описание:</label>
          <textarea class="url-operator__input form-input" type="text" id="description" onkeydown="this.style.width = ((this.value.length + 1) * 8) + 'px';" name="description" required=""></textarea>
        </div>
        <div class="input-container">
          <label for="description_bottom" class="url-operator__label form-label">3.1 Нижняя часть описания:</label>
          <textarea class="url-operator__input form-input" type="text" id="description_bottom" onkeydown="this.style.width = ((this.value.length + 1) * 8) + 'px';" name="description_bottom" required=""></textarea>
        </div>        
        <div class="input-container">
          <label for="price_old" class="url-operator__label form-label">4. Цена старая:</label>
          <input class="form-input" type="text" id="price_old" name="price_old" required="">
        </div>
        <div class="input-container">
          <label for="price_current" class="url-operator__label form-label">5. Цена текущая:</label>
          <input class="form-input" type="text" id="price_current" name="price_current" required="">
        </div>
        <div class="input-container">
          <label for="vendor" class="url-operator__label form-label">6. Бренд:</label>
          <input class="form-input" type="text" id="vendor" name="vendor" required="">
        </div>     
        
        <div class="input-container">
          <label for="event_name" class="url-operator__label form-label">7. Название события на плашке:</label>
          <input class="form-input" type="text" id="event_name" name="event_name" required="">
        </div>   
        <div class="input-container">
          <label for="event_value" class="url-operator__label form-label">8. Значение события на плашке:</label>
          <input class="form-input" type="text" id="event_value" name="event_value" required="">
        </div>                      
                                        
        <button class="form-input submit-btn" type="button" onclick="getDataSKU(form_target)" form="form_target" value="Получить Данные о Товаре">
          Получить Данные
        </button>
        <button class="form-input submit-btn" type="button" onclick="generate(form_target)" form="form_target" value="Сгенерировать">
          Сгенерировать
        </button>
        """,
        "2_events": """
            <div class="text-container">
                <p>Введите SKU и нажмите "Получить Данные".</p>
                <p>Скрипт подтянет название, цены и бренд.</p>
                <p>Название нужно будет разделить на Наименование и Описание.</p>
                <p>
                </p>
                <p>Заполнить остальные поля согласно инструкции и Сгенерировать.</p>

                <p>Для рассрочки стоит использовать точку вместо тире:</p>
                <p>
                </p>
                <p>РАССРОЧКА</p>
                <p>0·0·24</p>

                <p>Справочная схема:</p>
                <img src="https://www.technodom.kz/under/feed/tddmdui/resources/example_visuals.png">
            </div>
            <div class="input-container">
                <label for="resize">Выберите регион:</label>
                <select class="select" name="locale" id="locale">
                    <option value="no" selected="selected">click me</option>
                    <option value="KZ">Казахстан</option>
                    <option value="KG">Киргизия</option>
                </select>
            </div>

            resize_selector


            <div class="input-container">
              <label for="sku" class="url-operator__label form-label">1. SKU:</label>
              <input class="form-input" type="text" id="sku" name="sku" required="">
            </div>

            <div class="input-container">
              <label for="title" class="url-operator__label form-label">2. Название:</label>
              <textarea class="url-operator__input form-input" type="text" id="title" onkeydown="this.style.width = ((this.value.length + 1) * 8) + 'px';" name="title" required=""></textarea>
            </div>
            <div class="input-container">
              <label for="title_bottom" class="url-operator__label form-label">2.1 Нижняя часть названия:</label>
              <textarea class="url-operator__input form-input" type="text" id="title_bottom" onkeydown="this.style.width = ((this.value.length + 1) * 8) + 'px';" name="title_bottom" required=""></textarea>
            </div>
            <div class="input-container">
              <label for="description" class="url-operator__label form-label">3. Описание:</label>
              <textarea class="url-operator__input form-input" type="text" id="description" onkeydown="this.style.width = ((this.value.length + 1) * 8) + 'px';" name="description" required=""></textarea>
            </div>
            <div class="input-container">
              <label for="description_bottom" class="url-operator__label form-label">3.1 Нижняя часть описания:</label>
              <textarea class="url-operator__input form-input" type="text" id="description_bottom" onkeydown="this.style.width = ((this.value.length + 1) * 8) + 'px';" name="description_bottom" required=""></textarea>
            </div>        
            <div class="input-container">
              <label for="price_old" class="url-operator__label form-label">4. Цена старая:</label>
              <input class="form-input" type="text" id="price_old" name="price_old" required="">
            </div>
            <div class="input-container">
              <label for="price_current" class="url-operator__label form-label">5. Цена текущая:</label>
              <input class="form-input" type="text" id="price_current" name="price_current" required="">
            </div>
            <div class="input-container">
              <label for="vendor" class="url-operator__label form-label">6. Бренд:</label>
              <input class="form-input" type="text" id="vendor" name="vendor" required="">
            </div>     

            <div class="input-container">
              <label for="event_name" class="url-operator__label form-label">7. Название верхнего события на плашке:</label>
              <input class="form-input" type="text" id="event_name" name="event_name" required="">
            </div>   
            <div class="input-container">
              <label for="event_value" class="url-operator__label form-label">8. Значение верхнего события на плашке:</label>
              <input class="form-input" type="text" id="event_value" name="event_value" required="">
            </div>
            
            <div class="input-container">
              <label for="event_name_2" class="url-operator__label form-label">9. Название нижнего события на плашке:</label>
              <input class="form-input" type="text" id="event_name_2" name="event_name_2" required="">
            </div>   
            <div class="input-container">
              <label for="event_value_2" class="url-operator__label form-label">10. Значение нижнего события на плашке:</label>
              <input class="form-input" type="text" id="event_value_2" name="event_value_2" required="">
            </div>                                       

            <button class="submit-btn" type="button" onclick="getDataSKU(form_target)" form="form_target" value="Получить Данные о Товаре">
              Получить Данные
            </button>
            <button class="submit-btn" type="button" onclick="generate(form_target)" form="form_target" value="Сгенерировать">
              Сгенерировать
            </button>
            """
    }

    return templates[template_id].replace('resize_selector', resize_selector)


async def get_prices(sku, locale):
    """
    Function gets the prices of the given product depending on the KZ or KG locale
    Return price_old and price_current
    """

    if locale == 'KG':
        sql_to_get_prices = f"""
        SELECT zcpe."/BIC/ZITEMSN" AS sku, sapbpaa_price."/BIC/ZPRICESOM" AS current_price, sapbpaa_price."/BIC/ZXPRICKGS" 
        AS old_price
        from "SAPBPA"."/BIC/AZAD_EDMC2" zcpe
        LEFT OUTER JOIN "SAPBPA"."/BIC/TZSHOPS" sapbpaa 
        ON zcpe."/BIC/ZSHOPS" = sapbpaa."/BIC/ZSHOPS"
        LEFT OUTER JOIN "SAPBPA"."/BIC/MZITEMSN" sapbpaa_price
        ON zcpe."/BIC/ZITEMSN" = sapbpaa_price."/BIC/ZITEMSN"
        WHERE "TXTLG" = 'Бишкек Ларель' 
        AND "DATE0" = (SELECT CURRENT_DATE FROM DUMMY) 
        AND "/BIC/ZKF_REMQ" > 0 
        AND "/BIC/ZKF_REMQ" IS NOT NULL AND sapbpaa_price."/BIC/ZPRICESOM" != '' 
        AND CAST(zcpe."/BIC/ZITEMSN" as INTEGER) = {int(sku)} 
        GROUP BY zcpe."/BIC/ZITEMSN", zcpe."/BIC/ZKF_REMQ", sapbpaa_price."/BIC/ZPRICESOM",  sapbpaa_price."/BIC/ZXPRICKGS"
        """
        # connection = conn_hana.raw_connection()
        # cursor = connection.cursor()
        # cursor.execute(sql_to_get_prices)

        df_prices = pd.read_sql(sql_to_get_prices, con=conn_hana, columns=['sku', 'CURRENT_PRICE', 'OLD_PRICE'])
    elif locale == 'KZ':
        sql_to_get_prices = f"""
        SELECT
            sku,
            retail_price as CURRENT_PRICE,
            internet_price as OLD_PRICE
        FROM
            k2_mongo_product_prices
        WHERE
            sku = '{sku}' and
            city_id = '0'
        """
        df_prices = pd.read_sql(sql_to_get_prices, conn_public)
        df_prices = df_prices.rename(columns={"current_price": 'CURRENT_PRICE', "old_price": "OLD_PRICE"})
        print(df_prices)

    if df_prices.empty:
        return False

    price_current = str(df_prices['CURRENT_PRICE'][0])
    price_old = str(df_prices['OLD_PRICE'][0])

    return {"price_old": price_old,
            "price_current": price_current}


async def get_details(sku, locale):
    """
    Function gets the description, product name and vendor from postgres/public/technodom_rees_feed
    """

    sql_to_get_details = f"""
    select name, vendor
    from technodom_rees_feed
    where offer_id = '{str(sku)}'
    """

    df = pd.read_sql(sql_to_get_details, conn_public)

    title = df['name'][0]
    vendor = df['vendor'][0]

    return {"title": title,
            "vendor": vendor}


async def generate_html_markup_for_visuals(username, request):
    topnav = generate_top_nav_from_username(username)

    return templates.TemplateResponse('index.html', {'request': request, 'topnav': topnav})


async def create_base(df):
    """
    Function creates the base for future interactions
    """
    base_width = int(df.loc[df['element_name'] == 'base_image', 'width'])
    base_height = int(df.loc[df['element_name'] == 'base_image', 'height'])

    # CREATING A BLANK BASE IMAGE
    image_base = np.zeros((base_height, base_width, 3), np.uint8)
    image_base[::] = (255, 255, 255)

    return image_base


async def put_images(product_pic, vendor_logo, df, image_base, template_group):
    """
    Function to iterate through image objects and put them on the base image
    """
    base_width = int(df.loc[df['element_name'] == 'base_image', 'width'])
    base_height = int(df.loc[df['element_name'] == 'base_image', 'height'])

    if template_group == 'basic':
        product_max_height = int(df.loc[df['element_name'] == 'product_image', 'height'])
        product_max_width = int(df.loc[df['element_name'] == 'base_image', 'width']) - int(
            (df.loc[df['element_name'] == 'side_border', 'width'] * 2))
    elif template_group == '2_events':
        image_product = product_pic
        coefficient = image_product.shape[0] / image_product.shape[1]

        if coefficient <= 1:
            pic_direction = 'horizontal'
            product_max_height = int(df.loc[df['element_name'] == 'product_image_horizontal', 'height'])
            product_max_width = int(df.loc[df['element_name'] == 'product_image_horizontal', 'width'])
            product_target_x = int(df.loc[df['element_name'] == 'product_image_horizontal', 'x'])
            product_target_y = int(df.loc[df['element_name'] == 'product_image_horizontal', 'y'])
        else:
            pic_direction = 'vertical'
            product_max_height = int(df.loc[df['element_name'] == 'product_image_vertical', 'height'])
            product_max_width = int(df.loc[df['element_name'] == 'product_image_vertical', 'width'])
            product_target_x = int(df.loc[df['element_name'] == 'product_image_vertical', 'x'])
            product_target_y = int(df.loc[df['element_name'] == 'product_image_vertical', 'y'])

    df = df.loc[df['group'] == 'images']

    product_image_drawn = 0
    for index, row in df.iterrows():

        target_height = int(row['height'])
        target_width = int(row['width'])

        target_x = int(row['x'])
        target_y = int(row['y'])
        if row['file'] == 'resources/visuals/{sku}.png':
            if product_image_drawn == 1:
                continue
            product_image_drawn = 1

            if template_group == 'basic':
                image_product = product_pic

                coefficient = image_product.shape[0] / image_product.shape[1]
                target_width = int(target_height / coefficient)

                image_product_temp = cv2.resize(image_product, (target_width, target_height))

                if image_product_temp.shape[1] > product_max_width:
                    target_width = product_max_width
                    coefficient_extra = product_max_width / image_product_temp.shape[1]

                    target_height = int(round(product_max_height * coefficient_extra, 0))
                    image_product = cv2.resize(image_product, (target_width, target_height))
                    target_y = target_y + int(round((product_max_height - target_height) / 2, 0))
                else:
                    image_product = image_product_temp

                target_x = int(base_width / 2 - target_width // 2)

                print(target_x, target_y, target_width, target_height)
            elif template_group == '2_events':

                if pic_direction == 'horizontal':
                    target_height = product_max_height
                    target_width = product_max_width
                    coefficient_target = target_height / target_width
                    if coefficient >= coefficient_target:
                        # IF THE IMAGE WILL EXCEED MAX HEIGHT OF FRAME
                        target_height = product_max_height
                        target_width = int(target_height / coefficient)
                        target_x = product_target_x + (product_max_width - target_width) // 2
                        target_y = product_target_y + (product_max_height - target_height) // 2
                    else:
                        # IF THE IMAGE WILL EXCEED MAX WIDTH OF FRAME
                        print('i work')
                        target_width = product_max_width
                        target_height = int(product_max_width * coefficient)
                        target_y = product_target_y + (product_max_height - target_height) // 2
                        target_x = product_target_x + (product_max_width - target_width) // 2
                if pic_direction == 'vertical':
                    target_height = product_max_height
                    target_width = product_max_width
                    coefficient_target = target_height / target_width
                    if coefficient >= coefficient_target:
                        # IF THE IMAGE WILL EXCEED MAX HEIGHT OF FRAME
                        target_height = product_max_height
                        target_width = int(target_height / coefficient)

                        # target_x = product_target_x

                        target_x = product_target_x + (product_max_width - target_width) // 2

                        # target_x = product_target_x + (product_max_height - target_height) // 2

                        # target_y = product_target_y

                        target_y = product_target_y + (product_max_height - target_height) // 2

                        # target_y = product_target_y + (product_max_width - target_width) // 2
                    else:
                        # IF THE IMAGE WILL EXCEED MAX WIDTH OF FRAME
                        print('i work')
                        target_width = product_max_width
                        target_height = int(product_max_width * coefficient)
                        target_y = product_target_y + (product_max_height - target_height) // 2
                        target_x = product_target_x + (product_max_width - target_width) // 2

                image_product = cv2.resize(image_product, (target_width, target_height))

            image_product = cv2.cvtColor(image_product, cv2.COLOR_BGR2RGB)
            print(target_height)
            print(target_width)
            print(target_x)
            print(target_y)
            image_base[target_y:target_y + target_height, target_x:target_x + target_width] = image_product[::]
        elif row['file'] == 'resources/visuals/{vendor}.png':
            vendor_logo = vendor_logo
            vendor_logo = cv2.cvtColor(vendor_logo, cv2.COLOR_BGR2RGB)

            image_base[target_y:target_y + target_height, target_x:target_x + target_width] = vendor_logo[::]
        elif row['element_name'] == 'plashka':
            file = row['file']

            plashka = cv2.imread(file)
            plashka = cv2.cvtColor(plashka, cv2.COLOR_BGR2RGB)

            image_base[target_x:target_x + target_width, target_y:target_y + target_height] = plashka[::]

    return image_base


async def put_names(image_base, df, names, details):
    df = df.loc[df['group'] == 'product_data']

    pil_im = Image.fromarray(image_base)
    draw = ImageDraw.Draw(pil_im)

    for index, row in df.iterrows():

        font = ImageFont.truetype(row['file'], int(row['font_size']))

        target_x = row['x']
        target_y = row['y']
        target_color = eval(str(row['color']))

        if row['element_name'] == 'product_name_top':
            draw.text((target_x, target_y), names[0].upper(), font=font, fill=target_color)
        if row['element_name'] == 'product_name_bottom' and len(names) == 2:
            if names[1] is None or names[1] == 'None':
                continue
            draw.text((target_x, target_y), names[1].upper(), font=font, fill=target_color)

        if row['element_name'] == 'product_description_top' and len(names) == 1 and len(details) == 1:
            print(df.loc[df['element_name'] == 'product_price_bottom', 'x'])
            target_x = int(df.loc[df['element_name'] == 'product_name_bottom', 'x'])
            target_y = int(df.loc[df['element_name'] == 'product_name_bottom', 'y'])
            draw.text((target_x, target_y), details[0].upper(), font=font, fill=target_color)
        if row['element_name'] == 'product_description_top' and (len(names) == 2 or len(details) == 2):
            if details[0] is None or details[0] == 'None':
                continue
            draw.text((target_x, target_y), details[0].upper(), font=font, fill=target_color)

        if row['element_name'] == 'product_description_bottom' and len(details) == 2:
            if details[1] is None or details[1] == 'None':
                continue
            draw.text((target_x, target_y), details[1].upper(), font=font, fill=target_color)

    return pil_im


async def put_event(pil_im, df, event_details):
    df = df.loc[df['group'] == 'event_data']

    draw = ImageDraw.Draw(pil_im)

    inputs = {"event_name": event_details[0],
              "event_value": event_details[1],
              "event_name_2": event_details[2],
              "event_value_2": event_details[3]}

    for index, row in df.iterrows():

        font = ImageFont.truetype(row['file'], int(row['font_size']))

        target_x = row['x']
        target_y = row['y']
        target_color = eval(str(row['color']))

        if row['element_name'] == 'event_separator_line':
            target_width = row['width']
            draw.line([(target_x, target_y), ((target_x + target_width) * (1), target_y)], fill=target_color,
                      width=5)
            continue

        if inputs[str(row['element_name'])] is not None:
            draw.text((target_x, target_y), inputs[str(row['element_name'])].upper(), font=font, fill=target_color)

    return pil_im


async def put_old_price(pil_image_base, df, old_price):
    df = df.loc[df['group'] == 'prices_old']

    draw = ImageDraw.Draw(pil_image_base)

    price_old = int(old_price.replace('.00', '').replace(' ', ''))
    price_old = str(price_old)[::-1]
    target_len = len(price_old) + (len(price_old) // 3.5)

    for i in range(int(target_len) - len(price_old)):
        price_old = price_old[:(4 * i + 3)] + ' ' + price_old[(4 * i + 3):]

    price_old = price_old[::-1]

    for index, row in df.iterrows():
        target_x = row['x']
        target_y = row['y']
        target_width = row['width']
        target_height = row['height']
        target_color = eval(row['color'])
        font = ImageFont.truetype(row['file'], int(row['font_size']))

        if row['element_name'] == 'price_old':
            draw.text((target_x, target_y), price_old.upper(), font=font, fill=target_color)
        else:
            (price_old_width, baseline), (offset_x, offset_y) = font.font.getsize(price_old)
            draw.line([(target_x, target_y), ((target_x + price_old_width) * (1), target_y)], fill=target_color,
                      width=5)

    return pil_image_base


async def put_real_prices(pil_image_base, df, price_real, locale):
    df = df.loc[df['group'] == 'prices_real']
    draw = ImageDraw.Draw(pil_image_base)

    price_real = int(price_real.replace('.00', '').replace(' ', ''))
    price_real = str(price_real)[::-1]
    target_len = len(price_real) + (len(price_real) // 3.5)

    for i in range(int(target_len) - len(price_real)):
        price_real = price_real[:(4 * i + 3)] + ' ' + price_real[(4 * i + 3):]

    prices = price_real[::-1].split(' ')

    visible_M = len(prices) // 3
    visible_T = len(prices) // 2
    visible_H = 1
    visible_S = 1

    while len(prices) != 3:
        prices = [None] + prices

    for index, row in df.iterrows():
        if row['element_name'] != 'price_real_S':
            font = ImageFont.truetype(row['file'], int(row['font_size']))
        target_x = row['x']
        target_y = row['y']
        target_width = row['width']
        target_height = row['height']
        target_color = eval(row['color'])
        try:
            target_shift_x = int(row['shift_x'])
        except:
            target_shift_x = 0

        if row['element_name'] == 'price_real_M':
            if visible_M == 0:
                width_M = 0
                previous_x = target_x
                continue
            else:
                previous_x = target_x
                previous_y = target_y
                (width_M, baseline), (offset_x, offset_y) = font.font.getsize(prices[0])
                draw.text((target_x, target_y), prices[0].upper(), font=font, fill=target_color)

        if row['element_name'] == 'price_real_T':
            if visible_T == 0:
                width_T = 0
                continue
            else:
                (width_T, baseline), (offset_x, offset_y) = font.font.getsize(prices[1])
                target_x = previous_x + (width_M + target_shift_x) * visible_M
                previous_x = target_x
                draw.text((target_x, target_y), prices[1].upper(), font=font, fill=target_color)

        if row['element_name'] == 'price_real_H':
            if visible_H == 0:
                width_H = 0
                continue
            else:
                (width_H, baseline), (offset_x, offset_y) = font.font.getsize(prices[2])
                target_x = previous_x + (width_T + target_shift_x) * visible_T
                previous_x = target_x
                draw.text((target_x, target_y), prices[2].upper(), font=font, fill=target_color)

        if row['element_name'] == 'price_real_S':
            target_file = row['file'].replace('.jpg', f'_{locale.lower()}.jpg')
            price_real_S = cv2.imread(target_file)
            price_real_S = cv2.cvtColor(price_real_S, cv2.COLOR_BGR2RGB)
            image_base = np.asarray(pil_image_base)
            target_x = previous_x + (width_H + target_shift_x) * visible_H

            image_base[target_y:target_y + target_height, target_x:target_x + target_width] = price_real_S[::]
            pil_image_base = Image.fromarray(image_base)

    return pil_image_base


async def get_data_from_sku(username, input_dict):
    """
    Function gets the name, description, prices and vendor of a given SKU
    Then it returns the retrieved data to the user
    """

    general_dict = {}

    prices = await get_prices(input_dict.sku, input_dict.locale)

    if not prices:
        return {'is_available': 'False'}

    details = await get_details(input_dict.sku, input_dict.locale)

    general_dict['is_available'] = 'True'
    general_dict['price_old'] = prices['price_old']
    general_dict['price_current'] = prices['price_current']
    general_dict['vendor'] = details['vendor']
    general_dict['title'] = details['title']

    return general_dict


async def generate_visual(username, input_dict):
    """
    Function receives the data related to the given product in order to generate the image step by step
    Returns a link to the generated image uploaded to SFTP
    """

    sku = input_dict.sku
    title = input_dict.title
    title_bottom = input_dict.title_bottom
    description = input_dict.description
    description_bottom = input_dict.description_bottom
    price_old = input_dict.price_old
    price_current = input_dict.price_current
    vendor = input_dict.vendor
    event_name = input_dict.event_name
    event_value = input_dict.event_value
    event_name_2 = input_dict.event_name_2
    event_value_2 = input_dict.event_value_2
    locale = input_dict.locale
    resize = input_dict.resize
    template_group = input_dict.template_group

    if title_bottom is None:
        product_names = [title]
    else:
        product_names = [title, title_bottom]

    if description_bottom is None:
        product_details = [description]
    else:
        product_details = [description, description_bottom]

    event_details = [event_name, event_value, event_name_2, event_value_2]

    df = pd.read_excel(f'resources/visuals/templates/{template_group}/{resize}.xlsx')
    df['file'] = 'resources/visuals/' + df['file'].astype(str)
    image_base = await create_base(df)

    vendor_logo = await get_logo(vendor)
    cropped_image = await prepare_image(sku)

    image_base = await put_images(cropped_image, vendor_logo, df, image_base, template_group)
    pil_image_base = await put_names(image_base, df, product_names, product_details)
    pil_image_base = await put_event(pil_image_base, df, event_details)

    if price_old != price_current:
        pil_image_base = await put_old_price(pil_image_base, df, price_old)

    pil_image_base = await put_real_prices(pil_image_base, df, price_current, locale)

    pil_image_base.save('visuals.png')

    remote_dir = f'/html/under/feed/tddmdui/results/apitemplate/results/{str(datetime.now()).replace(" ", "").replace(":", "").replace(".", "")}.png'
    sftp_sender('visuals.png', remote_dir)
    result_link = remote_dir.replace('/html', 'https://www.technodom.kz')

    df = pd.DataFrame([{
        "date": str(datetime.now()),
        "author": str(username),
        "sku": str(sku),
        "title": str(title),
        "description": description,
        "price_old": str(price_old),
        "price_current": str(price_current),
        "vendor": str(vendor),
        "event_name": str(event_name),
        "event_value": str(event_value),
        "locale": str(locale),
        "result_link": str(result_link)
    }])

    df.to_sql('smm_generated_apitemplate_history', index=False, if_exists='append', con=conn_django)

    dimensions = resize.split('x')

    return {'link': result_link, 'width': f'{dimensions[1]}', 'height': f'{dimensions[0]}'}


async def get_logo(vendor):
    """
    Function tries to get a logo of the given vendor
    Then it returns False in case no corresponding logo
    And w/h correlation coef in case there is a logo
    """

    vendor = vendor.replace(' ', '_').replace('/', '_')

    url = f"https://www.technodom.kz/under/feed/tddmdui/results/apitemplate/vendor_logos/{vendor}.jpg"
    try:
        req = urllib.request.urlopen(url)
        arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
        image = cv2.imdecode(arr, 1)
        # correlation = image.shape[0] / image.shape[1]
        return image
    except:
        req = urllib.request.urlopen(
            'https://www.technodom.kz/under/feed/tddmdui/results/apitemplate/vendor_logos/no_logo.jpg')
        arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
        image = cv2.imdecode(arr, 1)
        # correlation = image.shape[0] / image.shape[1]
        return image


async def prepare_image(sku):
    """
    Gets an image from SKU.
    Crops the outer white space to leave only the product itself
    :param sku:
    :return: cropped image ready to push to SFTP
    """

    sql = f"""
    select image
    from k2_image_api_links
    where sku = '{str(sku)}'
    """

    df = pd.read_sql(sql, conn_public)

    if df.empty:
        return False, False

    link = df['image'][0]

    req = urllib.request.urlopen(link)
    arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
    image = cv2.imdecode(arr, 1)

    imgray = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
    ret, thresh = cv2.threshold(imgray, 250, 255, cv2.THRESH_TOZERO_INV)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    acceptable = False

    c = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(c)
    if w * h >= image.shape[0] * image.shape[1] * 0.3:
        acceptable = True

    if not acceptable:
        x, y, w, h = 0, 0, image.shape[0], image.shape[1]

    cropped = image[y:y + h, x:x + w]

    local_filename = f'{sku}.png'
    remote_filename = f'/html/under/feed/tddmdui/results/apitemplate/cropped/{sku}.png'

    cv2.imwrite(local_filename, cropped)

    # correlation = cropped.shape[0] / cropped.shape[1]

    sftp_sender(local_filename, remote_filename)

    os.remove(local_filename)

    return cropped


async def adjust_stroke(price_old):
    """
    Function assesses the occupied width of price_old to adjust the strike size
    """

    price_old = price_old.replace('.00', '')

    font_path = 'resources/MuseoSansCyrl_3.otf'

    font_price = ImageFont.truetype(font_path, 40)
    font_strike = ImageFont.truetype(font_path, 40)

    price_old = str(int(price_old) // 1000) + ' ' + str(price_old)[-3:]

    strike = ''

    (width_price, baseline), (offset_x, offset_y) = font_price.font.getsize(price_old)
    (width_strike, baseline), (offset_x, offset_y) = font_strike.font.getsize(strike)

    while width_price > width_strike:
        strike += ' '
        (width_strike, baseline), (offset_x, offset_y) = font_strike.font.getsize(strike)

    return price_old, strike


async def adjust_prices(price_current, locale):
    """
    Function separates the price_current to thousands and units
    Assesses the occupied width by the components
    Then adjusts them via adding a space at the beginning of each component

    Returns price_current_left, price_current_right and price_current_symbol strings
    """

    font_path = 'resources/MuseoSansCyrl_3.otf'

    font_left = ImageFont.truetype(font_path, 84)
    font_right = ImageFont.truetype(font_path, 65)
    font_symbol = ImageFont.truetype(font_path, 40)

    price_current = int(price_current.replace('.00', ''))

    price_current_left = str(price_current // 1000)
    price_current_right = str(price_current)[-3:]

    if price_current_left == '0':
        price_current_left = ''

    space_right = ''
    space_symbol = ''

    if locale == 'KG':
        price_current_symbol = 'c'
    else:
        price_current_symbol = '₸'

    (width_left, baseline), (offset_x, offset_y) = font_left.font.getsize(price_current_left)
    (width_space_right, baseline), (offset_x, offset_y) = font_right.font.getsize(space_right)

    while width_left > width_space_right + 5:
        space_right += ' '
        (width_space_right, baseline), (offset_x, offset_y) = font_right.font.getsize(space_right)

    price_current_right = space_right + price_current_right

    (width_right, baseline), (offset_x, offset_y) = font_right.font.getsize(price_current_right)
    (width_space_symbol, baseline), (offset_x, offset_y) = font_symbol.font.getsize(space_symbol)

    while width_right > width_space_symbol + 5:
        space_symbol += ' '
        (width_space_symbol, baseline), (offset_x, offset_y) = font_symbol.font.getsize(space_symbol)

    price_current_symbol = space_symbol + price_current_symbol

    return price_current_left, price_current_right, price_current_symbol


async def post_to_telegram(data):

    bot = Bot(token=bot_token)

    print(data.title_bottom)

    if data.template_group == 'basic':
        message = f"""
*{data.event_name.upper()} {data.event_value.upper()}*

[{data.title} {data.title_bottom}](generated_link)

*только в Technodom!*    
        """
    elif data.template_group == '2_events':
        message = f"""
*{data.event_name.upper()} {data.event_value.upper()}*
    +
*{data.event_name_2.upper()} {data.event_value_2.upper()}*

[{data.title} {data.title_bottom}](generated_link)

*только в Technodom!*    
            """
    if data.locale.lower() == 'kg':
        product = 'product'
    else:
        product = 'p'

    message = message.replace('generated_link',f'https://www.technodom.{data.locale.lower()}/{product}/{data.sku}?utm_source=telegram&utm_medium=social&utm_campaign=telegram-social-product-price-autopost')

    test_button = InlineKeyboardButton('НА САЙТ', url='https://www.technodom.kz')

    await bot.send_photo(chat_id=target_chat_name, caption=message, photo=data.image_link, parse_mode='Markdown')
    await bot.send_message(chat_id=target_chat_name,reply_markup=InlineKeyboardMarkup(resize_keyboard=True).add(test_button),text='TEST CAPTION')
    # await bot.send_message(chat_id=target_chat_name, text=message)
