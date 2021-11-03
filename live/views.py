from django import forms
from django.shortcuts import render
from django.http import HttpResponseRedirect
from .form import AddNewSku
from function import *
# Create your views here.

# FUNCTION


def Add_Process(sku, user):
    if '-' in sku:
        sku_task = sku.split('-')[0]
    else:
        sku_task = sku
    task_db = f"select sku from live_room where sku like '%{sku_task}%'"
    mycursor = db.query(task_db)
    myresult = list(mycursor.fetchall())
    if len(myresult) == 0:
        add(sku, user)
        return(f'{sku} , เพิ่มเข้าห้องไลฟ์เรียบร้อย !!')
    else:
        return('บนห้องไลฟ์มีแล้ว')


def del_Process(sku,user):
    result = delete(sku,user)
    if result:
        return f'ใน stock รหัส {sku} มีไซส์ {result} อยู่ '
    else:
        return f'ใน stock ไม่มีรหัส {sku} แล้ว'

# PAGE


def room(request):
    role = get_role(request,'role')
    task = f"""SELECT distinct(left(sku,6)),size,descript
                FROM {get_role(request,'department')}.stock_zort
                WHERE left(sku,6) NOT IN
                    (SELECT left(sku,6) 
                     FROM {get_role(request,'department')}.live_room) and amount > 0
    ORDER BY FIELD(size, 'XXS', 'XS', 'S', 'M', 'L', 'XL', 'XXL', 'F'), size"""
    mycursor = db.query(task)
    data = list(mycursor.fetchall())
    sku, size,chk = [], [], []
    for i in data:
        if i[0] not in chk:
            chk.append(i[0])
            # sku.append(i[0]+'-'+i[1])
            size.append(i[2])
    # size = list(zip(sku,size))
    size.sort()
    return render(request, 'main/result.html', {'data': size, 'host': host,'role':role})


def add_page(request, name):
    role = get_role(request,'role')
    def trans(var: str):
        return Add_Process(var.split(' ')[0], str(request.user))
    lst_sku = name.split(',')
    lst_sku = list(map(trans, lst_sku))
    return render(request, 'main/room.html', {'res': lst_sku, 'host': host,'role':role})


def del_page(request, name):
    role = get_role(request,'role')
    def trans(var: str):
        return del_Process(var.split(' ')[0],str(request.user))
    lst_sku = name.split(',')
    lst_sku = list(map(trans, lst_sku))
    return render(request, 'main/room.html', {'res': lst_sku, 'host': host, 'role':role })



def main_2(request):
    role = get_role(request,'role')
    task_db = f"select * from {get_role(request,'department')}.live_room"
    mycursor = db.query(task_db)
    myresult = mycursor.fetchall()
    if len(list(myresult)) == 0:
        res = 'ไม่มีบนห้องไลฟ์'
    lst = []
    for index, row in enumerate(myresult):
        lst.append(f"{row[0]} เวลา {row[1]} เพิ่มโดย {row[2]}")
    res = lst
    return render(request, 'main/room.html', {'res': res, 'host': host,'role':role})


def main(request):
    role = get_role(request,'role')
    if request.method == 'POST':
        form = AddNewSku(request.POST)
        res = []
        if form.is_valid():
            sku = form.cleaned_data['sku']
            mycursor = db.query(f"select * from  {get_role(request,'department')}.stock_zort\
                where sku like '%{sku}%' limit 1;")
            if mycursor.fetchone():
                # check METHOD check,add,delete
                if request.POST.get('check'):
                    if '-' in sku:
                        sku = sku.split('-')[0]
                    if len(sku) > 0:
                        task_db = f"select * from {get_role(request,'department')}.live_room where sku like '%{sku}%'"
                    else:
                        task_db = f"select * from {get_role(request,'department')}.live_room"
                    mycursor = db.query(task_db)
                    myresult = mycursor.fetchall()
                    if len(list(myresult)) == 0:
                        res = 'ไม่มีบนห้องไลฟ์'
                    lst = []
                    for index, row in enumerate(myresult):
                        lst.append(f"{row[0]} เวลา {row[1]} เพิ่มโดย {row[2]}")
                    res = lst
                elif request.POST.get('add'):
                    if sku == '':
                        res.append("โปรดใส่ SKU เข้าห้องไลฟ์")
                    else:
                        res.append(Add_Process(sku, str(request.user)))
                else:
                    sku = delete(sku,str(request.user))
                    res.append("ลบเรียบร้อย")
                    if sku:
                        res.append(
                            f"ลบเรียบร้อย\n\nข้างล่างมีรหัส Size {sku} อยู่ เอาขึ้นไปรีดด้วย ")
                    else:
                        res.append("ในสต็อคไม่มีให้รีดแล้ว")
        return render(request, 'main/room.html', {'res': res, 'host': host,'role':role})

    else:
        form = AddNewSku()
    return render(request, 'main/main.html', {"form": form, 'role': role})
