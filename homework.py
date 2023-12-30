from function import *

def get_amount(zortamount,amount):
    amount = int(amount)
    zortamount = int(zortamount)
    new_amount = amount - (2 - zortamount)
    if new_amount >= 0:
        return 2,new_amount
    else:
        return zortamount + amount,0

class Web():
    def __init__(self,apikey,apisecret,storename) -> None:
        self.apikey = apikey
        self.apisecret = apisecret
        self.storename = storename

    #  upload trackingno today to database
    # get data from list of www.api.zort.com
    def get(self,method,datatype,page=1):
        header = {
            'storename':f'{self.storename}',
            'apikey':f'{self.apikey}',
            'apisecret':f'{self.apisecret}'
        }

        url = 'https://api.zortout.com/api.aspx'

        payload = {'method':method,'version':'3','page': page}

        res = requests.get(url=url,headers=header,params=payload)
        data = res.json()
        datalist = []
        for i in range(len(data['list'])):
            datalist.append(data['list'][i][datatype])
        return datalist

    def get_datatype_filter_by_sku(self,method,datatype,sku):
        header = {
            'storename':f'{self.storename}',
            'apikey':f'{self.apikey}',
            'apisecret':f'{self.apisecret}'
        }
    def post(self, method, sku, amount,cost=0):

        header = {
            'storename': f'{self.storename}',
            'apikey': f'{self.apikey}',
            'apisecret': f'{self.apisecret}'
        }

        url = 'https://api.zortout.com/api.aspx'

        payload = {'method': method, 'version': '3', 'warehousecode': 'W0001'}
        data = {"stocks": [{"sku": f"{sku}", "stock": amount,'cost':cost}]}
        print(data)
        res = requests.post(url=url, headers=header, params=payload, json=data)
        print(res.status_code)
        print(res)
        # for i in range(len(data['list'])):
        #     print(data['list'][i]['customerphone'])


def set_three(dep):
    if dep == 'muslin':
        web = Web(get_api_register(dep,'apikey'),get_api_register(dep,'apisecret'),get_api_register(dep,'storename'))
        task = """
        select stock.sku,stock_main.amount,stock.amount,cost.cost from stock
        inner join stock_main on stock.sku = stock_main.sku
        inner join cost on stock.sku = cost.sku
        where stock.amount > 0 and stock_main.amount < 2 and stock_main.image != 'None'
        """

        result = db.query_custom(task,'muslin')
        result = list(result.fetchall())
        sku = [i[0] for i in result]
        zortamount = [i[1] for i in result]
        amount = [i[2] for i in result]
        cost = [i[3] for i in result]

        for i in range(len(sku)):
            print(sku[i])
            zort_amount,stock_amount = get_amount(zortamount[i],amount[i])
            task = f"update {dep}.stock set amount = {stock_amount} where sku = '{sku[i]}'"
            db.query_commit(task)
            web.post("UPDATEPRODUCTAVAILABLESTOCKLIST",sku[i],zort_amount,cost[i] )
            db.query_commit(f"insert into {dep}.log values ('ระบบ','ดึงอัตโนมัติ รหัส {sku[i]}จากกลาง เหลือ {stock_amount} เป็น {zort_amount}',now())")

set_three('muslin')