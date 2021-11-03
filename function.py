import datetime
import requests
from io import BytesIO
from sqlalchemy.sql.schema import MetaData
from source import *
import mysql.connector
import pandas as pd
import json
import requests
from requests_toolbelt import MultipartEncoder
import sqlalchemy

class DB:
    mydb = None

    def connect(self,dbname=databasedb):
        self.mydb = mysql.connector.connect(
            host=hostdb,
            user=userdb,
            password=passworddb,
            database=dbname,
            port='3306'
        )

    def query(self, task):
        try:
            self.connect()
            mycursor = self.mydb.cursor(buffered=True)
            mycursor.execute(task)
        except:
            self.connect()
            mycursor = self.mydb.cursor(buffered=True)
            mycursor.execute(task)
        return mycursor
    def query_custom(self, task,db):
        try:
            self.connect(dbname=db)
            mycursor = self.mydb.cursor(buffered=True)
            mycursor.execute(task)
        except:
            self.connect()
            mycursor = self.mydb.cursor(buffered=True)
            mycursor.execute(task)
        return mycursor

    def query_commit(self, task):
        try:
            self.connect()
            mycursor = self.mydb.cursor(buffered=True)
            mycursor.execute(task)
            mycursor.commit()
        except:
            self.connect()
            mycursor = self.mydb.cursor(buffered=True)
            mycursor.execute(task)
            self.mydb.commit()
        return mycursor

    def callproc(self, procname: str, task_db, task_db2):
        arg = [task_db, task_db2]
        try:
            self.connect()
            mycursor = self.mydb.cursor(buffered=True)
            mycursor.callproc(procname, arg)
            self.mydb.commit()
        except:
            self.connect()
            mycursor = self.mydb.cursor(buffered=True)
            mycursor.callproc(procname, arg)
            self.mydb.commit()
    
    def create_table(self,dbname):
        task = f'''create table if not exists {dbname} (  `sku` longtext NOT NULL,
                    `descript` longtext,
                    `amount` int DEFAULT NULL )'''
        db.query_commit(task)
        # print(task)

    def insert_into_duplicate(self,dbname,data,amount):
        task = f"""
        INSERT INTO {dbname}(sku, descript, amount)
        VALUES ({data})
        ON DUPLICATE KEY UPDATE amount = {amount};  
        """
        # db.query_commit(task)
        print(task)
db = DB()

def add(sku, user):
    task_db = f'insert into {get_role(user,"department")}.live_room values ("{sku}","{str(datetime.datetime.now()).split(".")[0]}","{user}")'
    db.query_commit(task_db)

def delete(sku, user):
    task_db = f'delete from {get_role(user,"department")}.live_room where sku = "{sku}"'
    db.query_commit(task_db)
    # send_line(f"รหัส {sku} เอาออกโดย {user}")
    if '-' in sku:
        sku = sku.split('-')[0]
    task_db = f"select size from zortmain where sku like '%{sku}%' and amount > 0 \
    ORDER BY FIELD(size, 'XXS', 'XS', 'S', 'M', 'L', 'XL', 'XXL', 'F'), size"
    mycursor = db.query(task_db)
    myresult = list(mycursor.fetchall())
    if not len(myresult) == 0:
        for i in myresult[0]:
            if i == 'S':
                return i
            elif i == 'M':
                return i
            elif i == 'L':
                return i
            elif i == 'XL':
                return i
            elif i == 'XXL':
                return i
            elif i == 'F':
                return i
    else:
        return False

def get_mysql_path():
    mydb = mysql.connector.connect(
        host=hostdb,
        user=userdb,
        password=passworddb,
        database=databasedb
    )
    mycursor = mydb.cursor()
    mycursor.execute('SHOW VARIABLES LIKE "secure_file_priv";')
    return mycursor.fetchone()[1]

def convert_url_to_bytes(url):
    try:
        response = requests.get(url, stream=True)
        data = BytesIO(response.content)
        return data.getvalue()
    except:
        return None

def get_api_register(department, api):
    """
    select {column} from store_api where department
    """
    mycursor = db.query(
        f"select {api} from store_api where department = '{department}'")
    try:
        return list(mycursor.fetchall())[0][0]
    except:
        return None

def get_role(req, role):
    """
        get {columns} from register_employee
    """

    if not type(req) == str:
        req = str(req.user)
    mycursor = db.query(
        f"select {role} from register_employee where user = '{req}'")
    try:
        return str(list(mycursor.fetchall())[0][0])
    except:
        return None

def send_line(msg):
    url = 'https://notify-api.line.me/api/notify'
    token = '4E8XnAl7T4tQPUgstBsuwnKr6zTSyMOf4jiRMeWuVwP'
    headers = {'content-type': 'application/x-www-form-urlencoded',
               'Authorization': 'Bearer '+token}
    r = requests.post(url, headers=headers, data={'message': msg})


class Web():
    def __init__(self, apikey, apisecret, storename) -> None:
        self.apikey = apikey
        self.apisecret = apisecret
        self.storename = storename

    #  upload trackingno today to database
    def get_track(self):
        header = {
            'storename': f'{self.storename}',
            'apikey': f'{self.apikey}',
            'apisecret': f'{self.apisecret}'
        }

        url = 'https://api.zortout.com/api.aspx'

        payload = {'method': "GETORDERS", 'version': '3'}

        res = requests.get(url=url, headers=header, params=payload)
        data = res.json()
        trackingno, sku, cstname = [], [], []

        for i in range(len(data['list'])):
            if (data['list'][i]['status']) == 'Waiting':
                for customer in data['list'][i]['list']:
                    trackingno.append(data['list'][i]['trackingno'])
                    sku.append(customer['sku'])
                    cstname.append(data['list'][i]['customername'])
        return trackingno, sku, cstname
    # get data from list of www.api.zort.com

    def get(self, method, datatype, sku, page=1):
        header = {
            'storename': f'{self.storename}',
            'apikey': f'{self.apikey}',
            'apisecret': f'{self.apisecret}'
        }

        url = 'https://api.zortout.com/api.aspx'

        payload = {'method': method, 'version': '3',
                   'page': page, 'searchsku': sku}

        res = requests.get(url=url, headers=header, params=payload)
        data = res.json()
        datalist = []
        for i in range(len(data['list'])):
            datalist.append(data['list'][i][datatype])
        return datalist

    def get_condition(self, method, datatype, amount, page=1):
        header = {
            'storename': f'{self.storename}',
            'apikey': f'{self.apikey}',
            'apisecret': f'{self.apisecret}'
        }

        url = 'https://api.zortout.com/api.aspx'

        payload = {'method': method, 'version': '3',
                   'page': page}

        res = requests.get(url=url, headers=header, params=payload)
        data = res.json()
        datalist = []
        for i in range(len(data['list'])):
            if 0 < int(data['list'][i]['availablestock']) <= amount:
                datalist.append(data['list'][i][datatype])
        return datalist

    def get_condition_2(self, method, datatype, amount, page=1):
        header = {
            'storename': f'{self.storename}',
            'apikey': f'{self.apikey}',
            'apisecret': f'{self.apisecret}'
        }

        url = 'https://api.zortout.com/api.aspx'

        payload = {'method': method, 'version': '3',
                   'page': page}

        res = requests.get(url=url, headers=header, params=payload)
        data = res.json()
        datalist = []
        for i in range(len(data['list'])):
            if int(data['list'][i]['availablestock']) >= amount:
                if datatype == 'availablestock':
                    data['list'][i][datatype] = int(
                        data['list'][i][datatype]) - 3
                datalist.append(data['list'][i][datatype])
        return datalist

    def get_datatype_filter_by_sku(self, method, datatype, sku):
        header = {
            'storename': f'{self.storename}',
            'apikey': f'{self.apikey}',
            'apisecret': f'{self.apisecret}'
        }

        url = 'https://api.zortout.com/api.aspx'

        payload = {'method': method, 'version': '3'}

        res = requests.get(url=url, headers=header, params=payload)
        data = res.json()
        datalist = []
        for i in range(len(data['list'])):
            if data['list'][i]['sku'] == sku:
                return data['list'][i][datatype]
    # post data to www.api.zort.com

    def post(self, method, sku, amount):
        header = {
            'storename': f'{self.storename}',
            'apikey': f'{self.apikey}',
            'apisecret': f'{self.apisecret}'
        }

        url = 'https://api.zortout.com/api.aspx'

        payload = {'method': method, 'version': '3', 'warehousecode': 'W0001'}
        data = {"stocks": [{"sku": f"{sku}", "stock": amount}]}
        res = requests.post(url=url, headers=header, params=payload, json=data)
        data = res.json()
        print(data['resDesc'])
        # for i in range(len(data['list'])):
        #     print(data['list'][i]['customerphone'])

    def post_descript(self, method, sku, descript):
        header = {
            'storename': f'{self.storename}',
            'apikey': f'{self.apikey}',
            'apisecret': f'{self.apisecret}'
        }

        url = 'https://api.zortout.com/api.aspx'

        payload = {'method': method, 'version': '3', 'warehousecode': 'W0001'}
        data = {"sku": f'{sku}', 'description': f'{descript}'}
        res = requests.post(url=url, headers=header, params=payload, json=data)
        data = res.json()
        print(data['resDesc'])
        # for i in range(len(data['list'])):
        #     print(data['list'][i]['customerphone'])

def update_size(apikey,apisecret,storename):
    web =Web(apikey,apisecret,storename)
    df = pd.read_excel(r"C:\Users\Chino\Downloads\Muslin Size.xlsx")
    for i in df.index:
        if  not str(df.loc[i,"SIZE"]) == 'nan':
            web.post_descript("UPDATEPRODUCT",str(df.loc[i,'SKU']),str(df.loc[i,'SIZE']))

def get_data(filter_amount: int, filter_amount_2: int):
    def filter(filter_amount: int):
        web = Web('7KRzYzjPqknzzSM2nVcooo3sWNF6EK4Oyq9QtGI8uyk=',
                  'RA9VD1AjwaHo8UW0uNk924SnxN0xIFIGdlelDEcTEE=', 'Muslin.info@gmail.com')
        sku = web.get_condition("GETPRODUCTS", 'sku', filter_amount)
        name = web.get_condition("GETPRODUCTS", 'name', filter_amount)
        amount = web.get_condition(
            "GETPRODUCTS", 'availablestock', filter_amount)
        purchaseprice = web.get_condition(
            "GETPRODUCTS", 'purchaseprice', filter_amount)
        sku2 = web.get_condition("GETPRODUCTS", 'sku', filter_amount, 2)
        name2 = web.get_condition("GETPRODUCTS", 'name', filter_amount, 2)
        amount2 = web.get_condition(
            "GETPRODUCTS", 'availablestock', filter_amount, 2)
        purchaseprice2 = web.get_condition(
            "GETPRODUCTS", 'purchaseprice', filter_amount, 2)
        sku += [i for i in sku2]
        name += [i for i in name2]
        amount += [i for i in amount2]
        purchaseprice += [i for i in purchaseprice2]
        return sku, name, amount, purchaseprice

    def filter2(filter_amount_2):
        web = Web('7KRzYzjPqknzzSM2nVcooo3sWNF6EK4Oyq9QtGI8uyk=',
                  'RA9VD1AjwaHo8UW0uNk924SnxN0xIFIGdlelDEcTEE=', 'Muslin.info@gmail.com')
        sku = web.get_condition_2("GETPRODUCTS", 'sku', filter_amount_2)
        name = web.get_condition_2("GETPRODUCTS", 'name', filter_amount_2)
        amount = web.get_condition_2(
            "GETPRODUCTS", 'availablestock', filter_amount_2)
        purchaseprice = web.get_condition_2(
            "GETPRODUCTS", 'purchaseprice', filter_amount_2)
        sku2 = web.get_condition_2("GETPRODUCTS", 'sku', filter_amount_2, 2)
        name2 = web.get_condition_2("GETPRODUCTS", 'name', filter_amount_2, 2)
        amount2 = web.get_condition_2(
            "GETPRODUCTS", 'availablestock', filter_amount_2, 2)
        purchaseprice2 = web.get_condition_2(
            "GETPRODUCTS", 'purchaseprice', filter_amount_2, 2)
        sku += [i for i in sku2]
        name += [i for i in name2]
        amount += [i for i in amount2]
        purchaseprice += [i for i in purchaseprice2]
        return sku, name, amount, purchaseprice
    sku, name, amount, purchaseprice = filter(filter_amount)
    sku2, name2, amount2, purchaseprice2 = filter2(filter_amount_2)
    sku += [i for i in sku2]
    name += [i for i in name2]
    amount += [i for i in amount2]
    purchaseprice += [i for i in purchaseprice2]
    return zip(sku, name, amount, purchaseprice)


def export_excel_zortform(less, greate, path):
    df = pd.DataFrame(list(get_data(less, greate)), columns=[
        'รหัสสินค้า', 'ชื่อสินค้า', 'จำนวน', 'ทุน'])
    df['ชื่อคลัง/สาขา'] = 'คลังหลัก'
    today_date = datetime.date.today()
    today_date = today_date.strftime("%d/%m/%Y")
    df['วันที่ทำรายการ'] = ''
    df['วันที่จัดส่ง'] = ''
    df['หมายเลขรายการ'] = ''
    df['ชื่อคู่ค้า'] = ''
    df.at[0, 'หมายเลขรายการ'] = 'VR LIVE'+today_date
    df.at[0, 'ชื่อคู่ค้า'] = 'VR'
    df.at[0, 'วันที่ทำรายการ'] = today_date
    df.at[0, 'วันที่จัดส่ง'] = today_date

    df = df[['หมายเลขรายการ', 'ชื่อคู่ค้า', 'วันที่ทำรายการ', 'วันที่จัดส่ง',
             'ชื่อคลัง/สาขา', 'รหัสสินค้า', 'ชื่อสินค้า', 'จำนวน', 'ทุน']]
    df.to_excel(f'{path}', index=False)
    # result = list(export_excel(5,5))


def export_excel_vrichform(less, greate, path):
    df = pd.DataFrame(list(get_data(less, greate)), columns=[
        'รหัสสินค้า', 'รายละเอียด', 'จำนวน', 'ต้นทุน'])

    def tran(var: str):
        result = var.split('0')[0]
        if len(result) == 2:
            firstchar = result[1]
        else:
            firstchar = result
        try:
            number = int(var.replace(result, '')[:4])
        except:
            print(var)
            return 'wrong'
        return firstchar+str(number)

    df['รหัสขาย'] = df['รหัสสินค้า'].apply(tran)
    df = df[df['รหัสขาย'] != 'wrong']
    df['หน่วย'] = ''
    df['ราคา'] = 790
    df['ค่าส่งเพิ่ม'] = 0
    df['หมายเหตุ'] = ''
    df['จำนวน'] = df['จำนวน'].apply(pd.to_numeric, errors='ignore')
    df['ต้นทุน'] = df['ต้นทุน'].apply(pd.to_numeric, errors='ignore')
    df = df[['รหัสสินค้า', 'รหัสขาย', 'รายละเอียด', 'หน่วย',
             'จำนวน', 'ราคา', 'ต้นทุน', 'ค่าส่งเพิ่ม', 'หมายเหตุ']]
    df.to_excel(f'{path}', index=False)


def export_checkstock(type, path):
    try:
        task = f"TRUNCATE {type};"
        task1 = f"""
        SELECT "รหัสสินค้า","รายละเอียด","จำนวน"
        UNION ALL
        SELECT sku,descript,amount
        FROM {type}
                """
        db.connect()
        df = pd.read_sql(task1, db.mydb)
        df.to_excel(path, index=False, header=False)
        db.query_commit(task)
        return path
    except Exception as e:
        print(e)


def send_message_facebook(recipient_id, message_text):
    params = {
        "access_token": 'EAACNi6PriH4BAHx71ZCuZADZCVWQ0v4ZABJt4IpEN36LCmdYRbYta5oVjcBel7bwiZBV2QU6EN1y0LywjNiHKYAvcOsWslUzJL8ZAuLZAVgP4GNRZCMCZBLw54alXAfsnwVxlHZCnQxY1Qkp8088HiMuBTeecFKrvqJSxlwsXvlH59iKCR9H9EVhFYjWV1yNt8BS4pO8b4CH781QP8ClSB7r33'
    }
    print(os.getcwd())
    data = {
        # encode nested json to avoid errors during multipart encoding process
        'recipient': json.dumps({
            'id': recipient_id
        }),
        # encode nested json to avoid errors during multipart encoding process
        'message': json.dumps({
            'attachment': {
                'type': 'image',
                'payload': {}
            }
        }),
        'filedata': (os.path.basename(message_text), open(message_text, 'rb'), 'image/png')
    }

    # multipart encode the entire payload
    multipart_data = MultipartEncoder(data)

    # multipart header from multipart_data
    multipart_header = {
        'Content-Type': multipart_data.content_type
    }
    r = requests.post("https://graph.facebook.com/v12.0/me/messages",
                      params=params, headers=multipart_header, data=multipart_data)
    if r.status_code != 200:
        print(r.status_code)
        print(r.text)


def get_photo_facebook(id):
    params = {
        "access_token": 'EAACNi6PriH4BAHx71ZCuZADZCVWQ0v4ZABJt4IpEN36LCmdYRbYta5oVjcBel7bwiZBV2QU6EN1y0LywjNiHKYAvcOsWslUzJL8ZAuLZAVgP4GNRZCMCZBLw54alXAfsnwVxlHZCnQxY1Qkp8088HiMuBTeecFKrvqJSxlwsXvlH59iKCR9H9EVhFYjWV1yNt8BS4pO8b4CH781QP8ClSB7r33',
    }
    r = requests.get(
        f"https://graph.facebook.com/v12.0/{id}",params=params)
    print(r.status_code)
    print(r.text)

# get_photo_facebook(4327063214039376)

# get_facebook_live('405370274427849')
# send_message("4368040723287885",'media/image.png')

def copy(source,dest):
    db.query_commit(f'create database if not exists {dest}')
    metadata = MetaData()
    db1 = sqlalchemy.create_engine(f"mysql+pymysql://{userdb}:{passworddb}@{hostdb}/{source}")
    db2 = sqlalchemy.create_engine(f"mysql+pymysql://{userdb}:{passworddb}@{hostdb}/{dest}")
    result = db.query(f"show tables from {source}")
    result = list(result.fetchall())
    for i in result:
        table = sqlalchemy.Table(i[0],metadata,autoload=True, autoload_with=db1)
        table.create(db2,checkfirst=True)

# copy('muslin','maruay')
def get_database():
    result = db.query('show databases')
    result = list(result.fetchall())
    return [i[0] for i in result if i[0] not in ['information_schema', 'mysql', 'performance_schema','sys','image'] ]


# update_size("7KRzYzjPqknzzSM2nVcooo3sWNF6EK4Oyq9QtGI8uyk=","RA9VD1AjwaHo8UW0uNk924SnxN0xIFIGdlelDEcTEE=","Muslin.info@gmail.com")
string = '1234'
print(string[:2])
print(string[2:])