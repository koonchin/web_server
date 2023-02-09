import datetime
from io import BytesIO
import json,random,string
import time
from sqlalchemy import create_engine
import mysql.connector
import pandas as pd
import requests
import sqlalchemy
from pandas.api.types import CategoricalDtype
from PIL import Image, ImageDraw, ImageFont,ImageOps
from requests_toolbelt import MultipartEncoder
from sqlalchemy.sql.schema import MetaData
from server import cancelLoadpath,runLoadpath
from source import *
from collections import Counter
from django.conf import settings

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
    def query_with_image(self,query,args):
        self.connect()
        cursor = self.mydb.cursor(buffered=True)
        result = cursor.execute(
        query, args)
    # Committing the data
        self.mydb.commit()

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
    
    def check(self,task,db='muslin'):
        try:
            self.connect(dbname=db)
            mycursor = self.mydb.cursor(buffered=True)
            mycursor.execute(task)
        except:
            self.connect(dbname=db)
            mycursor = self.mydb.cursor(buffered=True)
            mycursor.execute(task)
        
        return mycursor.fetchall()

    def query_custom(self, task,db):
        try:
            self.connect(dbname=db)
            mycursor = self.mydb.cursor(buffered=True)
            mycursor.execute(task)
        except:
            self.connect(dbname=db)
            mycursor = self.mydb.cursor(buffered=True)
            mycursor.execute(task)
        
        return mycursor

    def query_commit(self, task):
        try:
            self.connect()
            mycursor = self.mydb.cursor(buffered=True)
            mycursor.execute(task)
            self.mydb.commit()
        except:
            self.connect()
            mycursor = self.mydb.cursor(buffered=True)
            mycursor.execute(task)
            self.mydb.commit()
        return mycursor

    def query_commit_many(self, task,rows):
        try:
            self.connect()
            mycursor = self.mydb.cursor(buffered=True)
            mycursor.executemany(task,rows)
            self.mydb.commit()
        except:
            self.connect()
            mycursor = self.mydb.cursor(buffered=True)
            mycursor.executemany(task,rows)
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
        # 

    def insert_into_duplicate(self,dbname,data,amount):
        task = f"""
        INSERT INTO {dbname}(sku, descript, amount)
        VALUES ({data})
        ON DUPLICATE KEY UPDATE amount = {amount};  
        """
        # db.query_commit(task)
db = DB()

def add(sku, user):
    dep = get_role(user,"department")
    task_db = f'insert into {dep}.live_room values ("{sku}",NULL)'
    db.query_commit(task_db)
    web = Web(get_api_register(dep,'apikey'),get_api_register(dep,'apisecret'),get_api_register(dep,'storename'))
    
    amount = f"select stock_main.amount from {dep}.stock_main where stock_main.sku = '{sku}'"
    amount = db.query(amount)
    amount = list(amount.fetchall())[0][0]
    amount = int(amount)
    if amount >= 1:
        web.post("UPDATEPRODUCTAVAILABLESTOCKLIST",sku,amount - 1 )
        db.query_commit(f"update {dep}.stock_main set amount = amount - 1 where sku = '{sku}'")
    else:
        db.query_commit(f"update {dep}.stock set amount = amount - 1 where sku = '{sku}'")
    db.query_commit(f"insert into {dep}.log values ('{user}','เพิ่มเข้าสต็อกห้องไลฟ์ รหัส {sku}',now())")
        
def delete(sku, user):
    dep = get_role(user,"department")
    web = Web(get_api_register(dep,'apikey'),get_api_register(dep,'apisecret'),get_api_register(dep,'storename'))
    amount = f"select stock_main.amount from {dep}.stock_main where stock_main.sku = '{sku}'"
    amount = db.query(amount)
    amount = list(amount.fetchall())[0][0]
    amount = int(amount)
    web.post("UPDATEPRODUCTAVAILABLESTOCKLIST",sku,amount + 1 )
    db.query_commit(f"update {dep}.stock_main set amount = amount + 1 where sku = '{sku}'")

    task_db = f'delete from {dep}.live_room where sku = "{sku}"'
    db.query_commit(task_db)

    db.query_commit(f"insert into {dep}.log values ('{user}','ลบสต็อกห้องไลฟ์ รหัส {sku}',now())")
    # send_line(f"รหัส {sku} เอาออกโดย {user}")
    if '-' in sku:
        sku = sku.split('-')[0]
    task_db = f"select stock_main.size from {dep}.stock_main\
    inner join {dep}.stock on {dep}.stock_main.sku = {dep}.stock.sku\
    where stock_main.amount + stock.amount > 0 and {dep}.stock_main.sku like '%{sku}%'\
    ORDER BY FIELD(stock_main.size, 'XXS', 'XS', 'S', 'M', 'L', 'F', 'XL', '2XL','3XL'), {dep}.stock_main.size"
    mycursor = db.query(task_db)
    myresult = list(mycursor.fetchall())
    if not len(myresult) == 0:
        return myresult[0][0]
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
    token = 'qGjBCv5oFvqb9IKNM05puRYhwDz0X3vAr6bs9y1Kvp8'
    headers = {'content-type': 'application/x-www-form-urlencoded',
               'Authorization': 'Bearer '+token}
    r = requests.post(url, headers=headers, data={'message': msg})

def send_line_adjust(msg):
    url = 'https://notify-api.line.me/api/notify'
    token = 'AyfLcJAM8h5IdNuxGUPqVfcFuS8Lt2dK6jCzKrPLIcW'
    headers = {'content-type': 'application/x-www-form-urlencoded',
               'Authorization': 'Bearer '+token}
    r = requests.post(url, headers=headers, data={'message': msg})

def send_line_return(msg):
    url = 'https://notify-api.line.me/api/notify'
    token = 'MMHcMhda3sy1ilLdq5FkDOyNNyp6HubLYNcInlq8ULx'
    headers = {'content-type': 'application/x-www-form-urlencoded',
               'Authorization': 'Bearer '+token}
    r = requests.post(url, headers=headers, data={'message': msg})

class Web():
    def __init__(self, apikey, apisecret, storename) -> None:
        self.apikey = apikey
        self.apisecret = apisecret
        self.storename = storename

    #  upload trackingno today to database
    def post_order(self,data):
        header = {
            'storename': f'{self.storename}',
            'apikey': f'{self.apikey}',
            'apisecret': f'{self.apisecret}'
        }

        url = 'https://api.zortout.com/api.aspx'

        payload = {'method': "ADDORDER", 'version': '3'}
        
        res = requests.post(url=url, headers=header, params=payload, json=data)
        print(res.status_code)

    def update_payment(self,number,paymentmethod,paymentamount):
        header = {
            'storename': f'{self.storename}',
            'apikey': f'{self.apikey}',
            'apisecret': f'{self.apisecret}'
        }

        url = 'https://api.zortout.com/api.aspx'

        payload = {'method': "UPDATEORDERPAYMENT", 'version': '3','number':number,'paymentmethod':paymentmethod,'paymentamount':paymentamount}
        
        res = requests.post(url=url, headers=header, params=payload)
        print(res.status_code)

    def update_order_status(self,number):
        header = {
            'storename': f'{self.storename}',
            'apikey': f'{self.apikey}',
            'apisecret': f'{self.apisecret}'
        }

        url = 'https://api.zortout.com/api.aspx'

        payload = {'method': "UPDATEORDERSTATUS", 'version': '3','number':number,'status':1}
        
        res = requests.post(url=url, headers=header, params=payload)
        print(number,res.status_code)

    def VOIDORDERPAYMENT(self,number,paymentid):
        header = {
            'storename': f'{self.storename}',
            'apikey': f'{self.apikey}',
            'apisecret': f'{self.apisecret}'
        }

        url = 'https://api.zortout.com/api.aspx'

        payload = {'method': "VOIDORDERPAYMENT", 'version': '3','number':number,'paymentid':paymentid}
        
        res = requests.post(url=url, headers=header, params=payload)
        print(number,res.content)
        
    def update_fee(self):
        header = {
            'storename': f'{self.storename}',
            'apikey': f'{self.apikey}',
            'apisecret': f'{self.apisecret}'
        }

        url = 'https://api.zortout.com/api.aspx'
        day = datetime.datetime.now() - datetime.timedelta(days = 4)
        day = day.strftime('%Y-%m-%d')
        for i in range(20):
            payload = {'method': "GETORDERS", 'version': '3','status':"0",'orderdatebefore':day,'page':i}
            res = requests.get(url=url, headers=header, params=payload)
            data = res.json()
            for customer in data['list']:
                for info in customer['list']:
                    if 'FEE' in info['sku'].upper():
                        self.update_order_status(customer['number'])
    def update_Payment(self):
        header = {
            'storename': f'{self.storename}',
            'apikey': f'{self.apikey}',
            'apisecret': f'{self.apisecret}'
        }

        url = 'https://api.zortout.com/api.aspx'
        day = datetime.datetime.now() - datetime.timedelta(days = 60)
        day = day.strftime('%Y-%m-%d')
        for i in range(20):
            payload = {'method': "GETORDERS", 'version': '3','paymentstatus':"0,3,4",'orderdateafter':day,'page':i}
            res = requests.get(url=url, headers=header, params=payload)
            data = res.json()
            for customer in data['list']:
                if 'COD' not in customer['shippingchannel']:
                    for info in customer['payments']:
                            self.VOIDORDERPAYMENT(customer['number'],info['id'])
                        # print(customer['number'])
                    self.update_payment(customer['number'],'โอนผ่านธนาคาร',int(customer['amount']))

    def updateproduct(self,sku,sellprice):
        header = {
            'storename': f'{self.storename}',
            'apikey': f'{self.apikey}',
            'apisecret': f'{self.apisecret}'
        }

        url = 'https://api.zortout.com/api.aspx'

        payload = {'method': "UPDATEPRODUCT", 'version': '3'}
        data = {'sku':sku,'sellprice':f"{sellprice}",'barcode':sku}
        res = requests.post(url=url, headers=header, params=payload, json=data)
        print(sku,res.status_code)

    def updatebarcode(self,sku):
        header = {
            'storename': f'{self.storename}',
            'apikey': f'{self.apikey}',
            'apisecret': f'{self.apisecret}'
        }

        url = 'https://api.zortout.com/api.aspx'

        payload = {'method': "UPDATEPRODUCT", 'version': '3'}
        data = {'sku':sku,'barcode':sku}
        res = requests.post(url=url, headers=header, params=payload, json=data)
        print(sku,res.status_code)
        
    def updateproductName(self,sku,name):
        header = {
            'storename': f'{self.storename}',
            'apikey': f'{self.apikey}',
            'apisecret': f'{self.apisecret}'
        }

        url = 'https://api.zortout.com/api.aspx'

        payload = {'method': "UPDATEPRODUCT", 'version': '3'}
        data = {'sku':sku,'name':name}
        res = requests.post(url=url, headers=header, params=payload, json=data)
        print(name,res.status_code)

    def post_purchase_order(self,data):
        header = {
            'storename': f'{self.storename}',
            'apikey': f'{self.apikey}',
            'apisecret': f'{self.apisecret}'
        }

        url = 'https://api.zortout.com/api.aspx'

        payload = {'method': "ADDPURCHASEORDER", 'version': '3'}

        res = requests.post(url=url, headers=header, params=payload, json=data)
        print(res.status_code)

    def get_track_chino(self,dep):
        header = {
            'storename': f'{self.storename}',
            'apikey': f'{self.apikey}',
            'apisecret': f'{self.apisecret}'
        }

        url = 'https://api.zortout.com/api.aspx'
        day = datetime.datetime.now() - datetime.timedelta(days = 1)
        payload = {'method': "GETORDERS", 'version': '3','orderdateafter':day.strftime('%Y-%m-%d')}

        res = requests.get(url=url, headers=header, params=payload)
        data = res.json()
        count = 0 
        sku_list = []
        for i in range(len(data['list'])):
            if data['list'][i]['status'] == 'Success':
                if data['list'][i]['amount'] > 0:
                            for sku in data['list'][i]['list']:
                                sku_list.append(sku['sku'])
        return sku_list
    def get_track(self,dep):
        def check(idorder):
            try:
                result = db.query(f"select * from {dep}.deli_zort where idorder = {idorder}")
                result = list(result.fetchall())
                return result
            except Exception as e:
                print(e)
            return False

        header = {
            'storename': f'{self.storename}',
            'apikey': f'{self.apikey}',
            'apisecret': f'{self.apisecret}'
        }

        url = 'https://api.zortout.com/api.aspx'
        day = datetime.datetime.now() - datetime.timedelta(days = 40)
        payload = {'method': "GETORDERS", 'version': '3','orderdateafter':day.strftime('%Y-%m-%d')}

        res = requests.get(url=url, headers=header, params=payload)
        data = res.json()
        count = 0 
        for i in range(len(data['list'])):
            if data['list'][i]['status'] == 'Waiting':
                trackingno = data['list'][i]['trackingno']
                IDorder = data['list'][i]['id']
                if check(IDorder):
                    db.query_commit(f"update {dep}.deli_zort set trackingno ='{trackingno}',printed = 1,printedtime = now() ,status = '{data['list'][i]['status']}'\
                        where idorder = {IDorder}")
                    count += 1
        return count

    def update_cost(self,pages):
        header = {
            'storename': f'{self.storename}',
            'apikey': f'{self.apikey}',
            'apisecret': f'{self.apisecret}'
        }
        dep = 'maruay'
        url = 'https://api.zortout.com/api.aspx'
        payload = {'method': "GETPRODUCTS", 'version': '3','page':pages,'warehousecode':"W0001"}

        res = requests.get(url=url, headers=header, params=payload)
        data = res.json()
        count = 0 
        for i in range(len(data['list'])):
            cost = data['list'][i]['purchaseprice']
            price = data['list'][i]['sellprice']
            sku = data['list'][i]['sku']
            
            task = f"""insert into {dep}.cost
            values ('{sku}',{cost},1,{price});\n"""
            with open ("sql.txt","a",encoding="utf-8") as f:
                f.write(task)
    def get_track_2(self,pages):
        dep = 'muslin'
        result = db.query(f"select idorder from {dep}.deli_zort")
        result = list(result.fetchall())
        idorder = [i[0] for i in result]

        result = db.query(f"select idorder from {dep}.order_main")
        result = list(result.fetchall())
        idorder_ordermain = [i[0] for i in result]

        def check(id,status,shipping,track,pay,number,cstname,orderdate,addr,tel):
            if id in idorder:
                return ""
                if not shipping:
                    task = f"update {dep}.deli_zort set status = '{status}',trackingno='{track}',paymentstatus='{pay}' ,tel='{tel}',addr = '{addr}'where idorder = {id};"
                else:
                    task = f"update {dep}.deli_zort set status = '{status}',trackingno = '{track}',paymentstatus='{pay}' ,tel='{tel}',addr = '{addr}'where idorder = {id};"
            else:
                task = f"""insert into {dep}.deli_zort
                values ('{id}','{number}','{status}','{cstname}','{orderdate}','',0,NULL,NULL,'{pay}',"{addr}",'{tel}');\n"""
                with open ("sql.txt","a",encoding="utf-8") as f:
                    f.write(task)


            # db.query_commit(task)
        header = {
            'storename': f'{self.storename}',
            'apikey': f'{self.apikey}',
            'apisecret': f'{self.apisecret}',
        }

        url = 'https://api.zortout.com/api.aspx'
        day = datetime.datetime.now() - datetime.timedelta(days = 90)
        # day1 = datetime.datetime.now() - datetime.timedelta(days = 2)
        payload = {'method': "GETORDERS", 'version': '3','orderdateafter':day.strftime('%Y-%m-%d'),'page':pages}
        # payload = {'method': "GETORDERS", 'version': '3','orderdateafter':"2024-03-31"}
        # payload = {'method': "GETORDERS", 'version': '3'}

        res = requests.get(url=url, headers=header, params=payload)
        data = res.json()
        # for i in range(len(data['list'])):
        #     if data['list'][i]['status'] == 'Pending':
        #         if data['list'][i]['paymentstatus'] == "Paid":
        #             IDorder = data['list'][i]['number']
    #             print(IDorder)
        for i in range(len(data['list'])):
            if data['list'][i]['amount'] > 0:
                if '"' in data['list'][i]['shippingaddress'] or "'" in data['list'][i]['shippingaddress']:
                    data['list'][i]['shippingaddress'] = data['list'][i]['shippingaddress'].replace('"','')
                    data['list'][i]['shippingaddress'] = data['list'][i]['shippingaddress'].replace("'",'')
                check(data['list'][i]['id'],data['list'][i]['status'],data['list'][i]['shippingdateString'],data['list'][i]['trackingno'],data['list'][i]['paymentstatus'],data['list'][i]['number'],data['list'][i]['customername'],data['list'][i]['orderdateString'],data['list'][i]['shippingaddress'],data['list'][i]['shippingphone'])
                for sku in data['list'][i]['list']:
                    if data['list'][i]['id'] not in idorder_ordermain:
                        task = f"insert into {dep}.order_main values ('{data['list'][i]['id']}','{sku['pricepernumber']}','{sku['sku']}','{data['list'][i]['amount']}','{sku['number']}');\n"
                        with open ("sql.txt","a",encoding="utf-8") as f:
                            f.write(task)
                        # db.query_commit(f"insert into {dep}.order_main values ('{data['list'][i]['id']}','{sku['pricepernumber']}','{sku['sku']}','{data['list'][i]['amount']}','{sku['number']}')")
                    

    def get_track_success(self):
        header = {
            'storename': f'{self.storename}',
            'apikey': f'{self.apikey}',
            'apisecret': f'{self.apisecret}'
        }

        url = 'https://api.zortout.com/api.aspx'

        payload = {'method': "GETORDERS", 'version': '3',"createdafter":"2021-11-01"}

        res = requests.get(url=url, headers=header, params=payload)
        data = res.json()

        for i in range(len(data['list'])):
            if data['list'][i]['status'] == 'Success':
                trackingno = data['list'][i]['trackingno']
                if trackingno:
                    IDorder = data['list'][i]['id']
                    date = data['list'][i]['createdatetimeString']
                    FBname = data['list'][i]['reference']
                    cstname = data['list'][i]['customername']
                    addr = data['list'][i]['customeraddress']
                    tel = data['list'][i]['customerphone']
                    amount = len(data['list'][i]['list'])
                    paid = data['list'][i]['paymentamount']
                    total = data['list'][i]['amount']
                    descript = [data['list'][i]['list'][i2]['sku'] for i2 in range(amount)]
                    price = [data['list'][i]['list'][i2]['totalprice'] for i2 in range(amount)]
                    status = 'packed'
                    result = db.query(f"select idorder from muslin.order_main where idorder = '{IDorder}'")
                    result = list(result.fetchall())
                    if not result:
                        now = time.strftime('%Y-%m-%d %H:%M:%S')
                        for i3 in range(amount):
                            print(IDorder)
                            try:
                                task =f"""
                                insert into muslin.order_main
                                values ('{IDorder}', '{date}', '{FBname}', '{cstname}', '{addr}', '{tel}', '{trackingno}', '{amount}', '{total}', '{paid}', "{now}", '{descript[i3]}', 'Zort', '{price[i3]}', '{status}')"""
                                db.query_commit(task)
                            except Exception as e:
                                print(e,IDorder)
                # for dt in range(len(data['list'][i]['list'])):
                #     sku = data['list'][i]['list'][dt]['sku']
                #     descript = data['list'][i]['list'][dt]['name']
    # get data from list of www.api.zort.com
    #  upload trackingno today to database
    def get_track_data(self,idorder,trackingNo):
        header = {
            'storename': f'{self.storename}',
            'apikey': f'{self.apikey}',
            'apisecret': f'{self.apisecret}'
        }

        url = 'https://api.zortout.com/api.aspx'

        payload = {'method': "GETORDERDETAIL", 'version': '3','id':idorder}

        res = requests.get(url=url, headers=header, params=payload)
        data = res.json()
        date = data['createdatetimeString']
        FBname = data['reference']
        cstname = data['customername']
        addr = data['customeraddress']
        tel = data['customerphone']
        amount = len(data['list'])
        paid = data['paymentamount']
        total = data['amount']
        descript = [data['list'][i]['name'] for i in range(amount)]
        price = [data['list'][i]['totalprice'] for i in range(amount)]
        status = 'packed'
        return idorder, date, FBname, cstname, addr, tel, trackingNo, amount, total, paid, 'now()', descript, 'Zort', price, status
    # get data from list of www.api.zort.com

    def get(self, datatype, page=1):
        header = {
            'storename': f'{self.storename}',
            'apikey': f'{self.apikey}',
            'apisecret': f'{self.apisecret}'
        }

        url = 'https://api.zortout.com/api.aspx'

        payload = {'method': "GETPRODUCTS", 'version': '3',
                   'page': page}
        res = requests.get(url=url, headers=header, params=payload)
        data = res.json()
        for i in range(len(data['list'])):
            if data['list'][i]['number'][:2] == 'SO' and data['list'][i]['status'] != 'Voided' and data['list'][i][''] != 'Excess Payment':
                number.append(data['list'][i]['number'])
                datalist.append(data['list'][i]['list'])
                status.append(data['list'][i]['status'])
        return number,status,datalist

    def get_order_shopee(self, page=1):
        header = {
            'storename': f'{self.storename}',
            'apikey': f'{self.apikey}',
            'apisecret': f'{self.apisecret}'
        }

        task = """select idorder from muslin.deli_zort
        where shippingtime = '2021-12-17'"""
        result = db.query(task)
        result = list(result.fetchall())
        result = [i[0] for i in result]

        url = 'https://api.zortout.com/api.aspx'

        payload = {'method': "GETORDERS", 'version': '3',
                   'page': page}
        res = requests.get(url=url, headers=header, params=payload)
        data = res.json()
        number = []
        for i in range(len(data['list'])):
            if data['list'][i]['id'] in result:
                number.append(data['list'][i]['list'])
        return number

    def post_zero(self, page=1,dep='muslin'):

        header = {
            'storename': f'{self.storename}',
            'apikey': f'{self.apikey}',
            'apisecret': f'{self.apisecret}'
        }

        url = 'https://api.zortout.com/api.aspx'

        payload = {'method': "GETPRODUCTS", 'version': '3',
                    'page': page}

        res = requests.get(url=url, headers=header, params=payload)
        data = res.json()
        datadict = {}
        datadict['stocks'] = list()
        taskdb_stock = ''
        for i in range(len(data['list'])):
            if i % 200 == 0:
                self.postzero(datadict)
                datadict['stocks'] = list()
                print("{:.2f} %".format(i / len(data['list']) * 100))
            if int(data['list'][i]['stock']) != 0 and 'Q' not in data['list'][i]['sku']:
                datadict['stocks'].append({"sku": data['list'][i]['sku'], "stock": 0,'cost':0})
                # self.post("UPDATEPRODUCTSTOCKLIST",data['list'][i]['sku'],0)
            if int(data['list'][i]['availablestock']) < 0:
                taskdb_stock += f"WHEN '{data['list'][i]['sku']}' THEN {int(data['list'][i]['availablestock'])}\n"   
        self.postzero(datadict)
        return taskdb_stock

    def get_condition_2(self,  page=1):
        header = {
            'storename': f'{self.storename}',
            'apikey': f'{self.apikey}',
            'apisecret': f'{self.apisecret}'
        }

        url = 'https://api.zortout.com/api.aspx'

        payload = {'method': "GETORDERS", "orderdatebefore":"2022-02-04",'version': '3',
                   'page': page}

        res = requests.get(url=url, headers=header, params=payload)
        data = res.json()
        datalist = []
        for i in range(len(data['list'])):
            if data['list'][i]['status'] != "Success":
                if  data['list'][i]['status'] != "Voided":
                    print(data['list'][i]['number'])
                    for sku in data['list'][i]['list']:
                       self.post("UPDATEPRODUCTAVAILABLESTOCKLIST",sku['sku'],int(sku['number']))
                    self.post_status_order(data['list'][i]["id"])
        return datalist

    def get_datatype_filter_by_sku(self,dep,page):
        task = f'select sku,cost from cost'
        result = db.query_custom(task,dep)
        result = list(result.fetchall())
        cost = {}
        for i in result:
            cost[i[0]] = int(i[1])

        header = {
            'storename': f'{self.storename}',
            'apikey': f'{self.apikey}',
            'apisecret': f'{self.apisecret}'
        }

        url = 'https://api.zortout.com/api.aspx'

        payload = {'method': "GETPRODUCTS", 'version': '3','page':page}

        res = requests.get(url=url, headers=header, params=payload)
        data = res.json()
        for i in range(len(data["list"])):
            sku = data['list'][i]['sku']
            if 'Q' in sku:
                continue
            try:
                if cost[sku] == 0 and float(data['list'][i]['purchaseprice']) != 0:
                    print(sku)
                if cost[sku] != 0 and float(data['list'][i]['purchaseprice']) == 0:
                    print(sku)
            except Exception as E:
                print(E,sku)
    # post data to www.api.zort.com

    def post_status_order(self, id):

        header = {
            'storename': f'{self.storename}',
            'apikey': f'{self.apikey}',
            'apisecret': f'{self.apisecret}'
        }

        url = 'https://api.zortout.com/api.aspx'

        payload = {'method': "UPDATEORDERSTATUS", 'version': '3', 'warehousecode': 'W0001',"id":int(id)}
        res = requests.post(url=url, headers=header, params=payload)
        print(res.status_code)

    def post(self, method, sku, amount,cost=0):

        header = {
            'storename': f'{self.storename}',
            'apikey': f'{self.apikey}',
            'apisecret': f'{self.apisecret}'
        }

        url = 'https://api.zortout.com/api.aspx'

        payload = {'method': method, 'version': '3', 'warehousecode': 'W0001'}
        data = {"stocks": [{"sku": f"{sku}", "stock": amount,'cost':cost}]}
        res = requests.post(url=url, headers=header, params=payload, json=data)
        # for i in range(len(data['list'])):
        #     print(data['list'][i]['customerphone'])

    def postzero(self,data):
        # example
        # data = {"stocks": [{"sku": "BA0002-S", "stock": 0,'cost':0},{"sku": "BA0002-L", "stock": 0,'cost':0},{"sku": "BA0002-M", "stock": 0,'cost':0}]}
        header = {
            'storename': f'{self.storename}',
            'apikey': f'{self.apikey}',
            'apisecret': f'{self.apisecret}'
        }

        url = 'https://api.zortout.com/api.aspx'

        payload = {'method': 'UPDATEPRODUCTSTOCKLIST', 'version': '3', 'warehousecode': 'W0001'}
        res = requests.post(url=url, headers=header, params=payload, json=data)
        # print(res.status_code)
        # print(json.loads(res.text)['resDesc'])

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

    def update_track(self, idorder):
        header = {
            'storename': f'{self.storename}',
            'apikey': f'{self.apikey}',
            'apisecret': f'{self.apisecret}'
        }

        url = 'https://api.zortout.com/api.aspx'

        payload = {'method': "UPDATEORDERPAYMENT", 'version': '3', 'number': f"{idorder}",'paymentamount':0.1,"paymentmethod":"โอนผ่านธนาคาร"}
        res = requests.post(url=url, headers=header, params=payload)
        print(res.status_code)
        print(res.content)
        # for i in range(len(data['list'])):
        #     print(data['list'][i]['customerphone'])

def update_size(apikey,apisecret,storename):
    web =Web(apikey,apisecret,storename)
    df = pd.read_excel(r"C:\Users\Chino\Desktop\diff.xlsx")
    for i in df.index:
        if  not str(df.loc[i,"SIZE"]) == 'nan':
            web.post_descript("UPDATEPRODUCT",str(df.loc[i,'SKU']),str(df.loc[i,'SIZE']))
    
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

def export_excel_vrichform_(less, greate, path):
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
    result2 = db.query(f"show tables from {dest}")
    result2 = list(result2.fetchall())
    for i in result:
        if i not in result2:
            table = sqlalchemy.Table(i[0],metadata,autoload=True, autoload_with=db1)
            table.create(db2,checkfirst=True)

# copy('muslin','maruay')
def get_database():
    result = db.query('show databases')
    result = list(result.fetchall())
    return [i[0] for i in result if i[0] not in ['information_schema', 'mysql', 'performance_schema','sys','image'] ]

# string = '1234'
# print(string[:2])
# print(string[2:])

def get_idsell(string:str):
    try:
        char = string.split('-')[0].split('0')[0]
        if 'q' in char.lower():
            return ''
        try:
            number = int(string.split('-')[0].split(char)[1])
        except Exception as e:
            return (f'error at {string} cuz {e}')
        if len(char) > 1:
            char = char[-1]
        return char + str(number)
    except:
        print('error at ',string)
        return string
def get_idsell_for_qc(string:str):
    try:
        char = string.split('-')[0].split('0')[0]
        size = string.split('-')[1]
        try:
            number = int(string.split('-')[0].split(char)[1])
        except Exception as e:
            return (f'error at {string} cuz {e}')
        if len(char) > 1:
            char = char[-1]
        return char + str(number),size
    except:
        print('error at ',string)
        return string,size

def diff_day(d1, d2):
    """
        datetime(2010,10,1), datetime(2010,9,1)
    """
    return ((d1.year - d2.year) * 12 + d1.month - d2.month) * 30 + d1.day - d2.day

def write_image(imgpath,title_text):
    basewidth = 980
    my_image = Image.open(imgpath)
    if my_image.mode != 'RGB':
        my_image = my_image.convert("RGB")
    width, height = my_image.size
    width = int(width/height*basewidth)
    my_image = my_image.resize((width,basewidth), Image.ANTIALIAS)
    
    x, y = width*65/100,basewidth*10/100

    shadowcolor = "white"
    fillcolor = 'red'

    title_font = ImageFont.truetype(f'{settings.MEDIA_ROOT}/luxury_thai.ttf', 50)
    image_editable = ImageDraw.Draw(my_image)

    # image_editable.text((1000,15), title_text, (0, 0, 0),font=title_font)
    image_editable.text((x-1.5, y-1.5), title_text, font=title_font, fill=shadowcolor)
    image_editable.text((x+1.5, y-1.5), title_text, font=title_font, fill=shadowcolor)
    image_editable.text((x-1.5, y+1.5), title_text, font=title_font, fill=shadowcolor)
    image_editable.text((x+1.5, y+1.5), title_text, font=title_font, fill=shadowcolor)

    image_editable.text((x, y), title_text, font=title_font, fill=fillcolor)
    my_image.save(imgpath)

def write_image2(imgpath,imgpath2):
    my_image = Image.open(imgpath)
    width, height = my_image.size
    basewidth = int(height*1)
    width = int(width/height*basewidth)
    my_image = my_image.resize((width,basewidth), Image.ANTIALIAS)
    
    my_image.save(imgpath2)

def write_image_top_right(imgpath,title_text):
    basewidth = 800
    my_image = Image.open(imgpath)
 
    pil = ImageOps.exif_transpose(my_image)
    # ------------ crop -------------------------------

    # left = 0
    # # top = height / 5
    # # right = width
    # top = 400
    # right = 1080
    # bottom = 1480
    # my_image = my_image.crop((left, top, right, bottom))

    # ------------ crop -------------------------------
    width, height = pil.size
    # width2 = int(width/height*basewidth)

    # my_image = my_image.resize((width,basewidth), Image.ANTIALIAS)
    
    # x, y = width*75/100,basewidth*.5/100
    LEN = 85 - len(title_text)*5
    x, y = width*LEN/100,height*.5/100

    shadowcolor = "black"
    fillcolor = 'white'
    print(width,height)
    title_font = ImageFont.truetype(f'{settings.MEDIA_ROOT}/luxury2.ttf',int(width/7.6))
    image_editable = ImageDraw.Draw(pil)
    # image_editable.text((1000,15), title_text, (0, 0, 0),font=title_font)
    image_editable.text((x-int(width/7.6/40.66), y-int(width/7.6/40.66)), title_text, font=title_font, fill=shadowcolor)
    image_editable.text((x+int(width/7.6/40.66), y-int(width/7.6/40.66)), title_text, font=title_font, fill=shadowcolor)
    image_editable.text((x-int(width/7.6/40.66), y+int(width/7.6/40.66)), title_text, font=title_font, fill=shadowcolor)
    image_editable.text((x+int(width/7.6/40.66), y+int(width/7.6/40.66)), title_text, font=title_font, fill=shadowcolor)

    image_editable.text((x, y), title_text, font=title_font, fill=fillcolor)

    pil.save(imgpath,quality=100)

def crop(imgpath):
    my_image = Image.open(imgpath)
    width, height = my_image.size
    # ------------ crop -------------------------------

    left = int(width/2)
    # top = height / 5
    # right = width
    top = 0
    right = width
    bottom = int(height/5)
    my_image = my_image.crop((left, top, right, bottom))

    # ------------ crop -------------------------------
    my_image.save(imgpath,quality=100)

def write_image_top_right2(imgpath,title_text):
    my_image = Image.open(imgpath)

    width, height = my_image.size

    x, y = width*55/100,height*.5/100

    shadowcolor = "black"
    fillcolor = 'white'

    title_font = ImageFont.truetype(f'{settings.MEDIA_ROOT}/luxury2.ttf', int(width/20))
    image_editable = ImageDraw.Draw(my_image)
    # image_editable.text((1000,15), title_text, (0, 0, 0),font=title_font)
    image_editable.text((x-1.5, y-1.5), title_text, font=title_font, fill=shadowcolor)
    image_editable.text((x+1.5, y-1.5), title_text, font=title_font, fill=shadowcolor)
    image_editable.text((x-1.5, y+1.5), title_text, font=title_font, fill=shadowcolor)
    image_editable.text((x+1.5, y+1.5), title_text, font=title_font, fill=shadowcolor)

    image_editable.text((x, y), title_text, font=title_font, fill=fillcolor)
    try:
        my_image.save(imgpath,quality=100)
    except:
        print(imgpath)

web = Web("7KRzYzjPqknzzSM2nVcooo3sWNF6EK4Oyq9QtGI8uyk=","RA9VD1AjwaHo8UW0uNk924SnxN0xIFIGdlelDEcTEE=","Muslin.info@gmail.com")
# web = Web("pteRXLvqBNcUXlgIB3RDHxBn3vXoi9cwRp6u/v9M=","GbJK2j7YS5dJtVaBomSsdyenjYuEwdI2A4gLPbKrRAI=","Maruay18.co.th@gmail.com")
# web.update_Payment()
# web.update_fee()
def write_image_all():
    web = Web("7KRzYzjPqknzzSM2nVcooo3sWNF6EK4Oyq9QtGI8uyk=","RA9VD1AjwaHo8UW0uNk924SnxN0xIFIGdlelDEcTEE=","Muslin.info@gmail.com")
    # web.get_purchasedorder()
    imagepath = web.get("GETPRODUCTS",'imagepath','')
    sku = web.get("GETPRODUCTS",'sku','')

    sku_list = []

    for i in range(len(sku)):
        if imagepath[i]:
            if not get_idsell(sku[i]) in sku_list:
                sku_list.append(get_idsell(sku[i]))
                with open(f'image/{get_idsell(sku[i])}.jpg','wb') as f:
                    f.write(convert_url_to_bytes(imagepath[i]))
                write_image(f'image/{get_idsell(sku[i])}.jpg',get_idsell(sku[i]))

    imagepath = web.get("GETPRODUCTS",'imagepath','',2)
    sku = web.get("GETPRODUCTS",'sku','',2)

    for i in range(len(sku)):
        if imagepath[i]:
            if not get_idsell(sku[i]) in sku_list:
                sku_list.append(get_idsell(sku[i]))
                with open(f'image/{get_idsell(sku[i])}.jpg','wb') as f:
                    f.write(convert_url_to_bytes(imagepath[i]))
                write_image(f'image/{get_idsell(sku[i])}.jpg',get_idsell(sku[i]))

def concat_someColumn_by_group():
    web = Web("7KRzYzjPqknzzSM2nVcooo3sWNF6EK4Oyq9QtGI8uyk=","RA9VD1AjwaHo8UW0uNk924SnxN0xIFIGdlelDEcTEE=","Muslin.info@gmail.com")
    sku = web.get("GETPRODUCTS",'sku','')
    description = web.get("GETPRODUCTS",'description','')
    sku2 = web.get("GETPRODUCTS",'sku','',2)
    description2 = web.get("GETPRODUCTS",'description','',2)

    sku.extend(sku2)
    description.extend(description2)
    data = list(zip(sku,description))

    df = pd.DataFrame(data,columns=['SKU','description'])
    size_order = CategoricalDtype(
    ['F','XS', 'S', 'M', 'L', 'XL','2XL','3XL'], 
    ordered=True)

    df = df[df['description'] != '']
    df = df[~df["SKU"].str.contains('Q')]
    df.to_excel("V1.xlsx")
    df['Size'] = df['SKU'].apply(lambda x: x.split('-')[1])
    df['Size'] = df['Size'].astype(size_order)
    df = df.sort_values('Size')
    df['IDSell'] = df['SKU'].apply(lambda x:get_idsell(x))
    df = df[df['IDSell'].duplicated(keep=False)]
    df['DataSized'] = df.groupby('IDSell')['description'].transform(lambda x: '\n'.join(x))
    df.to_excel("V2.xlsx",header=True,index=False)

def update_sql_by_sku(sku,data,dep):
    name,breast,minwrest,maxwrest,hip,detail,data_size = data
    task = f"""
        update {dep}.stock_main
        set descript = '{name}', breast = '{breast}', minwrest = '{minwrest}', maxwrest = '{maxwrest}', hip = '{hip}', detail = '{detail}', data_size = '{data_size}'
        where sku = '{sku}'
    """
    db.query_commit(task)
    task = f"""
        update {dep}.data_size
        set data_size = '{data_size}'
        where sku = '{sku}'
    """
    db.query_commit(task)

def insert_sql_by_sku(data,dep):
    sku,name,breast,minwrest,maxwrest,hip,detail,data_size = data
    task = f"""
        insert into {dep}.stock_main
        values ('{sku}','{name}','{sku.split("-")[1]}','','{breast}','{minwrest}','{maxwrest}','{hip}','{detail}','{data_size}')
    """
    db.query_commit(task)
    task = f"""
        insert into {dep}.data_size
        values ('{sku}','{sku.split("-")[1]}','{get_idsell(sku)}','{data_size}')
    """
    db.query_commit(task)

def insert_data_size(sku,s,idsell,size):
    task = f"""
    insert into muslin.data_size
    values('{sku}','{s}','{idsell}','{size}')
    """
    db.query_commit(task)

def export_excel(script,name,dep='muslin'):
    
    cursor = db.query_custom(script,dep)
    columns = [desc[0] for desc in cursor.description]
    data = cursor.fetchall()
    df = pd.DataFrame(list(data), columns=columns)

    writer = pd.ExcelWriter(f'{settings.MEDIA_ROOT}/stock/{name}.xlsx')
    df.to_excel(writer, sheet_name='bar',index=False)
    writer.save()
    return f'/media/stock/{name}.xlsx'

def update_table_size():
    query = """select sku from muslin.stock_main"""
    result = db.query(query)
    result = list(result.fetchall())
    result = [i[0] for i in result]
    for i in len(result):
        size_dict = {"XS":0,"S":1,"M":2,"L":3,"XL":4,"XXL":5,"2XL":6,"3XL":7}
        task = f"""
        insert into size
        values ('{result[i]}','{result[i].split("-")[1]}','{size_dict[{result[i].split("-")[1]}]}')
        """
        db.query_commit(task)

def get_data(path,dep):
    df = pd.read_excel(path)

    if dep == 'muslin':
        column = {"sku":"SKU.1","name":"Description","amount":'Incoming ',"cost":'Unnamed: 11'}
    else:
        column = {"sku":"SKU.1","name":"Description","amount":'Incoming ',"cost":'Unnamed: 10'}
    df = df.iloc[1: , :]
    df.dropna(subset = [column['sku']], inplace=True)

    sku = [df.loc[i,column['sku']] for i in df.index]
    name = [df.loc[i,column['name']] for i in df.index]
    amount = [df.loc[i,column['amount']] for i in df.index]
    cost = [df.loc[i,column['cost']] for i in df.index]

    data = list(zip(sku,name,amount,cost))

    # task = f"""select addorder_detail.* from addorder_detail inner join addorder on addorder.idaddorder = addorder_detail.id
    #         where addorder.status = 0 and addorder_detail.status = 0"""
    # result = db.query_custom(task,dep)
    # result = list(result.fetchall())
    # reserveOrder = {}
    # for i in result:
    #     reserveOrder[i[1]] = int(i[2]),i[0]

    # for i in data:
    #     if data[0] in reserveOrder:
    #         data[2] -= reserveOrder[data[0]][0]
    #         db.query_commit(f"update {dep}.addorder_detail set status = 1 where id = {reserveOrder[data[0]][1]}")

    # prepare_keyorder(dep)
    return data

def export_excel_vrichform(data,dest_path):
    df = pd.DataFrame(data, columns=['รหัสสินค้า', 'รายละเอียด', 'จำนวน', 'ต้นทุน','ราคา'])

    def get_cost(sku):
        try:
            sku = get_idsell(sku)[0]
            price_dict = {"A":790,"B":890,"C":950,"D":890,"E":790,"X":690,"N":790,"T":890,"P":950,"R":890,"K":890,'Y':890,"U":890,"G":890,"V":890,'J':0,'ก':690,'W':790}
            return price_dict[sku]
        except:
            return 0

    df['รหัสขาย'] = df['รหัสสินค้า'].apply(get_idsell)
    df = df[df['รหัสขาย'] != 'wrong']
    df['หน่วย'] = ''
    df['ค่าส่งเพิ่ม'] = 0
    df['หมายเหตุ'] = ''
    df['จำนวน'] = df['จำนวน'].apply(pd.to_numeric, errors='ignore')
    df['ต้นทุน'] = df['ต้นทุน'].apply(pd.to_numeric, errors='ignore')
    df['ราคา'] = df['ราคา'].apply(pd.to_numeric, errors='ignore')
    df = df[['รหัสสินค้า', 'รหัสขาย', 'รายละเอียด', 'หน่วย',
             'จำนวน', 'ราคา', 'ต้นทุน', 'ค่าส่งเพิ่ม', 'หมายเหตุ']]
    df.to_excel(f'{dest_path}', index=False)

def prepare_keyorder(dep):    
    task = "select id,min(status) from addorder_detail group by id"
    result = db.query_custom(task,dep)
    result = list(result.fetchall())
    for i in result:
        if int(i[1]) > 0:
            key(dep,i[0])

def key(dep,id):
    #product
    task = f"""select addorder_detail.*,descript,stock_main.amount from addorder_detail
            inner join stock_main on stock_main.sku = addorder_detail.sku
            where id ={id}"""
    product = db.query_custom(task,dep)
    product = list(product.fetchall())
    data_list = []
    for i in product:
        name = i[5]
        sku = i[1]
        amount = int(i[2])
        price = int(i[3])   
        web.post("UPDATEPRODUCTAVAILABLESTOCKLIST",sku,int(i[6]) + amount)
        data_form = {"sku":sku,"name":name,"number":amount,"pricepernumber":price,"discount":"0","totalprice":price * amount}
        data_list.append(data_form)
    #product

    #information
    task = f"select * from addorder where id = {id}"
    result = db.query_custom(task,dep)
    result = list(result.fetchall())
    task = f"select max(number) from deli_zort where number like '%SO%'"
    maxnumber = db.query_custom(task,dep)
    maxnumber = list(maxnumber.fetchall())[0][0]
    splitMaxnumber = maxnumber.split('-')[1]
    splitMaxnumber = int(splitMaxnumber) + 1
    maxnumber = f"SO-{splitMaxnumber}"
    idaddorder, name, addr, phone, shippingchannel, paymentmethod, discount, shippingamount, status, date, total = result
    if 'cod' in shippingchannel.lower():
        isCOD = True
        cstname += " (COD)"
        zort_form = {
            "number":maxnumber,
            'customername':cstname,
            'customerphone':phone,
            'customeraddress':addr,
            'shippingname':cstname,
            'shippingphone':phone,
            'shippingaddress':addr,
            'shippingchannel':shippingchannel,
            'isCOD':isCOD,
            "orderdate": f"{datetime.date.today()}",
            "amount": total,
            "discount": discount,
            "vattype": 3,
            "shippingamount":shippingamount ,
            "warehousecode":"W0001",
            "list":data_list
            }
    else:
        isCOD = False
        zort_form = {
            "number":maxnumber,
            'customername':cstname,
            'customerphone':phone,
            'customeraddress':addr,
            'shippingname':cstname,
            'shippingphone':phone,
            'shippingaddress':addr,
            'shippingchannel':shippingchannel,
            'isCOD':isCOD,
            "orderdate": f"{datetime.date.today()}",
            "amount": total,
            "discount": discount,
            "vattype": 3,
            "shippingamount":shippingamount ,
            "warehousecode":"W0001",
            "paymentmethod" : paymentmethod,
            "paymentamount":total,
            "list":data_list
            }
    db.query_commit(f'update {dep}.addorder set status = 1 where id = {id}')
    web = Web(get_api_register(dep,"apikey"),get_api_register(dep,"apisecret"),get_api_register(dep,"storename"))
    web.post_order(zort_form)

def cleaned_data_for_zort(data,checked_stock,dep,path=''):
    def tranprice(dep,sku):
        if dep == 'muslin':
            try:
                idsell = get_idsell(sku)[0]
                price_dict = {"L":850,"H":990,"A":790,"B":890,"C":990,"D":890,"E":790,"X":690,"N":790,"T":890,"P":990,"R":890,"K":890,"U":890,"G":890,"V":890,'J':'','ก':690,'W':790}
                if idsell == 'Y':
                    if 'แขนสั้นขาสั้น' in sku:
                        return 790
                    elif 'แขนยาวขายาว' in sku:
                        return 950
                    else:
                        return 890
                else:
                    return price_dict[idsell]
            except:
                return 0
        else:
            return 0
    vrich = []
    web = Web("7KRzYzjPqknzzSM2nVcooo3sWNF6EK4Oyq9QtGI8uyk=","RA9VD1AjwaHo8UW0uNk924SnxN0xIFIGdlelDEcTEE=","Muslin.info@gmail.com")
    
    result = db.query(f"select sku,amount from {dep}.stock")
    result = list(result.fetchall())
    cost_dict = {}
    for i in result:
        cost_dict[i[0]] = i[1]

    result = db.query(f"select sku from {dep}.reserve")
    result = list(result.fetchall())
    reserveList = [i[0].split(' ')[0] for i in result]
        
    result = db.query(f"select sku,amount,image from {dep}.stock_main")
    result = list(result.fetchall())
    amount_dict = {}
    for i in result:
        amount_dict[i[0]] = [i[1],i[2]]

    result = db.query(f"select sku,price from {dep}.cost")
    result = list(result.fetchall())
    price_dict = {}
    for i in result:
        try:
            price_dict[i[0]] = int([i[1]])
        except:
            price_dict[i[0]] = 0

    def tran(sku):
        try:
            return price_dict[sku]
        except:
            return 0
            
    def prepare_amount2(sku,value,cost,name,dep):
        if dep == 'muslin':
            if '-' in sku:
                size = sku.split('-')[1]
            else:
                size = ''
            try:
                zort_amount = int(amount_dict[sku][0])
                if amount_dict[sku][1] == 'None':
                    return 0,value
                amount = int(value) - (2-zort_amount)
                if amount >= 0:
                    return (2-zort_amount),amount
                else:
                    return int(value),0
            except:
                vrich.append(sku)
                db.query_commit(f'insert into {dep}.stock values ("{sku}",0);\n')
                db.query_commit(f'insert into {dep}.stock_detailsize values ("{sku}","","","","");\n')
                db.query_commit(f"insert into {dep}.cost values('{sku}',{cost},0,{tranprice(dep,sku)})")
                task = f'''
                insert into {dep}.data_size
                values ("{sku}","{size}","{get_idsell(sku)}","")
                  '''
                db.query_commit(task)
                command = (f'''insert into {dep}.stock_main
                                    values ("{sku}","{name}","{size}","None","34","24","46",
                                          "50","","",0)''')
                db.query_commit(command)
                # with open ("multi.txt","a",encoding="utf-8") as f:
                #     f.write(f'insert into {dep}.stock_detailsize values ("{sku}","","","","");\n')
                #     f.write(f'insert into {dep}.stock values ("{sku}",0);\n')
                return 0,int(value)
        else:
            try:
                zort_amount = int(amount_dict[sku][0])
                return int(value),0
            except:
                print('new',sku)
                if '-' in sku:
                    size = sku.split('-')[1]
                else:
                    size = ''
                # db.query_commit(f'insert into {dep}.stock values ("{sku}",0);\n')
                # db.query_commit(f'insert into {dep}.stock_detailsize values ("{sku}","","","","");\n')
                vrich.append(sku)
                db.query_commit(f'insert into {dep}.stock_detailsize values ("{sku}","","","","");\n')
                db.query_commit(f'insert into {dep}.stock values ("{sku}",0);\n')
                task = f"insert into {dep}.cost values('{sku}',{cost},0,{tranprice(dep,sku)})"
                print(task)
                db.query_commit(task)
                task = f'''
                insert into {dep}.data_size
                values ("{sku}","{size}","{get_idsell(sku)}","")
                  '''
                db.query_commit(task)
                command = (f'''insert into {dep}.stock_main
                                    values ("{sku}","{name}","{size}","None","34","24","46",
                                          "50","","",0)''')
                db.query_commit(command)

            return int(value),0

    def prepare_amount_vrich(sku):
        try:
            return cost_dict[sku]
        except:
            return 0

    data_list = []
    taskdb_stock_main = ''
    taskdb_stock = ''
    sum_all = 0
    for i in range(len(data)):
        data[i] = list(data[i])
        sku = str(data[i][0])
        if sku in reserveList:
            result = db.query_custom(f"select fname from reserve where sku like '%{sku}%'",dep)
            result = list(result.fetchall())
            for res in result:
                send_line_return(f"รหัสนี้มาแล้ว {sku} ลูกค้าชื่อ {res[0]}")
        name = str(data[i][1])
        data[i].append(tran(sku))
        if not sku in name:
            name = f"{data[i][0]} {data[i][1]}"
        
        amount,data[i][2] = prepare_amount2(sku,data[i][2],float(data[i][3]),str(name),dep)
        data_form = {"sku":str(sku),"name":str(name),"number":int(amount),"pricepernumber":float(data[i][3]),"discount":"0","totalprice":float(data[i][3]) * int(amount)}
        data_list.append(data_form)
        sum_all += float(float(data[i][3]) * amount)
        # db.query_commit(f"update {dep}.cost set cost = '{float(data[i][3])}' where sku = '{sku}'")
        if not checked_stock:
            data[i][2] += prepare_amount_vrich(data[i][0])
        # send_line(f"อัพสต็อค {sku},{data[i][2]}")
        if dep == 'muslin':
            try:
                # with open ("multi.txt","a",encoding="utf-8") as f:
                #     f.write(f"update {dep}.stock_main set amount = { int(amount_dict[sku][0]) + amount} where sku = '{sku}';\n")
                taskdb_stock_main += f"WHEN '{sku}' THEN { int(amount_dict[sku][0]) + amount}\n"
                # db.query_commit(f"update {dep}.stock_main set amount = { int(amount_dict[sku][0]) + amount} where sku = '{sku}';\n")

            except:
                # with open ("multi.txt","a",encoding="utf-8") as f:
                #     f.write(f"update {dep}.stock_main set amount = 0 where sku = '{sku}';\n")
                taskdb_stock_main += f"WHEN '{sku}' THEN 0\n"
                # db.query_commit(f"update {dep}.stock_main set amount = 0 where sku = '{sku}';\n")

            # with open ("multi.txt","a",encoding="utf-8") as f:
            #     f.write(f"update {dep}.stock set amount = {data[i][2]} where sku = '{sku}';\n")
            taskdb_stock += f"WHEN '{sku}' THEN {data[i][2]}\n"   
            # db.query_commit(f"update {dep}.stock set amount = {data[i][2]} where sku = '{sku}';\n")
    if dep == 'muslin':
        task_final = f'''
        UPDATE {dep}.stock_main
        SET amount
        = CASE sku
        {taskdb_stock_main}
        ELSE amount
        END;
        '''
        db.query_commit(task_final)
        task_final = f'''
        UPDATE {dep}.stock
        SET amount
        = CASE sku
        {taskdb_stock}
        ELSE amount
        END;
        '''
        db.query_commit(task_final)

    if not path:
        refer = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
    else:
        refer = path
    zort_form = {
        "reference":f"{refer} {datetime.date.today()}",
        "number": f"{refer} {datetime.date.today()}",
        "purchaseorderdate": f"{datetime.date.today()}",
        "amount": sum_all,
        "warehousecode":"W0001",
        "paymentmethod" : "Cash",
        "paymentamount":sum_all,
        "status" : "Success",
        "list":data_list
        }

    return vrich,zort_form

def get_diff(data,dep):
    result = db.query_custom("select stock.sku,stock.amount + stock_main.amount from stock_main inner join stock on stock_main.sku = stock.sku",dep)
    result = list(result.fetchall())
    result_dict = {}
    DATA = []
    for i in result:
        result_dict[i[0]] = i[1]
    for i in range(len(data)):
        data[i] = list(data[i])
        try:
            data[i].insert(2,result_dict[data[i][0]])
            data[i].insert(3,data[i][3])
            data[i][4] = data[i][4] - result_dict[data[i][0]]
        except:
            print(data[i][0])
            DATA.append(data[i][0])
    skus = [i[0] for i in data]
    for sku in result_dict:
        if sku not in skus:
            data.append((sku,sku,result_dict[sku],0,result_dict[sku] - 0,0))
    if DATA:
        df = pd.DataFrame(DATA)
    else:
        columns = ['SKU','ชื่อ','จำนวนเก่า','จำนวนใหม่','จำนวนต่าง','ต้นทุน']
        df = pd.DataFrame(data,columns=columns)
        df = df.sort_values(by='จำนวนต่าง', key=abs,ascending=False)

    df.to_excel(f"{settings.MEDIA_ROOT}/stock/diff.xlsx",index=False)

def upstock(path,dep):
    cancelLoadpath()
    def tran(dep,sku):
        if dep == 'muslin':
            try:
                idsell = get_idsell(sku)[0]
                price_dict = {"L":850,"H":990,"A":790,"B":890,"C":990,"D":890,"E":790,"X":690,"N":790,"T":890,"P":990,"R":890,"K":890,"U":890,"G":890,"V":890,'J':'','ก':690,'W':790}
                if idsell == 'Y':
                    if 'แขนสั้นขาสั้น' in sku:
                        return 790
                    elif 'แขนยาวขายาว' in sku:
                        return 950
                    else:
                        return 890
                else:
                    return price_dict[idsell]
            except:
                return 0
        else:
            result = db.query(f"select sku,price from {dep}.cost")
            result = list(result.fetchall())
            price_dict = {}
            for i in result:
                price_dict[i[0]] = i[1]
            try:
                return price_dict[sku]
            except:
                return 0

    data = get_data(path,dep)
    # get_diff(data)
    vrich,zort = cleaned_data_for_zort(data,False,dep,os.path.basename(path))
    path = f"{str(path).split('.')[0]}.xlsx"
    web = Web(get_api_register(dep,'apikey'),get_api_register(dep,'apisecret'),get_api_register(dep,'storename'))
    print(zort)
    web.post_purchase_order(zort)
    for i in vrich:
        web.updateproduct(i,tran(dep,i))
    runLoadpath()
    return path

def get_diff_stock(path,dep):

    descript = db.query(f"select sku,descript from {dep}.stock_main")
    descript = list(descript.fetchall())
    descript_dict = {}
    for i in descript:
        descript_dict[i[0]] = i[1]

    price = db.query(f"select sku,cost from {dep}.cost")
    price = list(price.fetchall())
    price_dict = {}
    for i in price:
        price_dict[i[0]] = i[1]

    def get_cost(sku):
        try:
            return price_dict[sku]
        except:
            return 0

    def get_data_checkstock(path):
        df = pd.read_excel(path)

        column = [i for i in df.columns]

        sku = [df.loc[i,column[0]] for i in df.index if str(df.loc[i,column[0]]) != 'nan']
        # amount = [df.loc[i,'จำนวน'] for i in df.index]

        # count duplicated
        amount_dict = Counter(sku)

        # remove duplicated
        sku = list(dict.fromkeys(sku))
 
        amount = [amount_dict[i] for i in sku]
        descript = []
        for i in sku:
            try:
                descript.append(descript_dict[i])
            except:
                descript.append(i)
        cost = [get_cost(i) for i in sku]
        data = list(zip(sku,descript,amount,cost))

        task = "select descript from RMA_data where id in (select id from RMA where recieve_time is null and order_status != 'ส่งทันที')"
        reservedForRma = db.query_custom(task,dep)
        reservedForRma = list(reservedForRma.fetchall())
        reservedForRma = [i[0] for i in reservedForRma]
        reservedSku = []
        for i in reservedForRma:
            task = db.query_custom(f"select sku from stock_main where descript = '{i}'",dep)
            try:
                sku = list(task.fetchall())[0][0]
            except:
                task = db.query_custom(f"select sku from stock_main where descript like '%{i.split(' ')[0]}%'",dep)
                sku = list(task.fetchall())[0][0]

            reservedSku.append(sku)
        for i in range(len(data)):
            if data[i][0] in reservedSku:
                data[i] = list(data[i])
                data[i][2] -= 1
                data[i] = tuple(data[i])
        return data
        
    data = get_data_checkstock(path)
    print('done getdata')
    get_diff(data,dep)
    return 'media/stock/diff.xlsx'

def check_stock(path,dep):
    descript = db.query(f"select sku,descript from {dep}.stock_main")
    descript = list(descript.fetchall())
    descript_dict = {}
    for i in descript:
        descript_dict[i[0]] = i[1]

    price = db.query(f"select sku,cost from {dep}.cost")
    price = list(price.fetchall())
    price_dict = {}
    for i in price:
        price_dict[i[0]] = i[1]

    def get_cost(sku):
        try:
            return price_dict[sku]
        except:
            return 0

    def get_data_checkstock(path):
        df = pd.read_excel(path)

        column = [i for i in df.columns]

        sku = [df.loc[i,column[0]] for i in df.index if str(df.loc[i,column[0]]) != 'nan']
        # amount = [df.loc[i,'จำนวน'] for i in df.index]

        # count duplicated
        amount_dict = Counter(sku)

        # remove duplicated
        sku = list(dict.fromkeys(sku))
 
        amount = [amount_dict[i] for i in sku]
        descript = []
        for i in sku:
            try:
                descript.append(descript_dict[i])
            except:
                descript.append(i)
        cost = [get_cost(i) for i in sku]
        data = list(zip(sku,descript,amount,cost))
        df = pd.DataFrame(data)
        df.to_excel(f"{settings.MEDIA_ROOT}/stock/checkstock_cleaned.xlsx",index=False)

        task = "select descript from RMA_data where id in (select id from RMA where recieve_time is null and order_status != 'ส่งทันที')"
        reservedForRma = db.query_custom(task,dep)
        reservedForRma = list(reservedForRma.fetchall())
        reservedForRma = [i[0] for i in reservedForRma]
        reservedSku = []
        for i in reservedForRma:
            task = db.query_custom(f"select sku from stock_main where descript = '{i}'",dep)
            try:
                sku = list(task.fetchall())[0][0]
            except:
                task = db.query_custom(f"select sku from stock_main where descript like '%{i.split(' ')[0]}%'",dep)
                sku = list(task.fetchall())[0][0]

            reservedSku.append(sku)
        for i in range(len(data)):
            if data[i][0] in reservedSku:
                data[i] = list(data[i])
                data[i][2] -= 1
                data[i] = tuple(data[i])
                print(data[i])
        print('ZZZZZZZZZZZZZZZZZZZZZZZ')
        for i in data:
            if i[0] in reservedSku:
                print(i)
        task =f"""update {dep}.addorder_detail inner join addorder on addorder.idaddorder = addorder_detail.id
            set addorder_detail.status = 0  where addorder.status = 0"""
        
        # db.query_commit(task)

        task = f"""select addorder_detail.* from addorder_detail inner join addorder on addorder.idaddorder = addorder_detail.id
                where addorder.status = 0 """
        if dep == 'muslin':
            result = db.query_custom(task,dep)
            result = list(result.fetchall())
            reserveOrder = {}
            for i in result:
                reserveOrder[i[1]] = int(i[2]),i[0]

            for i in data:
                if data[0] in reserveOrder:
                    data[2] -= reserveOrder[data[0]][0]
                    # db.query_commit(f"update {dep}.addorder_detail set status = 1 where id = {reserveOrder[data[0]][1]} and sku = '{data[0]}'")
                    print(f"update {dep}.addorder_detail set status = 1 where id = {reserveOrder[data[0]][1]} and sku = '{data[0]}'")

            # prepare_keyorder(dep)
        return data
        
    data = get_data_checkstock(path)
    print('done getdata')
    # get_diff(data,',muslin')
    vrich,zort = cleaned_data_for_zort(data,True,dep)
    print('cleaned')
    web = Web(get_api_register(dep,'apikey'),get_api_register(dep,'apisecret'),get_api_register(dep,'storename'))
    web.post_purchase_order(zort)
    runLoadpath()
    return "media/stock/checkstock_cleaned.xlsx"

def nospecial(text):
	import re
	text = re.sub("[^a-zA-Z0-9]+", "",text)
	return text

# web = Web("pteRXLvqBNcUXlgIB3RDHxBn3vXoi9cwRp6u/v9M=","GbJK2j7YS5dJtVaBomSsdyenjYuEwdI2A4gLPbKrRAI=","Maruay18.co.th@gmail.com")
# web.get_track_2(1)
# web.get_track_2(2)
# web.get_track_2(3)
def insert_jt(path,dep):
    df = pd.read_excel(path)
    colum = [i for i in df.columns]
    df = df[1:]
    df.dropna(subset = [colum[1]], inplace=True)
    
    track = [df.loc[i,colum[1]] for i in df.index]
    cstname = [df.loc[i,colum[2]] for i in df.index]
    day = datetime.datetime.now() - datetime.timedelta(days = 1)
    # day = datetime.datetime.now()
    for i in range(len(cstname)):
        db.query_commit(f"insert into {dep}.jt values ('{track[i]}','{cstname[i]}','{day.strftime('%Y-%m-%d')}')")

def get_diff_JT(day):
    task = f"select *,if(customername in (select customername from jt where shippingdate = '{day}'),'เปลี่ยนเลขแทรค','ไม่มีแทรค') as สาเหตุ from deli_zort where trackingno not in (select trackingno from jt) and shippingtime = '{day}'"
    export_excel(task,'diff2')
    task = f"select distinct(IDorder),fbname,cstname,if(cstname in (select customername from jt where shippingdate = '{day}'),'เปลี่ยนเลขแทรค','ไม่มีแทรค') as สาเหตุ from deli_vrich where trackingno not in (select trackingno from jt)"
    export_excel(task,'vrich_diff')

def post_zero_zort(dep):
    cancelLoadpath()
    db.query_commit(f"update {dep}.stock set amount = 0")
    db.query_commit(f"update {dep}.stock_main set amount = 0")
    web = Web(get_api_register(dep,'apikey'),get_api_register(dep,'apisecret'),get_api_register(dep,'storename'))
    for i in range(3):
        try:
            task = web.post_zero(1,dep)
            task2 = web.post_zero(2,dep)
            task3 = web.post_zero(3,dep)
            task4 = web.post_zero(4,dep)
            task_final = f'''
            UPDATE {dep}.stock_main
            SET amount
            = CASE sku
            {task}
            {task2}
            {task3}
            {task4}
            ELSE amount
            END;
            '''
            db.query_commit(task_final)
        except:
            print('error')
        print('done')
# post_zero_zort()

def get_amount(sku,amount,dep='muslin'):
    amount = int(amount)
    result = db.query(f"select amount from {dep}.stock where sku = '{sku}'")
    result = list(result.fetchall())[0][0]
    result = int(result)
    new_amount = 2 - amount
    if result - new_amount >= 0:
        return 2,result - new_amount
    else:
        return amount + result,0

def upstock_no_vrich(refername,path,dep):

    web = Web(get_api_register(dep,'apikey'),get_api_register(dep,'apisecret'),get_api_register(dep,'storename'))
    descript = db.query(f"select sku,descript from {dep}.stock_main ")
    descript = list(descript.fetchall())
    descript_dict = {}
    for i in descript:
        descript_dict[i[0]] = i[1]

    def get_cost(sku):
        try:
            sku = get_idsell(sku)[0]
            price_dict = {"A":790,"B":890,"C":950,"D":890,"E":790,"X":690,"N":790,"T":890,"P":950,"R":890,"K":890,'Y':890,"U":890,"G":890,"V":890,'J':0,'ก':690,'W':790}
            return price_dict[sku]
        except:
            return 0

    def get_data_checkstock(path):
        df = pd.read_excel(path)
        
        columns = [i for i in df.columns]
        sku = [df.loc[i,columns[0]] for i in df.index]

        # count duplicated
        amount_dict = Counter(sku)

        # remove duplicated
        sku = list(dict.fromkeys(sku))

        amount = [amount_dict[i] for i in sku]
        descript = []
        for i in sku:
            try:
                descript.append(f"{descript_dict[str(i).strip()]}")
            except:
                descript.append(f"{i} none")
        cost = [get_cost(i) for i in sku]
        data = list(zip(sku,descript,amount,cost))
        # df.to_excel("checkstock_cleaned.xlsx",index=False)
        return data

    data = get_data_checkstock(path)

    data_list = []
    sum_all = 0
    for i in range(len(data)):
        data[i] = list(data[i])
        sku = str(data[i][0])
        name = str(data[i][1])
        amount = int(data[i][2])

        #cost
        data[i][3] = 0

        if not sku in name:
            name = f"{sku} {name}"
        
        data_form = {"sku":sku,"name":name,"number":amount,"pricepernumber":data[i][3],"discount":"0","totalprice":data[i][3] * amount}
        data_list.append(data_form)
        sum_all += data[i][3] * amount

    zort_form = {
        "reference":f"{refername}",
        "number": f"{refername}",
        "purchaseorderdate": f"{datetime.date.today()}",
        "amount": sum_all,
        "warehousecode":"W0001",
        "paymentmethod" : "Cash",
        "paymentamount":sum_all,
        "status" : "Success",
        "list":data_list
        }

    web.post_purchase_order(zort_form)

def export_to_vrich(dep,excelname):
    task = """
    select stock_main.sku,stock_main.descript,stock.amount,cost.cost,cost.price from stock_main
    inner join stock on stock_main.sku = stock.sku
    inner join cost on stock_main.sku = cost.sku
    where stock.amount > 0
    """
    result = db.query_custom(task,dep)
    result = list(result.fetchall())

    sku = [i[0] for i in result]
    descript= [i[1] for i in result]
    name = []

    for i in range(len(sku)):
        if sku[i] in descript[i]:
            name.append(descript[i].replace(sku[i],'').strip())
        else:
            name.append(descript[i])

    amount= [i[2] for i in result]
    cost = [i[3] for i in result]
    price = [i[4] for i in result]

    data = list(zip(sku,name,amount,cost,price))
    export_excel_vrichform(data,f'{excelname}.xlsx')
# export_to_vrich('muslin','ก่อนไลฟ์',True)
def manageStockLive(name):
    task = """
    SELECT a.min_descript, a.idsell, a.sum_amount, concat(a.count_sku,":", b.count_sku) as ratio
    FROM 
    (SELECT min(stock_main.descript) as min_descript, idsell , sum(stock.amount) as sum_amount, count(stock.sku) as count_sku
    FROM stock_main
    INNER JOIN data_size ON data_size.sku = stock_main.sku 
    INNER JOIN stock ON stock.sku = stock_main.sku 
    WHERE stock.amount > 0 
    GROUP BY idsell) as a
    LEFT JOIN (SELECT idsell, count(sku) as count_sku from data_size group by idsell) as b 
    ON a.idsell = b.idsell
    order by idsell ,ratio
    """
    export_excel(task,name)
# manageStockLive('live')
def send_line_blog(msg):
    url = 'https://notify-api.line.me/api/notify'
    token = 'b3pgaYmoqCp51kMPzL4pgknKg68Gc4227OxVg3y3nVe'
    headers = {'content-type': 'application/x-www-form-urlencoded',
               'Authorization': 'Bearer '+token}
    r = requests.post(url, headers=headers, data={'message': msg})

def send_line_blog_admin(msg):
    url = 'https://notify-api.line.me/api/notify'
    token = 'TcfnJ46PQkvm2AqOHhpurxvOCVczm8ruZ023EYjSBb6'
    headers = {'content-type': 'application/x-www-form-urlencoded',
               'Authorization': 'Bearer '+token}
    r = requests.post(url, headers=headers, data={'message': msg})
 
def table_break(time:str,name):
    task = f"""
     select name,date(checkin),time(checkin) as 'เวลาเข้างาน ',time(checkout)  as 'เวลาออกงาน'  ,time(breakin) as เวลาเข้าเบรค,time(breakout) as เวลออกเบรค,
     if(hour(timediff(checkin,checkout)) - 1 >= 8,8,hour(timediff(checkin,checkout)) -1 ) as 'ชั่วโมงทำงาน',if(timediff(breakin,breakout) < -010000,'เบรคเกิน','เบรคพอดี') as เช็คเบรค,
     if(time(checkin) > 091500,'สาย','') as เช็คมาสาย
    from face_check
    where name != 'JUBJANG' and name != 'GINK' and checkin > '{time}'
    order by name,checkin  ;
    """
    export_excel(task,name)

def reportrma(name,dep):
    task = f"""
    select max(RMA.id) as id,max(RMA.number) as ชื่อรายการ,max(reason) as สาเหตุ,max(platform) as platform,max(key_time) as เวลาที่คีย์,max(recieve_time) as เวลารับสินค้า ,group_concat(distinctrow RMA_before.descript) as สินค้าเก่า,group_concat(distinctrow RMA_data.descript) as สินคเาใหม่ from RMA 
    join RMA_before on RMA.id = RMA_before.id
    join RMA_data on RMA.id = RMA_data.id
    group by RMA.id;
    """
    export_excel(task,name,dep)
    
def getBalanceForAccount(text):
    task = f"""
    select deli_zort.idorder,max(number),max(orderdate) as วันที่,sum(order_main.amount) as จำนวนสินค้า,sum(order_main.price) as 'ราคาต่อออเดอร์',sum(T.cost) as 'ต้นทุนรวมต่อออเดอร์',sum(order_main.price) - sum(cost) as 'กำไร' from deli_zort
    inner join order_main on deli_zort.idorder = order_main.idorder
    inner join muslin.T on muslin.T.sku = order_main.sku
    where orderdate > '2022-04-01' and orderdate <'2022-06-01' and number like 'SO-%' and status != "Voided" and number not like '%return%'
    group by deli_zort.idorder order by max(orderdate) ;
    """
    export_excel(task,'zortBalance')
    task = f"""
    select idorder,max(date) as วันที่,sum(amount) as จำนวนสินค้า,sum(deli_vrich.price) as 'ราคาต่อออเดอร์',sum(T.cost) as 'ต้นทุนรวมต่อออเดอร์',sum(deli_vrich.price) - sum(cost) as 'กำไร' from deli_vrich inner join T on T.sku = deli_vrich.sku
    where date > '{text}'
    group by idorder order by max(date) ;
    """
    export_excel(task,'vrichBalance')
    task ="""
    select date(orderdate) as วันที่ ,sum(order_main.amount) as จำนวนสินค้า,count(distinct(order_main.idorder)) as จำนวนออเดอร์,sum(order_main.price) - sum(cost) as กำไรต่อวัน from deli_zort 
    inner join order_main on order_main.idorder = deli_zort.idorder
    inner join T on T.sku = order_main.sku
    where status != "Voided" and order_main.price - cost  > 0
    group by date(orderdate);
    """
    export_excel(task,'OrderZortGroupByDate')
    task = """
    select date(date) as วันที่ ,sum(deli_vrich.amount) as จำนวนสินค้า,count(distinct(IDorder)) as จำนวนออเดอร์,sum(deli_vrich.price) - sum(cost) as กำไรต่อวัน from deli_vrich
    inner join T on T.sku = deli_vrich.sku
    group by date(date);
    """
    export_excel(task,'OrderVrichGroupByDate')

def fullFill(path,destname,dep):
    CHECK = False
    descript = db.query(f"select sku,descript from {dep}.stock_main")
    descript = list(descript.fetchall())
    descript_dict = {}
    for i in descript:
        descript_dict[i[0]] = i[1]

    price = db.query(f"select sku,cost from {dep}.cost")
    price = list(price.fetchall())
    price_dict = {}
    for i in price:
        price_dict[i[0]] = i[1]

    sell = db.query(f"select sku,price from {dep}.cost")
    sell = list(sell.fetchall())
    sell_dict = {}
    for i in sell:
        sell_dict[i[0]] = i[1]

    def get_cost(sku):
        try:
            return price_dict[sku]
        except:
            return 0
            
    df = pd.read_excel(path)

    column = [i for i in df.columns]

    sku = [df.loc[i,column[0]] for i in df.index if str(df.loc[i,column[0]]) != 'nan']
    # amount = [df.loc[i,'จำนวน'] for i in df.index]

    # count duplicated
    if len(column) < 2:
        amount_dict = Counter(sku)

        # remove duplicated
        sku = list(dict.fromkeys(sku))

        amount = [amount_dict[i] for i in sku]
    else:
        amount = [df.loc[i,column[1]] for i in df.index if str(df.loc[i,column[0]]) != 'nan']
        
    descript = []
    for i in sku:
        try:
            descript.append(descript_dict[i])
        except:
            descript.append(i)
    cost,price,error_sku = [],[],[]
    for i in sku:
        try:
            cost.append(get_cost(i))
            price.append(sell_dict[i])
        except:
            CHECK = True
            error_sku.append(i)

    name = []
    for i in range(len(sku)):
        if sku[i] in descript[i]:
            name.append(descript[i].replace(sku[i],'').strip())
        else:
            name.append(descript[i])

    if not CHECK:
        data = list(zip(sku,name,amount,cost,price))
        export_excel_vrichform(data,f'{settings.MEDIA_ROOT}/stock/{destname}.xlsx')
        return f'media/stock/{destname}.xlsx'
    df = pd.DataFrame(error_sku,columns=['รหัสที่พิมพ์ผิด'])
    df.to_excel(f"{settings.MEDIA_ROOT}/stock/{destname}.xlsx",index=False)
    return f'media/stock/{destname}.xlsx'

# check_stock('เช็คสต็อกร้านเล็ก 17-11-22.xlsx','maruay')
def tran_to_vrich(excelpath):
    dep = 'muslin'
    df = pd.read_excel(excelpath)
    sku = [df.loc[i,'sku'] for i in df.index]
    amount_list = []
    datadict = {}
    datadict['stocks'] = list()
    taskdb_stock = ''
    taskdb_stock_main = ''
    SKU = []
    for i in sku:
        task = f"select stock.sku,stock.amount + stock_main.amount from stock\
                inner join stock_main on stock.sku = stock_main.sku \
            inner join data_size on data_size.sku = stock.sku\
                where data_size.sku like '%{i}%'"
        result = db.query_custom(task,'muslin')
        amount = list(result.fetchall())


        for index in amount:
            print(index[0],index[1])
            datadict['stocks'].append({"sku": index[0], "stock": 0,'cost':0})
            taskdb_stock += f"WHEN '{index[0]}' THEN 0\n"
            taskdb_stock_main += f"WHEN '{index[0]}' THEN 0\n"
            # db.query_commit(f"update muslin.stock set amount = 0 where sku = '{index[0]}'")
            # db.query_commit(f"update muslin.stock_main set amount = 0 where sku = '{index[0]}'")
            SKU.append(index[0])
            amount_list.append(index[1])
            if len(datadict['stocks']) % 300 and len(datadict['stocks']) >= 300:
                web.postzero(datadict)
                datadict['stocks'] = list()
    
    web.postzero(datadict)
    datadict['stocks'] = list()

    task_final = f'''
        UPDATE {dep}.stock_main
        SET amount
        = CASE sku
        {taskdb_stock_main}
        ELSE amount
        END;
        '''
    db.query_commit(task_final)
    task_final = f'''
        UPDATE {dep}.stock
        SET amount
        = CASE sku
        {taskdb_stock}
        ELSE amount
        END;
        '''
    db.query_commit(task_final)

    df2 = pd.DataFrame(list(zip(SKU,amount_list)))
    df2.to_excel('ตัวโชว์ final.xlsx',index=False)

# tran_to_vrich('เหลือน้อย 15.12.xlsx')
# path = 'slip'
# for i in os.listdir(path):
#     print("{:.2f} %".format(os.listdir(path).index(i) / len(path) * 100))
#     write_image_top_right2(os.path.join(path,i),i.split('.')[0])

def test2():
    task = 'select sku,amount from stock_main where amount < 0'
    data = db.query_custom(task,'maruay')
    data = data.fetchall()
    dep = 'maruay'
    for i in data:
        print(i[0])
        web.post("UPDATEPRODUCTAVAILABLESTOCKLIST",i[0],0 )
        db.query_commit(f"update {dep}.stock_main set amount = 0 where sku = '{i[0]}';\n")
# test2() 

# UPDATE AMOUNT FROM VRICH TO ZORT AND UPDATE AMOUNT FROM VRICH TO 0
def update_vrich():
    dep = 'muslin'
    task = 'select sku,amount from muslin.stock_vrich where amount > 0'
    result = list(db.query_custom(task,'muslin').fetchall())
    taskdb_stock = ''
    for i in result:
        taskdb_stock += f"WHEN '{i[0]}' THEN amount + {i[1]}\n"   
                # db.query_commit(f"update {dep}.stock set amount = {data[i][2]} where sku = '{sku}';\n")

    task_final = f'''
    UPDATE muslin.stock
    SET amount
    = CASE sku
    {taskdb_stock}
    ELSE amount
    END;
    '''

    db.query_commit(task_final)
    task = 'update muslin.stock_vrich set amount = 0'
    db.query_commit(task)
# update_vrich()

# GET WHICH SKU THAT SIZE SKIP
def get_no_size(dep='muslin'):
    task = """
    select data_size.idsell from data_size inner join stock_main on stock_main.sku = data_size.sku
    inner join stock on stock.sku = stock_main.sku
        group by data_size.idsell having sum(stock_main.amount + stock.amount) > 0"""
    idsell = db.query_custom(task,dep)
    idsell = list(idsell.fetchall())
    idsell = [i[0] for i in idsell]
    task = f"""
    select stock_main.sku,breast,hip from stock_main 
    inner join data_size on data_size.sku = stock_main.sku
    where data_size.idsell in {tuple(idsell)}
    order by data_size.idsell,FIELD(stock_main.size,  'F','XXS', 'XS', 'S', 'M', 'L', 'XL', '2XL','3XL', '4XL','5XL','6XL')
    """
    result = db.query_custom(task,dep)

    result = list(result.fetchall())

    for i in range(len(result)):
        if i == 0:
            continue
        if get_idsell(result[i][0]) == get_idsell(result[i - 1][0]):
            try:
                if abs(int(result[i][2]) - int(result[i-1][2])) > 2:
                    print(int(result[i][2]),int(result[i - 1][2]))
                    print(result[i][0],result[i - 1][0])
            except:
                pass

def QC(dep,path):
    df = pd.read_excel(path)
    # old_SKU = tuple([df.loc[i,'sku'] for i in df.index])
    SKU = tuple([df.loc[i,'sku'] for i in df.index])
    # idsell = [df.loc[i,'รหัสขาย'] for i in df.index]
    data_dict ={}

    result = db.query_custom(f"select sku,data_size from data_size where idsell in {SKU}",dep)
    result = list(result.fetchall())
    for i in result:
        data_dict[i[0]] = i[1]

    for i in range(len(SKU)):
        with open ("multi.txt","a",encoding="utf-8") as f:
            f.write(f"""insert into muslin.data_size values ("{SKU[i]}","{SKU[i].split("-")[1]}","{idsell[i]}",'{data_dict[SKU[i]]}');\n""")
            # db.query_commit(f"""insert into muslin.data_size values ("{SKU[i]}","{SKU[i].split("-")[1]}","{idsell[i]}",'{datasize}');\n""")
# path = 'เยอะ.xlsx'
# QC('muslin',path)
def sql(empdata,table,databasedb):
    start_time = time.time()
    engine = create_engine("mysql+pymysql://" + userdb + ":" + passworddb + "@" + hostdb + "/" + databasedb)
    empdata.to_sql(table,engine ,index=False,if_exists='replace',method='multi')
   # print("--- %s seconds ---" % (time.time() - start_time))

def Start(path,database):
    df = pd.read_excel(path)
    df['size'] = df.iloc[:, 0].astype(str).str.split('-',expand=True)[1]
    df = df.set_axis(['sku', 'idsell', 'descript', 'unit', 'amount', 'price', 'cost', 'fee', 'etc', 'position','size'], axis=1, inplace=False)
    df.drop(['unit','price','cost','fee','etc','position'],axis='columns',inplace=True)
    sql(df,'stock_vrich',database)

# 
def download_image_vrich():
    task = 'select sku,image from stock_main where image != "none"'
    result = db.query_custom(task,'muslin')
    result = list(result.fetchall())
    sku_list = []
    for i in result:
        if i[0].split('-')[0] not in sku_list:
            with open(rf'C:\Users\Chino\Desktop\rose\{i[0].split("-")[0]}.png', 'wb') as f:
                f.write(convert_url_to_bytes(i[1]))
                f.close()
            sku_list.append(i[0].split('-')[0])
            print("{:.2f} %".format(result.index(i) / len(result) * 100))

def StartTest(path,database):
    print(path)
    df = pd.read_excel(path)
    df = df.set_axis(['IDorder','a','date', 'FBName', 'cstname', 'addr','b','c', 'tel','d','e', 'trackingNo','f','g', 'total_amount', 'cash', 'discount', 'deli_fee', 'total', 'Ebank', 'paid', 'timepaid', 'h','thing1', 'thing2', 'idsell', 'descript', 'Comment', 'amount', 'price', 'timedate', 'Printed', 'Checkout', 'Checkout_Time', 'sku'], axis=1, inplace=False)
    df.drop(['a','b','c','d','e','f','g','h'],axis='columns',inplace=True)
    sql(df,'deli_vrich',database)
    db.query_commit('update muslin.deli_vrich set trackingno = "" where trackingno is null ;')
#
def fullFillKorkai(path,destname,dep):
    descript = db.query(f"select sku,descript from {dep}.stock_main")
    descript = list(descript.fetchall())
    descript_dict = {}
    for i in descript:
        descript_dict[i[0]] = i[1]

    price = db.query(f"select sku,cost from {dep}.cost")
    price = list(price.fetchall())
    price_dict = {}
    for i in price:
        price_dict[i[0]] = i[1]

    sell = db.query(f"select sku,390 from {dep}.cost")
    sell = list(sell.fetchall())
    sell_dict = {}
    for i in sell:
        sell_dict[i[0]] = i[1]

    def get_cost(sku):
        try:
            return price_dict[sku]
        except:
            return 0
            
    df = pd.read_excel(path)

    column = [i for i in df.columns]

    sku = [df.loc[i,column[0]] for i in df.index if str(df.loc[i,column[0]]) != 'nan']
    # amount = [df.loc[i,'จำนวน'] for i in df.index]

    # count duplicated
    if len(column) < 2:
        amount_dict = Counter(sku)

        # remove duplicated
        sku = list(dict.fromkeys(sku))

        amount = [amount_dict[i] for i in sku]
    else:
        amount = [df.loc[i,column[1]] for i in df.index if str(df.loc[i,column[0]]) != 'nan']
        
    descript = []
    for i in sku:
        try:
            descript.append(descript_dict[i])
        except:
            descript.append(i)
    cost = [get_cost(i) for i in sku]
    price = [390 for i in range(len(sku))]

    name = []

    for i in range(len(sku)):
        if sku[i] in descript[i]:
            name.append(descript[i].replace(sku[i],'').strip())
        else:
            name.append(descript[i])

    data = list(zip(sku,name,amount,cost,price))
    export_excel_vrichform(data,f'{destname}')
    return f'{settings.MEDIA_ROOT}/stock/{destname}.xlsx'

def formKorKai(excelpath):
    df = pd.read_excel(excelpath)
    skus = [df.loc[i,'รหัสสินค้า'] for i in df.index]
    descripts = [df.loc[i,'รายละเอียด'] for i in df.index]
    amounts = [df.loc[i,'จำนวน'] for i in df.index]
     
    data_list = []

    for i in range(len(skus)):
        sku = skus[i]
        name = descripts[i]
        amount = int(amounts[i])
        price = 0

        data_form = {"sku":sku,"name":name,"number":amount,"pricepernumber":price,"discount":"0","totalprice":price * amount}
        data_list.append(data_form)

    zort_form = {
    "number":f"VR ก. วันที่ {datetime.date.today()} 2",
    'customername':"VR",
    "orderdate": f"{datetime.date.today()}",
    "amount": 0,
    "warehousecode":"W0001",
    "list":data_list
    }
    web = Web("pteRXLvqBNcUXlgIB3RDHxBn3vXoi9cwRp6u/v9M=","GbJK2j7YS5dJtVaBomSsdyenjYuEwdI2A4gLPbKrRAI=","Maruay18.co.th@gmail.com")
    web.post_order(zort_form)

def Korkai(filename):
    today = datetime.date.today()
    print(filename)
    fullFillKorkai(filename,filename,'maruay')
    df = pd.read_excel(filename)

    idsell = []

    for i in df.index:
        if  df.loc[i,'รหัสขาย'] not in idsell:
            idsell.append(df.loc[i,'รหัสขาย'])
            df.loc[i,'รหัสขาย'] = "ก" + str(len(idsell))
        else:
            df.loc[i,'รหัสขาย'] = "ก" + str(idsell.index(df.loc[i,'รหัสขาย']) + 1)
    df.to_excel(f'{settings.MEDIA_ROOT}/stock/korkai{today}.xlsx',index=False, encoding='utf8')
    formKorKai(f'{settings.MEDIA_ROOT}/stock/korkai{today}.xlsx')
    return f'media/stock/ก {today}.xlsx'

def convertQcToNormal(path,dep):
    df = pd.read_excel(path)
    realsku =[]
    for i in df.index:
        sku = df.loc[i,'sku']
        task = f'select sku from stock_main where sku like "%{sku[1:]}"'
        result = db.query_custom(task,dep)
        result = list(result.fetchall())
        try:
            realsku.append(result[0][0])    
        except:print('error',sku)
        if len(result) != 1:print('เจอหลาย ',sku)

    df = pd.DataFrame(realsku)
    df.to_excel('realsku.xlsx',index=False)

#
