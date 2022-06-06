import pysftp
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import create_engine
import psycopg2
import io
import base64
import pandas as pd
import openpyxl
import pyhdb
from PIL import Image
from datetime import datetime
from hdbcli import dbapi

dbschema = 'django'

conn_django = create_engine()

dbschema = 'public'
conn_public = create_engine()

conn_hana = dbapi.connect()


urls_paths = ['/urls', '/urls/generate', '/urls/generate/multi', '/urls/generate/banks', '/urls/generate/deeplinks']
smm_paths = ['/smm']
seo_paths = ['/seo']
home_paths = ['/home', '/upload', '/upload/new', '/upload/history']
analysis_paths = ['/analysis', '/analysis/abc_recompile', '/analysis/abc_no_recompiling']
direct_paths = ['/direct', '/direct/letter', '/direct/refresh', '/direct/sms']
custom_paths = ['/custom', '/custom/refresh', '/custom/create']
content_paths = ['/content/reports', '/content/smart_consumer']
content_mapping_paths = ['/content/mapping', '/content/mapping/create']
content_mapping_change_paths = ['/content/mapping/change']
promotion_top_4_paths = ['/promotion', '/promotion/add_top_4', '/promotion/check_top_4', '/promotion/history_top_4']
visuals_paths = ['/visuals', '/visuals/get_data_from_sku', '/visuals/generate']
map_events_paths = ['/map_events', '/map_events/special_offer', '/map_events/call_to_action', '/map_events/event']

security = HTTPBasic()


no_access_html = """
<html>
        <head>
                    <title>ACCESS DENIED</title>
        </head>
        <body>
        <p>Затычка: у тебя нет доступа.</p>
        </body>
</html>
"""

pth = {"string": "text",
       "boolean": "checkbox"}

modules = {'SMM Reports': '/smm',
           'SMM Story Generator': '/smm/generate/story',
           'SEO Reports': '/seo',
           'SEO Map Events Operator': '/map_events',
           'ANALYSIS Reports': '/analysis',
           'CONTENT Reports': '/content/reports',
           'CONTENT Mapping Operator': '/content/mapping',
           'URL Operator': '/urls',
           'Direct Channels Operator': '/direct',
           'Custom Events Operator': '/custom',

           'PROMOTION Top4 Operator': '/promotion',
           'VISUALS Operator': '/visuals',

           'File Upload Operator': '/upload',
           'VIP File Upload Operator': '/vip_upload'}

modules_pics = {'SMM Reports': 'https://www.technodom.kz/under/feed/tddmdui/resources/twitter.png',
                'SMM Story Generator': 'https://www.technodom.kz/under/feed/tddmdui/resources/twitter.png',
                'SEO Reports': 'https://www.technodom.kz/under/feed/tddmdui/resources/seo.png',
                'SEO Map Events Operator': 'https://www.technodom.kz/under/feed/tddmdui/resources/seo.png',
                'ANALYSIS Reports': 'https://www.technodom.kz/under/feed/tddmdui/resources/analysis.png',
                'CONTENT Reports': 'https://www.technodom.kz/under/feed/tddmdui/resources/content.png',
                'CONTENT Mapping Operator': 'https://www.technodom.kz/under/feed/tddmdui/resources/mapping.png',
                'URL Operator': 'https://www.technodom.kz/under/feed/tddmdui/resources/url-operator.svg',
                'Direct Channels Operator': 'https://www.technodom.kz/under/feed/tddmdui/resources/direct.png',
                'Custom Events Operator': 'https://www.technodom.kz/under/feed/tddmdui/resources/events.png',

                'PROMOTION Top4 Operator': 'https://www.technodom.kz/under/feed/tddmdui/resources/promotion.png',
                'VISUALS Operator': 'https://www.technodom.kz/under/feed/tddmdui/resources/visuals.png',

                'File Upload Operator': 'https://www.technodom.kz/under/feed/tddmdui/resources/upload.png',
                'VIP File Upload Operator': 'https://www.technodom.kz/under/feed/tddmdui/resources/upload.png'}


def sftp_sender(local_file, remote_dir):
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None

    myUsername = ""
    myPassword = ""
    myHostname = ""

    with pysftp.Connection(host=myHostname, username=myUsername, password=myPassword, port=2823, cnopts=cnopts) as sftp:
        try:
            sftp.put(local_file, remote_dir)
        except Exception as e:
            print('smth wrong happened during upload!')
            print(e)


def check_credentials_access(username, password):
    sql = f"""
    select username, password
    from users
    where username = '{username}'
    and password = '{password}'
    """

    df = pd.read_sql(sql, con=conn_django)

    if not df.empty:
        return True

    return False


def get_username_role(username):
    sql = f"""
    select role
    from users
    where username = '{username}'
    """

    df = pd.read_sql(sql, con=conn_django)
    return df['role'][0]


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    if not check_credentials_access(credentials.username, credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def check_role_paths(path, username):
    role = get_username_role(username)

    sql = f"""
    select paths
    from roles
    where role = '{role}'
    """

    df = pd.read_sql(sql, conn_django)
    paths = eval(df['paths'][0])

    if path not in paths:
        return False
    else:
        return True


def read_binary_excel(file_str):
    file64 = file_str.replace('data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,',
                              '')
    file = base64.b64decode(file64)

    xlsx = io.BytesIO(file)

    wb = openpyxl.load_workbook(xlsx)
    ws = wb.worksheets[0]

    data = ws.values

    df = pd.DataFrame(data)
    df.columns = df.iloc[0]
    df = df.drop(df.index[0])

    return df


async def read_binary_image(file_str):
    file64 = file_str.replace('data:image/png;base64,', '')
    file = base64.b64decode(file64)

    img = io.BytesIO(file)

    image = Image.open(img)
    image.save('temp_image.png')

    remote_dir = f'/html/under/feed/tddmdui/received/MapEventsVisual_{str(datetime.today()).replace(" ", "").replace(":", "")}.png'

    sftp_sender('temp_image.png', remote_dir)

    return "https://new.technodom.kz" + remote_dir.replace('/html', '')
