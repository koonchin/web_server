import datetime
import time
import mysql.connector
import requests
import os
from pathlib import Path

hostdb = '139.177.190.161'

passworddb = 'Chino002'

databasedb = 'image'

userdb = 'gink'

host = '127.0.0.1:8000'

BASE_DIR = Path(__file__).resolve().parent.parent

BASE_DIR = os.path.join(BASE_DIR,'app')
MEDIA_ROOT = os.path.join(BASE_DIR,'media')
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
        finally:
            mycursor.close()
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
        finally:
            mycursor.close()
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
        finally:
            mycursor.close()
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
        finally:
            mycursor.close()
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
    
    def send_sales_report(self,dep,date=''):

        header = {
            'storename': f'{self.storename}',
            'apikey': f'{self.apikey}',
            'apisecret': f'{self.apisecret}'
        }

        url = 'https://open-api.zortout.com/v4/Order/GetOrders'
        # datetime.datetime.now().strftime('%Y-%m-%d')
        if not date:
            date = (datetime.datetime.now() - datetime.timedelta(days = 1)).strftime('%Y-%m-%d')

        TIKTOK_AMOUNT,SHOPEE_AMOUNT,LAZADA_AMOUNT,ZORT_AMOUNT,VRICH_AMOUNT = [],[],[],[],[]
        params = {'method': "GETORDERS", 'version': '3','orderdatebefore':date,'orderdateafter':date,'saleschannel':'tiktok'}
        res = requests.get(url=url, headers=header, params=params)
        data = res.json()
        for customer in data['list']:
            if customer['status'].lower() != 'voided':
                TIKTOK_AMOUNT.append(round(float(customer['amount']),2))

        params = {'method': "GETORDERS", 'version': '3','orderdatebefore':date,'orderdateafter':date,'saleschannel':'Vrich'}
        res = requests.get(url=url, headers=header, params=params)
        data = res.json()
        for customer in data['list']:
            if customer['status'].lower() != 'voided':
                VRICH_AMOUNT.append(round(float(customer['amount']),2))

        params = {'method': "GETORDERS", 'version': '3','orderdatebefore':date,'orderdateafter':date,'saleschannel':'lazada'}
        res = requests.get(url=url, headers=header, params=params)
        data = res.json()
        for customer in data['list']:
            if customer['status'].lower() != 'voided':
                LAZADA_AMOUNT.append(round(float(customer['amount']),2))
        if dep == 'muslin':
            params = {'method': "GETORDERS", 'version': '3','orderdatebefore':date,'orderdateafter':date,'saleschannel':'Shopee MuslinPajamas'}
            res = requests.get(url=url, headers=header, params=params)
            data = res.json()
            for customer in data['list']:
                if customer['status'].lower() != 'voided':
                    SHOPEE_AMOUNT.append(round(float(customer['amount']),2))
                    
            params = {'method': "GETORDERS", 'version': '3','orderdatebefore':date,'orderdateafter':date,'saleschannel':'WAR'}
            res = requests.get(url=url, headers=header, params=params)
            data = res.json()
            for customer in data['list']:
                if customer['status'].lower() != 'voided':
                    ZORT_AMOUNT.append(round(float(customer['amount']),2))

            params = {'method': "GETORDERS", 'version': '3','orderdatebefore':date,'orderdateafter':date,'saleschannel':'pare'}
            res = requests.get(url=url, headers=header, params=params)
            data = res.json()
            for customer in data['list']:
                if customer['status'].lower() != 'voided':
                    ZORT_AMOUNT.append(round(float(customer['amount']),2))
        else:
            params = {'method': "GETORDERS", 'version': '3','orderdatebefore':date,'orderdateafter':date,'saleschannel':'Shopee'}
            res = requests.get(url=url, headers=header, params=params)
            data = res.json()
            for customer in data['list']:
                if customer['status'].lower() != 'voided':
                    SHOPEE_AMOUNT.append(round(float(customer['amount']),2))

            params = {'method': "GETORDERS", 'version': '3','orderdatebefore':date,'orderdateafter':date,'saleschannel':'minny'}
            res = requests.get(url=url, headers=header, params=params)
            data = res.json()
            for customer in data['list']:
                if customer['status'].lower() != 'voided':
                    ZORT_AMOUNT.append(round(float(customer['amount']),2))
                
        sum_all = int(sum(TIKTOK_AMOUNT)) +int(sum(SHOPEE_AMOUNT)) + int(sum(LAZADA_AMOUNT)) + int(sum(ZORT_AMOUNT)) + int(sum(VRICH_AMOUNT))
        TIKTOK_SUMALL,SHOPEE_SUMALL,LAZADA_SUMALL,ZORT_SUMALL,VRICH_SUMALL = format(int(sum(TIKTOK_AMOUNT)),','),format(int(sum(SHOPEE_AMOUNT)),','),format(int(sum(LAZADA_AMOUNT)),','),format(int(sum(ZORT_AMOUNT)),','),format(int(sum(VRICH_AMOUNT)),',')
        result =  f"""คีย์มือ : {ZORT_SUMALL}
Shopee : {SHOPEE_SUMALL}
TikTok : {TIKTOK_SUMALL}
Lazada : {LAZADA_SUMALL} 
Vrich : {VRICH_SUMALL} 
ยอดรวม : {format(int(sum_all),',')}"""
        return int(sum(ZORT_AMOUNT)),result

    def addImage(self, sku, imagepath):
        header = {
            'storename': f'{self.storename}',
            'apikey': f'{self.apikey}',
            'apisecret': f'{self.apisecret}'
        }

        url = 'https://api.zortout.com/api.aspx'

        payload = {'method': "UPDATEPRODUCTIMAGE", 'version': '3',
                   'id': self.getId(sku)}

        data = {'file': open(imagepath, 'rb')}
        res = requests.post(url=url, headers=header,
                            params=payload, files=data)
        print('here',res.text)

    def getId(self,sku):
        header = {
            'storename': f'{self.storename}',
            'apikey': f'{self.apikey}',
            'apisecret': f'{self.apisecret}'
        }

        url = 'https://api.zortout.com/api.aspx'

        payload = {'method': "GETPRODUCTS", 'version': '3',
                   'searchsku': sku}

        res = requests.get(url=url, headers=header,
                            params=payload)
        data = res.json()
        return data['list'][0]['id']

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
    def get_telephone(self,pages):
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

    def post_zero(self,dep='muslin'):

        header = {
            'storename': f'{self.storename}',
            'apikey': f'{self.apikey}',
            'apisecret': f'{self.apisecret}'
        }

        url = 'https://api.zortout.com/api.aspx'
        for page in range(1,10):
            payload = {'method': "GETPRODUCTS", 'version': '3',
                        'page': page,'warehousecode':'W0003','activestatus':1}

            res = requests.get(url=url, headers=header, params=payload)
            data = res.json()
            datadict = {}
            datadict['stocks'] = list()
            taskdb_stock = ''
            print(len(data['list']))
            for i in range(len(data['list'])):
                if i % 200 == 0:
                    self.postzero(datadict)
                    datadict['stocks'] = list()
                    print("{:.2f} %".format(i / len(data['list']) * 100))
                if int(data['list'][i]['stock']) != 0 and 'Q' not in data['list'][i]['sku']:
                    datadict['stocks'].append({"sku": data['list'][i]['sku'], "stock": 0,'cost':0})
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

        payload = {'method': method, 'version': '3', 'warehousecode': 'W0002'}
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

        payload = {'method': 'UPDATEPRODUCTSTOCKLIST', 'version': '3', 'warehousecode': 'W0002'}
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

access_tok = 'EAADs69tGsMEBO5GenCnyYZCQTLZAFpnmfow9KZAihhtmQxqZAb0tNmM2BgJ91UYYK2IckvrJrZAnsxLFqT7eo3hA9I6lLhZCXcLCYhaZAL6wozru5ULYgDxOUlIZA6slofrZAzVqTZBtMslZAnYRZC6vjserTKgOWLATo9ZBtuDgF2GTvZCzNZBB8qW9BhPvAZDZD'

# muslin ads account list
ad_acc_list = [
"1233977980713272",
"3126688860975489",
"736282584293594",
"3703607256535041",
"1789954911466934",
"1056201798412529",
"803785237485233",
"2703565199777489",
]

# maruay ads account list
ad_acc_list_maruay = [
"521471879981229",
"1025682725525082",
"2943245342634568",
]
# get spend from add id
def get_ads_spend(access_token, ad_acc_id, date_preset='yesterday'):
    url = f'https://graph.facebook.com/v18.0/act_{ad_acc_id}/insights'
    params = {
        'access_token': access_token,
        'fields': 'spend,account_id,account_currency,account_name,ad_id,ad_name,adset_id,adset_name',
        'date_preset': date_preset
    }

    response = requests.get(url, params=params)
    data = response.json()
    
    try:
        spend = data['data'][0]['spend']
        account_name = data['data'][0]['account_name']
        return round(float(spend), 2)
    except:
        return 0

from linebot import LineBotApi
from linebot.models import TextSendMessage
def auto_send_8am():
    channel_access_token_daily_report = 'w6F1ffyyanDJ+PMtmekbkLiKyNqQID1cWIM1u9oKwdRymskGI9BMCEplfSDsueuv/zOwv401JLWIAYNXucK6E3CuGnZWwTJxMgi91cIaY9L0tVYMPcdW3VuYDr3eEgJ+p6/bzcIeNf+21naBySayUwdB04t89/1O/w1cDnyilFU='

    spend_list = [get_ads_spend(access_tok, acc_id,'yesterday') for acc_id in ad_acc_list]
    ads_amount = round(sum(spend_list),2)
    spend_list = [get_ads_spend(access_tok, acc_id,'yesterday') for acc_id in ad_acc_list_maruay]
    ads_amount_jj = round(sum(spend_list),2)
    
    dep = 'muslin'
    web = Web(get_api_register(dep,'apikey'),get_api_register(dep,'apisecret'),get_api_register(dep,'storename'))
    muslin_amount,sales_amount = web.send_sales_report('muslin')
    dep = 'maruay'
    web = Web(get_api_register(dep,'apikey'),get_api_register(dep,'apisecret'),get_api_register(dep,'storename'))
    jj_amount,sales_amount_jj = web.send_sales_report('maruay')

    percentage = round((ads_amount / muslin_amount) * 100,2)
    percentage_jj = round((ads_amount_jj / jj_amount) * 100,2)
    if datetime.datetime.now().strftime("%d%m%Y") == "05022023":
        text = 'token will expire soon , https://developers.facebook.com/tools/explorer/169388512639138/?method=GET&path=me%3Ffields%3Did%2Cname&version=v16.0'
        line_bot_api_daily_report = LineBotApi(channel_access_token_daily_report)
        message = TextSendMessage(text=text)
        line_bot_api_daily_report.push_message('C7f9c7403440cef77ffb4561a74b58013',message)

    date = (datetime.datetime.now() - datetime.timedelta(days = 1)).strftime('%Y-%m-%d')
    text = f"""Sales Report {date}\nmuslin Ads : {format(ads_amount,',')}\nmuslin sales\n{sales_amount}\n\njj Ads : {format(ads_amount_jj,',')}\njj sales\n{sales_amount_jj}\nmuslin percent Ads : {percentage}%\njj percent Ads : {percentage_jj}%"""
    line_bot_api_daily_report = LineBotApi(channel_access_token_daily_report)
    message = TextSendMessage(text=text)
    line_bot_api_daily_report.push_message('C7f9c7403440cef77ffb4561a74b58013',message)
auto_send_8am()
web = Web("7KRzYzjPqknzzSM2nVcooo3sWNF6EK4Oyq9QtGI8uyk=","RA9VD1AjwaHo8UW0uNk924SnxN0xIFIGdlelDEcTEE=","Muslin.info@gmail.com")
# web.post_zero()
