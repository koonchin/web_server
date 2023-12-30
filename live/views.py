from django import forms
from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect
from .form import AddNewSku
from function import *
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
# Create your views here.

# FUNCTION

def Add_Process(sku, user):
    if '-' in sku:
        sku_task = sku.split('-')[0]
    else:
        sku_task = sku
    task_db = f"select sku from {get_role(user,'department')}.live_room where sku like '%{sku_task}%'"
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
    dep = get_role(request,'department')

    task = f"""
    select {dep}.stock_main.sku, {dep}.stock_main.descript from {dep}.stock_main
    inner join {dep}.stock on {dep}.stock_main.sku = {dep}.stock.sku
    where {dep}.stock.amount + {dep}.stock_main.amount > 0 and left({dep}.stock_main.sku,6) not in (select left(sku,6) from {dep}.live_room)
    ORDER BY FIELD(stock_main.size, 'XXS', 'XS', 'S', 'M', 'L', 'F', 'XL', '2XL','3XL','4XL','5XL','6XL'), {dep}.stock_main.size
    """
    
    result = db.query(task)

    idsell_sorted = []
    sku_sorted = []

    result = list(result.fetchall())

    for i in range(len(result)):
        sku = result[i][0]
        descript = result[i][1]
        if not get_idsell(sku) in idsell_sorted:
            # sku_sorted.append(f"{sku}\t\t {descript}")
            sku_sorted.append(descript)
            idsell_sorted.append(get_idsell(sku))

    sku_sorted.sort()
    return render(request, 'main/result.html', {'data': sku_sorted,'role':role})

def add_page(request, name):
    role = get_role(request,'role')
    def trans(var: str):
        return Add_Process(var.split(' ')[0], str(request.user))
    lst_sku = name.split(',')
    lst_sku = list(map(trans, lst_sku))
    return render(request, 'main/room.html', {'res': lst_sku,'role':role})

def del_page(request, name):
    role = get_role(request,'role')
    def trans(var: str):
        return del_Process(var.split(' ')[0],str(request.user))
    lst_sku = name.split(',')
    lst_sku = list(map(trans, lst_sku))
    return render(request, 'main/room.html', {'res': lst_sku, 'role':role })

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
    return render(request, 'main/room.html', {'res': res,'role':role})

def prism(req,idsell):
    dep = 'maruay'
    task = f"""
            SELECT GROUP_CONCAT(data_size ORDER BY FIELD(size, 'XXS', 'XS', 'S', 'M', 'L', 'F', 'XL','XXL', '2XL','3XL','4XL','5XL','6XL'),size separator '\n') AS Result from {dep}.data_size
        where idsell = '{idsell}' group by idsell;
    """
    result = db.query(task)
    size = list(result.fetchone())
    size = ''.join(size)
    
    context = {}
    context['size'] = size
    return render(req,'main/prism.html',context=context)

def main(request):
    role = get_role(request,'role')
    if request.method == 'POST':
        form = AddNewSku(request.POST)
        res = []
        if form.is_valid():
            sku = form.cleaned_data['sku']
            mycursor = db.query(f"select * from  {get_role(request,'department')}.stock_main\
                where sku like '%{sku}%' limit 1;")
            if mycursor.fetchone():
                # check METHOD check,add,delete
                if request.POST.get('check'):
                    dep = get_role(request,'department')
                    if '-' in sku:
                        sku = sku.split('-')[0]
                    if len(sku) > 0:
                        task_db = f"select live_room.sku,stock_main.descript from {dep}.live_room \
                            inner join {dep}.stock_main on {dep}.live_room.sku = {dep}.stock_main.sku\
                                where sku like '%{sku}%'"
                    else:
                        task_db = f"select live_room.sku,stock_main.descript from {dep}.live_room\
                            inner join {dep}.stock_main on {dep}.live_room.sku = {dep}.stock_main.sku\
                            where comment is NULL\
                                "
                    mycursor = db.query(task_db)
                    myresult = mycursor.fetchall()
                    if len(list(myresult)) == 0:
                        res = 'ไม่มีบนห้องไลฟ์'
                    res = [f"{i[1]}" for i in myresult]
                    task_db = f"select live_room.sku,stock_main.descript,comment from {dep}.live_room\
                        inner join {dep}.stock_main on {dep}.live_room.sku = {dep}.stock_main.sku\
                        where comment is not NULL\
                            "
                    mycursor = db.query(task_db)
                    myresult = mycursor.fetchall()
                    notQc = [f"{i[1]} ({i[2]})" for i in myresult]
                elif request.POST.get('add'):
                    notQc = ''
                    if sku == '':
                        res.append("โปรดใส่ SKU เข้าห้องไลฟ์")
                    else:
                        res.append(Add_Process(sku, str(request.user)))
                else:
                    notQc = ''
                    sku = delete(sku,str(request.user))
                    res.append("ลบเรียบร้อย")
                    if sku:
                        res.append(
                            f"ลบเรียบร้อย\n\nข้างล่างมีรหัส Size {sku} อยู่ เอาขึ้นไปรีดด้วย ")
                    else:
                        res.append("ในสต็อคไม่มีให้รีดแล้ว")
        return render(request, 'main/room.html', {'res': res, 'role':role,'notQc':notQc})

    else:

        form = AddNewSku()
        task = "select live_room.sku,descript from live_room inner join stock_main on stock_main.sku = live_room.sku "
        result = db.query_custom(task,'muslin')
        result = list(result.fetchall())
        res = [i[1] for i in result]
    return render(request, 'main/main.html', {"form": form, 'role': role,'res':res})

def addnote(req):
    sku = req.POST.get('sku')
    sku = str(sku).split(' ')[0]
    note= req.POST.get('addnote')
    if note == '':
        db.query_commit(f"update muslin.live_room set comment = NULL where sku = '{sku}'")
    else:
        db.query_commit(f"update muslin.live_room set comment = '{note}' where sku = '{sku}'")
        
    return redirect("/live/main")
    
def export_live_excel(req):
    dep = get_role(req,'department')
    task = f'select sku,comment from live_room'
    path = export_excel(task,'live_room_data',dep)
    
    return redirect(f"/{path}")

def import_excel(request):
    dep = get_role(request,'department')
    if request.method == 'POST' and request.FILES['myfile']:
        db.query_commit(f'truncate {dep}.live_room')
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        path = insert_live_room(f"{settings.MEDIA_ROOT}/{myfile.name}")
        messages.success(request,'อัพสต็อกเรียบร้อย ... ')
    return redirect('/')