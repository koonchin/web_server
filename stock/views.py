import time
from django.shortcuts import render, redirect
from requests.api import get
from function import *
# Create your views here.

def hello(req):
    if req.method == 'POST':
        dbname = req.POST.get('dbname')
        task = f"""
                    UPDATE image.register_employee
                    SET department='{dbname}'
                    where user = '{str(req.user)}'
                """
        db.query_commit(task)
    if not req.user.is_anonymous:
        return render(req, 'index.html')
    else:
        return redirect('/login/')

def check(req):
    return render(req, 'main.html')

def result(req):
    sku, descrip = check_tracking(req,req.GET.get("Tracking"))
    trackno = zip(sku, descrip)
    trackno2 = zip(sku, descrip)
    return render(req, 'result.html', {'trackno': trackno, 'data': trackno2, 'host': host})

def barcode(req):
    sku = req.GET.get("Barcode")
    database = req.GET.get("inlineFormSelectPref")
    data = []
    if sku and database == 'ZORT':
        web = Web(get_role(req,'apikey'),
                  get_role(req,'apisecret'), get_role(req,'storename'))
        data = web.get("GETPRODUCTS", 'sku', sku)
        data1 = web.get("GETPRODUCTS", 'name', sku)
        data2 = []
        for i1,i2 in zip(data,data1):
            if str(i1) in str(i2):
                i2 = str(i2).replace(str(i1),'')
            data2.append((i1,i2))
        data = data2
    elif sku:
        data = db.query(
            f"SELECT SKU,descript from {get_role(req,'department')}.stock_vrich where sku like '%{sku}%'")
        data = list(data)
        for i in range(len(data)):
            var = list(data[i])
            if 'ก' in var[0]:
                var[0] = str(var[0]).replace('ก','QQ')
            data[i] = tuple(var)
    return render(req, 'print.html', {'data': data})

def barcode_(req):
    sku = req.GET.getlist("checkSKU")
    amt = req.GET.get("Amount")
    amt = int(amt)
    data = []
    for i in sku:
        for row in range(int(amt)):
            data.append(i)
    return render(req, 'barcode.html', {'print': data, 'host': host})

def checkstock(req):
    if req.method == 'POST':
        export = req.POST.get('export')
        dbname = req.POST.get("dbname")
        print(dbname)
        if export:
            a = datetime.datetime.now().__str__()
            a = a.replace('-', '_')
            a = a.replace(':', '_')
            a = a.replace('.', '')
            a = a.replace(' ', '')
            path = f'media/{a}.xlsx'
            path = export_checkstock(f'{get_role(req,"department")}.`stock_zort_extra`', path)
            check = True
            print(path)
            while check:
                for i in os.listdir('media/'):
                    if f'media/{i}' == path:
                        check = False
                time.sleep(3)
            return redirect(f'/'+path)

        method = req.POST.get("type")
        method2 = req.POST.get("type2")
        # กดลด
        if not method == '':
            amount = []
            method = str(method).split('/')
            for i in method:
                amount.append(i.split('*')[-1])
            for i in range(len(method)-1):

                i = method[i].split('*')[0]
                data = db.query(f'select descript from {get_role(req,"department")}.stock_zort\
                    where sku = "{i}"')
                data = list(data.fetchall())[0][0]
                
                db.insert_into_duplicate(get_role(req,'department')+'.'+str(dbname),f"'{i}','{str(data)}'",int(amount[i]) * -1)
                # db.callproc("checkexistdeletezortmain",method[i].split('*')[0],int(amount[i]))
                # print("checkexistdeletezortmain",method[i].split('*')[0],int(amount[i]))
        if not method2 == '':
            method = str(method2).split('/')
            for i in method:

                data = db.query(f'select descript from {get_role(req,"department")}.stock_zort\
                    where sku = "{str(i)}"')
                data = list(data.fetchall())[0][0]
                db.insert_into_duplicate(get_role(req,'department')+'.'+str(dbname),f"'{str(i)}','{str(data)}'",0)

        sku = req.POST.get('input')
        number = req.POST.get('amount')
        number = int(number)
        
        data = db.query(f'select descript from {get_role(req,"department")}.stock_zort\
            where sku = "{str(sku)}"')
        data = list(data.fetchall())[0][0]
        db.insert_into_duplicate(get_role(req,'department')+'.'+str(dbname),f"'{str(sku)}','{str(data)}'",int(number))

        # db.callproc("checkexistpluszortmain",str(sku),int(number))
        cursor = db.query(f"select * from {get_role(req,'department')}.stock_zort_extra where amount > 0")
        data = list(cursor.fetchall())
        content = {'data':data}
    else:
        name = req.GET.get('name')
        if not name:
            name=  ''
        cursor = db.query(f"select * from {get_role(req,'department')}.stock_zort_extra where amount > 0")

        db.create_table(f"{get_role(req,'department')}.{name}")

        data = list(cursor.fetchall())
        content = {'data':data,
                    'name':name
                    }
    return render(req,'checkstock.html',content)

def check_tracking(req,trackno):
    print('in check tracking')
    task_db = f"""select stock_vrich.sku,stock_vrich.descript
                        from stock_vrich
                        join deli_vrich
                        on stock_vrich.descript = deli_vrich.descript
                        where trackingNo like '%{trackno}%'"""
    mycursor = db.query_custom(task_db,get_role(req,'department'))
    result = list(mycursor.fetchall())
    sku, descrp = [], []
    for i in result:
        if 'ก' in i[0]:
            sku.append(i[0].replace('ก', 'QQ'))
        else:
            sku.append(i[0])
        descrp.append(i[1])

    return (sku, descrp)


