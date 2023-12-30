import time,os,shutil
from django.shortcuts import render, redirect
from function import *
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from zipfile import ZipFile
from os.path import basename
from django.http import HttpResponseRedirect
from app import settings
from .thread import AddLocationThread
def addtracking(req):
    dep = get_role(req,'department')
    web = Web(get_api_register(dep,'apikey'),get_api_register(dep,'apisecret'),get_api_register(dep,'storename'))

    ordernumber = req.POST.get('ordernumber')
    trackingno = req.POST.get('trackingno')
    res = web.add_tracking(ordernumber,trackingno)
    if res:
        messages.success(req,"update success .... ")
        barcode = [trackingno]
        ems.SubscribeByReceipt(barcode)
    else:
        messages.error(req,"error !!!!!!!!! ")

    return render(req,'stock.html')
def hello(req):
    print('here')
    remove_file()
    if req.method == 'POST':
        dbname = req.POST.get('dbname')
        task = f"""
                    UPDATE image.register_employee
                    SET department='{dbname}'
                    where user = '{str(req.user)}'
                """
        db.query_commit(task)
        if not req.user.is_anonymous:
            print(req.path_info)
            return HttpResponseRedirect(req.META.get('HTTP_REFERER', '/'))
    if get_role(req,'role') == 'key':
        return redirect('/keyorder/')
    if not req.user.is_anonymous:
        return render(req, 'index.html')
    else:
        return redirect('/login/')

def simple_upload(request):
    dep = get_role(request,'department')
    remove_file()
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        path = upstock(f"{settings.MEDIA_ROOT}/{myfile.name}",dep)
        messages.success(request,'อัพสต็อกเรียบร้อย ... ')
    return render(request, 'index.html')

def secretUpstock(req):
    dep = get_role(req,'department')
    return render(req,'secretupstock.html')

def upload_checkstock(request):
    dep = get_role(request,'department')
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        path = check_stock(f"{settings.MEDIA_ROOT}/{myfile.name}",dep)
        return redirect(f'/{path}')
    return render(request, 'upstock.html')

def upload_checkdiff(request):
    dep = get_role(request,'department')
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        path = get_diff_stock(f"{settings.MEDIA_ROOT}/{myfile.name}",dep)
        return redirect(f'/{path}')
    return render(request, 'upstock.html')

def UpdateExcel(request):
    dep = get_role(request,'department')
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        Start(f"{settings.MEDIA_ROOT}/{myfile.name}",dep)
        messages.success(request,"update เรียบร้อย ... ")
    return render(request, 'index.html')

def UpdateExcelAndBringBack(request):
    dep = get_role(request,'department')
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        # Start(f"{settings.MEDIA_ROOT}/{myfile.name}",dep)
        # update_vrich(dep)
        # bringback_from_vrich_increase_stock_live(dep,f"{settings.MEDIA_ROOT}/{myfile.name}")
        pull_order_vrich_to_zort(dep,f"{settings.MEDIA_ROOT}/{myfile.name}")
        messages.success(request,"update เรียบร้อย ... ")
    return render(request, 'index.html')

def UpdateOrderVrich(request):
    dep = get_role(request,'department')
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        StartTest(f"{settings.MEDIA_ROOT}/{myfile.name}",dep)
        messages.success(request,"update เรียบร้อย ... ")
    return render(request, 'index.html')

def KorkaiUpload(request):
    dep = get_role(request,'department')
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        path = Korkai(f"{settings.MEDIA_ROOT}/{myfile.name}")
        return redirect(f'/{path}')
    return render(request, 'index.html')

def transferVrich(req):
    dep  = get_role(req,'department')
    web = Web(get_api_register(dep,'apikey'),get_api_register(dep,'apisecret'),get_api_register(dep,'storename'))
    dep = get_role(req,'department')
    sec = datetime.datetime.now().timestamp()
    sec = str(sec).split('.')[0]
    if req.method == 'POST':
        if req.POST.get('ZortToVrich'):
            web.transfer_all_amount_with_condition(4,'W0001','W0003','โยกสต็อกไปไลฟ์')
            # db.query_commit(f"update {dep}.stock set amount = 0")
            messages.success(req,'update เรียบร้อย ...')
            return redirect('/secretUpstock/')
        elif req.POST.get('VrichToZort'):
            export_to_vrich(dep,f'{MEDIA_ROOT}/stock/{sec}')
            time.sleep(3)
            return redirect(f'/media/stock/{sec}.xlsx')

def postZeroFunction(req):
    dep = get_role(req,'department')
    if req.method == 'POST':
        post_zero_zort(dep)
        time.sleep(3)
        messages.success(req,'ลง 0 ทุกรายการเรียบร้อย ... ')
        return render(req,'upstock.html')

def check(req):
    return render(req, 'main.html')

def result(req):
    sku, descrip = check_tracking(req,req.GET.get("Tracking"))
    if sku and descrip:
        if sku != 'not':
            data = zip(sku, descrip)
            data2 = zip(sku, descrip)
            trackno = str(req.GET.get("Tracking"))
            return render(req, 'result.html', {'trackno': trackno,'data2': data2, 'data': data, 'host': host})
        else:
            messages.error(req,"ไม่พบ TrackingNo")
            return redirect('/check/')
        
    else:
        messages.error(req,"ยิงแล้ว")
        return redirect('/check/')
        
def barcode(req):
    sku = req.GET.get("Barcode")
    database = req.GET.get("inlineFormSelectPref")
    db_dict = {'ZORT':'stock_main','VRICH':'stock_vrich'}
    dep = get_role(req,"department")
    data = []
    try:
        if sku:
            data = db.query(
                f"SELECT SKU,descript from {dep}.{db_dict[str(database)]} where sku like '%{sku}%'")
            data = list(data)
            for i in range(len(data)):
                var = list(data[i])
                if 'ก' in var[0]:
                    var[0] = str(var[0]).replace('ก','QQ')
                data[i] = tuple(var)
    except:
        data = [(sku,'')]
    # if sku and database == 'ZORT':
    #     web = Web(get_api_register(dep,"apikey"),
    #               get_api_register(dep,"apisecret"),get_api_register(dep,"storename"))
    #     data = web.get("GETPRODUCTS", 'sku', sku)
    #     data1 = web.get("GETPRODUCTS", 'name', sku)
    #     data2 = []
    #     for i1,i2 in zip(data,data1):
    #         if str(i1) in str(i2):
    #             i2 = str(i2).replace(str(i1),'')
    #         data2.append((i1,i2))
    #     data = data2
    # elif sku:
    #     data = db.query(
    #         f"SELECT SKU,descript from {get_role(req,'department')}.stock_vrich where sku like '%{sku}%'")
    #     data = list(data)
    #     for i in range(len(data)):
    #         var = list(data[i])
    #         if 'ก' in var[0]:
    #             var[0] = str(var[0]).replace('ก','QQ')
    #         data[i] = tuple(var)
    return render(req, 'print.html', {'data': data})

def barcode_(req):
    sku = req.GET.getlist("checkSKU")
    amt = req.GET.get("Amount")
    amt = int(amt)
    data = []
    for i in sku:
        for row in range(int(amt)):
            data.append(i)
    print(data)
    return render(req, 'barcode.html', {'print': data, 'host': host,'backpage':'barcode'})

def checkstock(req):
    if req.method == 'POST':
        export = req.POST.get('export')
        dbname = req.POST.get("dbname")
        if export:
            a = datetime.datetime.now().__str__()
            a = a.replace('-', '_')
            a = a.replace(':', '_')
            a = a.replace('.', '')
            a = a.replace(' ', '')
            path = f'{settings.MEDIA_ROOT}/{a}.xlsx'
            # path = export_checkstock(f'{get_role(req,"department")}.`stock_zort_extra`', path)
            check = True
            while check:
                for i in os.listdir('media/'):
                    if f'{settings.MEDIA_ROOT}/{i}' == path:
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
                data = db.query(f'select descript from {get_role(req,"department")}.stock_main\
                    where sku = "{i}"')
                data = list(data.fetchall())[0][0]
                
                db.insert_into_duplicate(get_role(req,'department')+'.'+str(dbname),f"'{i}','{str(data)}'",int(amount[i]) * -1)
                # db.callproc("checkexistdeletezortmain",method[i].split('*')[0],int(amount[i]))
        if not method2 == '':
            method = str(method2).split('/')
            for i in method:

                data = db.query(f'select descript from {get_role(req,"department")}.stock_main\
                    where sku = "{str(i)}"')
                data = list(data.fetchall())[0][0]
                db.insert_into_duplicate(get_role(req,'department')+'.'+str(dbname),f"'{str(i)}','{str(data)}'",0)

        sku = req.POST.get('input')
        number = req.POST.get('amount')
        number = int(number)
        
        data = db.query(f'select descript from {get_role(req,"department")}.stock_main\
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

        # db.create_table(f"{get_role(req,'department')}.{name}")

        data = list(cursor.fetchall())
        result = db.query(f"select sku from {get_role(req,'department')}.stock_main")
        sku = [i[0] for i in list(result.fetchall())]
        content = {'data':data,
                    'name':name,
                    'skus':sku,
                    }
                    
    return render(req,'checkstock2.html',content)

def check_tracking(req,trackno):
    task = f"select * from {get_role(req,'department')}.order_main where trackingNo like '%{trackno}%'"
    myresult = db.query(task)
    if myresult.fetchone():
        return None,None
    web = Web(get_api_register(get_role(req,"department"),"apikey"),get_api_register(get_role(req,"department"),"apisecret"),get_api_register(get_role(req,"department"),"storename"))
    task_db = f"""select stock_vrich.sku,stock_vrich.descript
                        from stock_vrich
                        join deli_vrich
                        on stock_vrich.descript = deli_vrich.descript
                        where trackingNo like '%{trackno}%'"""
    result = db.query_custom(task_db,get_role(req,'department'))
    sku, descrp = [], []
    for i in result:
        if 'ก' in i[0]:
            sku.append(i[0].replace('ก', 'QQ'))
        else:
            sku.append(i[0])
        descrp.append(i[1])
    if sku and descrp:
        return (sku, descrp)
    else:
        task_db = f"""select sku,descript,idorder
                        from {get_role(req,'department')}.deli_zort
                        where trackingNo like '%{trackno}%'"""
        result = db.query(task_db)
        sku, descrp = [], []
        for i in result:
            web.update_track(int(i[2]))
            if 'ก' in i[0]:
                sku.append(i[0].replace('ก', 'QQ'))
            else:
                sku.append(i[0])
            descrp.append(i[1])
        if sku and descrp:
            return (sku,descrp)
        else:
            return 'not','not'

def confirm(req,track):
    web = Web(get_api_register(get_role(req,'department'),'apikey'),get_api_register(get_role(req,'department'),'apisecret'),get_api_register(get_role(req,'department'),'storename'))
    rows = db.query(f"""
    select IDorder,date,FBname,cstname,addr,tel,trackingNo,amount,total,paid,now(),descript,"VRICH",price,'packed'
    from {get_role(req,'department')}.deli_vrich where trackingNo like '%{track}%';""")
    rows = rows.fetchall()
    if not rows:
        task = f"select idorder from {get_role(req,'department')}.deli_zort where trackingno like '%{track}%'"
        result = db.query(task)
        result = list(result.fetchone())
        idOrder = result[0]
        idorder, date, FBname, cstname, addr, tel, trackingNo, amount, total, paid, now, descript, comment, price, status = web.get_track_data(int(idOrder),track)
        for i,p in zip(descript,price):
            task = f"""
            insert into {get_role(req,'department')}.order_main
            values ('{idorder}', '{date}', '{FBname}', '{cstname}', '{addr}', '{tel}', '{trackingNo}', '{amount}', '{total}', '{paid}', now(), '{i}', 'ZORT', '{p}', '{status}')
            """
            db.query_commit(task)
    else:
        task = f"""
        insert into {get_role(req,'department')}.order_main(IDorder, date, FBName, cstname, addr, tel, trackingNo, amount, total, paid,packed_time, descript, Comment, price,status)
        values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
        """
        db.query_commit_many(task,rows)
    return render(req,'main.html')

def remove_file():
    for i in os.listdir("media/"):
        if i.endswith("xlsx") or i.endswith("xlsm"):
            os.remove(f"{settings.MEDIA_ROOT}/{i}")

def countprint(req):
    dep = get_role(req,'department')
    if req.method == "POST":
        web = Web(get_api_register(dep,'apikey'),get_api_register(dep,'apisecret'),get_api_register(dep,'storename'))
        leng = web.get_track(dep)
        messages.success(req,f"ปริ้นท์ {leng} ใบ ... ")
    else:
        miss = req.GET.get("stock_check_miss")
        printed = req.GET.get("stock_check_print")
        excel = req.GET.get("excel")
        date_filter = req.GET.get("date")
        if miss:
            task = f"select * from {dep}.deli_zort where status = 'Pending' and cast(orderdate as Date) = '{date_filter}' and paymentstatus = 'Paid'"
            result = db.query(task)
            result = list(result.fetchall())
        elif printed:
            task = f"select * from {dep}.deli_zort where printed = '1' and cast(printedtime as Date) = '{date_filter}'"
            result = db.query(task)
            result = list(result.fetchall())
        else:
            for i in os.listdir(f'{settings.MEDIA_ROOT}/stock/'):
                if i.endswith('.xlsx'):
                    os.remove(f'{settings.MEDIA_ROOT}/stock/{i}')

            task = f"select * from {dep}.deli_zort where orderdate = '{date_filter}'"
            today_name = datetime.datetime.today().strftime('%Y_%m_%d')
            path = export_excel(task,today_name)
            return redirect(path)
        context = {
            'data':result
        }
    return render(req,'stock.html',context)

def stock_check(req):
    return render(req,'stock.html')

def counted_print(req):
    dep = get_role(req,'department')
    web = Web(get_api_register(dep,'apikey'),get_api_register(dep,'apisecret'),get_api_register(dep,'storename'))
    leng = web.get_track(dep)
    messages.success(req,f"ปริ้นท์ออกมา {leng} ใบ ... ")
    return render(req,'index.html')

def upstock_page(request):
    sec = datetime.datetime.now().timestamp()
    sec = str(sec).split('.')[0]
    if request.method == 'POST':
        dep = get_role(request,'department')
        remove_file()
        if request.method == 'POST' and request.FILES['myfile']:
            myfile = request.FILES['myfile']
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            path = fullFill(f"{settings.MEDIA_ROOT}/{myfile.name}",sec,dep)
            return redirect(f'/{path}')
    return render(request,"upstock.html")

def download_zip(sec):
    main(f'{settings.MEDIA_ROOT}/write_image')
    # for i in os.listdir(f'{settings.MEDIA_ROOT}/write_image/'):
    #     if not os.path.isfile(f'{settings.MEDIA_ROOT}/write_image/{i}'):
    #         for i2 in os.listdir(f'{settings.MEDIA_ROOT}/write_image/{i}'):
    #             if os.path.isfile(f'{settings.MEDIA_ROOT}/write_image/{i}/{i2}'):
    #                 if f'{settings.MEDIA_ROOT}/write_image/{i}/{i2}'.endswith('.png') or f'{settings.MEDIA_ROOT}/write_image/{i}/{i2}'.endswith('.jpg'):
    #                     os.remove(f'{settings.MEDIA_ROOT}/write_image/{i}/{i2}')
                
    with ZipFile(f'{settings.MEDIA_ROOT}/write_image/{sec}/{sec}.zip', 'w') as zipObj:
        # Iterate over all the files in directory
        for folderName, subfolders, filenames in os.walk(f'{settings.MEDIA_ROOT}/write_image/{sec}'):
            for filename in filenames:
                if filename.lower().endswith('.png') or filename.lower().endswith('.jpg'):
                    # create complete filepath of file in directory
                    filePath = os.path.join(folderName, filename)
                    # Add file to zip
                    zipObj.write(filePath, basename(filePath))

    for i in os.listdir(f'{settings.MEDIA_ROOT}/write_image/{sec}'):
        if i.endswith('.png') or i.endswith('.jpg'):
            os.remove(f'{settings.MEDIA_ROOT}/write_image/{sec}/{i}')
    return sec

def upload_image(request):
    main('media/write_image')
    if request.method == 'POST' and request.FILES['myfile']:
        sec = datetime.datetime.now().timestamp()
        sec = str(sec).split('.')[0]
        os.makedirs(f'{settings.MEDIA_ROOT}/write_image/{sec}', exist_ok=True)
        myfile = request.FILES.getlist('myfile')
        custom = request.POST.get('custom')
        if custom:
            name = custom
        else:
            name = None
        for i in myfile:
            fs = FileSystemStorage()
            
            filename = fs.save(f"write_image/{sec}/{i.name}", i)

            if name:
                write_image_top_right(f"{settings.MEDIA_ROOT}/write_image/{sec}/{i.name}",name)
            else:
                write_image_top_right(f"{settings.MEDIA_ROOT}/write_image/{sec}/{i.name}",i.name.split('.')[0].strip())
        if not len(myfile) == 1:
            sec = download_zip(sec)

            return redirect(f'/media/write_image/{sec}/{sec}.zip')
        
        else:
            return redirect(f"/media/write_image/{sec}/{i.name}")
        # path = upstock(f"{settings.MEDIA_ROOT}/{myfile.name}",request)
        # return redirect(f'/{path}')

    return render(request, 'uploadimage.html')

def AddimageZort(request):
    dep = get_role(request,'department')
    web = Web(get_api_register(dep,'apikey'),get_api_register(dep,'apisecret'),get_api_register(dep,'storename'))
    main(f'{settings.MEDIA_ROOT}/zort')
    if request.method == 'POST' and request.FILES['myfilezort']:
        sec = datetime.datetime.now().timestamp()
        sec = str(sec).split('.')[0]
        os.makedirs(f'{settings.MEDIA_ROOT}/zort/{sec}', exist_ok=True)
        myfile = request.FILES.getlist('myfilezort')
        for i in myfile:
            fs = FileSystemStorage()
            filename = fs.save(f"zort/{sec}/{i.name}", i)
            task = f'select sku from data_size where idsell = "{str(i.name).split(".")[0]}"'
            result = db.query_custom(task,dep)
            result = list(result.fetchall())
            for row in result:
                print(row[0])
                try:
                    web.addImage(row[0],f"{settings.MEDIA_ROOT}/zort/{sec}/{i.name}")
                except:
                    pass
    return render(request, 'uploadimage.html')

# main function
def main(path):

    # initializing the count
    deleted_folders_count = 0
    deleted_files_count = 0

    # specify the path

    # specify the days

    # converting days to seconds
    # time.time() returns current time in seconds
    seconds = time.time() - (120)

    # checking whether the file is present in path or not
    if os.path.exists(path):

        # iterating over each and every folder and file in the path
        for root_folder, folders, files in os.walk(path):

            # comparing the days
            if seconds >= get_file_or_folder_age(root_folder):

                # removing the folder
                remove_folder(root_folder)
                deleted_folders_count += 1  # incrementing count

                # breaking after removing the root_folder
                break

            else:

                # checking folder from the root_folder
                for folder in folders:

                    # folder path
                    folder_path = os.path.join(root_folder, folder)

                    # comparing with the days
                    if seconds >= get_file_or_folder_age(folder_path):

                        # invoking the remove_folder function
                        remove_folder(folder_path)
                        deleted_folders_count += 1  # incrementing count

                # checking the current directory files
                for file in files:

                    # file path
                    file_path = os.path.join(root_folder, file)

                    # comparing the days
                    if seconds >= get_file_or_folder_age(file_path):

                        # invoking the remove_file function
                        remove_file_path(file_path)
                        deleted_files_count += 1  # incrementing count

        else:

            # if the path is not a directory
            # comparing with the days
            if seconds >= get_file_or_folder_age(path):

                # invoking the file
                remove_file_path(path)
                deleted_files_count += 1  # incrementing count

    else:

        pass

def remove_folder(path):
    # removing the folder
    shutil.rmtree(path)

def remove_file_path(path):
    os.remove(path)

def get_file_or_folder_age(path):

    # getting ctime of the file/folder
    # time will be in seconds
    ctime = os.stat(path).st_ctime

    # returning the time
    return ctime

def exportCheckin(req):
    
    current_date = datetime.date.today()
    current_month = current_date.strftime("%Y-%m-01")
    dep = get_role(req,'department')
    sec = datetime.datetime.now().timestamp()
    sec = str(sec).split('.')[0]
    table_break(current_month,sec)
    return redirect(f'/media/stock/{sec}.xlsx')

def exportrma(req):
    dep = get_role(req,'department')
    sec = datetime.datetime.now().timestamp()
    sec = str(sec).split('.')[0]
    reportrma(sec,dep)
    return redirect(f'/media/stock/{sec}.xlsx')

def managelive(req):
    dep = get_role(req,'department')
    sec = datetime.datetime.now().timestamp()
    sec = str(sec).split('.')[0]
    manageStockLive(sec)
    return redirect(f'/media/stock/{sec}.xlsx')

def share_barcode(req):
    if req.method == 'POST':
        data,SKU = [],[]
        s_ref_code = req.POST.get('s_ref_code')
        b_ref_code = req.POST.get('b_ref_code')
        for key, value in req.POST.items():
            if key.endswith('_amount'):  # Identify input fields by '_amount' suffix
                # Parse the key to extract pattern, dataMessage, size, and amount
                sku = key.split('_amount')[0]
                print(sku,req.POST[f"{sku}_amount"])
                SKU.append(sku)

        for i in SKU:
            for row in range(int(req.POST[f"{i}_amount"])):
                data.append(i)
                
        return render(req, 'barcode.html', {'print': data, 'host': host,'backpage':'share-barcode'})
    return render(req,'share_barcode.html')

def pull_order(req):
    if req.method == 'POST':
        dep = get_role(req,'department')
        web = Web(get_api_register(dep,'apikey'),get_api_register(dep,'apisecret'),get_api_register(dep,'storename'))
        web.get_track_2(dep)
        messages.success(req,'ดึงออเดอร์ zort สำเร็จ .... ')
        return redirect('/')

def barcode_scanner_view(req):
    dep = get_role(req, 'department')

    if req.method == 'POST':
        sku = req.POST.get('skuInput')
        location = req.POST.get('locationInput')
        sku = str(sku).upper()
        location = str(location).upper()

        AddLocationThread(dep, sku, location).start()
        print(dep,sku,location)
        messages.success(req, "Task has been started in the background.")
        return redirect('/barcode-scanner/')
    
    return render(req, 'scan.html')

from django.http import JsonResponse

def api_data(req):
    dep = get_role(req, 'department')
    patterns = list(req.GET.get('patterns'))
    sizes = list(req.GET.get('sizes'))

    if patterns and sizes:
        ref_code = req.GET.get('ref_code')
        satin_code = {'N', 'T', 'L', 'P', 'W', 'V', 'U', 'M', 'K', 'R'}

        is_a_pattern = any(pattern in satin_code for pattern in patterns)
        b = 'satin_sku' if is_a_pattern else 'bamboo_sku'

        # task = f'''
        # SELECT SUBSTRING(idsell, 2) AS extracted_text
        # FROM data_size
        # WHERE sku LIKE '{b}%'
        # ORDER BY CAST(SUBSTRING(idsell, 2) AS SIGNED) DESC;'''
        task = f'''
        select {b} from reserve_sku  where status = 2
        order by cast({b} as SIGNED) DESC'''
        result = db.query_custom(task, 'muslin')
        result = result.fetchall()
        if not result:
            task = f'''
            select {b} from reserve_sku  where status = 0 and {b} is not NULL
            order by cast({b} as SIGNED) DESC'''
            result = db.query_custom(task, 'muslin')
            result = result.fetchall()[0][0]
            result = str(int(result) + 1).zfill(4)
            task_dict = {'satin_sku':f'"{result}",NULL','bamboo_sku':f'NULL,"{result}"'}
            task_commit = f'insert into muslin.reserve_sku value (0,"factory_name",{task_dict[b]},now(),1,"{ref_code}")'
            db.query_commit(task_commit)
        else:
            result = int(result[0][0])
            result = str(result).zfill(4)
            task_commit = f"update muslin.reserve_sku set user = 'factory_name',date=now(),status = 1,ref_code = '{ref_code}' where {b} = {result}"
            db.query_commit(task_commit)
        data = {'message': result}
        return JsonResponse(data)
    return JsonResponse({})

def cancel_reserve(req):
    ref_code = req.GET.get('ref_code')
    db.query_commit(f'update muslin.reserve_sku set ref_code = NULL,date = NULL,user = NULL , status = 2 where ref_code = "{ref_code}"')
    return JsonResponse({})
