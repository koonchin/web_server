from django.contrib import messages
from django.shortcuts import render,redirect
from function import *
import os,shutil,time
from zipfile import ZipFile
from os.path import basename
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
@csrf_exempt
def image_admin(req):
    user = req.user
    dep = get_role(req,'department')
    downloads = None
    result = db.query(f"select distinct(size) from {dep}.stock_main where size != '' ORDER BY FIELD(size, 'XXS', 'XS', 'S', 'M', 'L', 'F', 'XL', '2XL','3XL', '4XL','5XL','6XL')")
    result = list(result.fetchall())
    sizes = [i[0] for i in result]
    if req.method == 'POST':

        sku = req.POST.get("sku")
        name = req.POST.get("name")
        size = str(req.POST.get("size"))

        breastmax = float(req.POST.get("breastmax"))
        wrestmax =float(req.POST.get("wrestmax"))
        hipmax = float(req.POST.get("hipmax"))
        breastmin = float(req.POST.get("breastmin"))
        wrestmin = float(req.POST.get("wrestmin"))
        hipmin = float(req.POST.get("hipmin"))

        downloads = req.POST.getlist('checkSKU')
        check_vrich = req.POST.getlist('checkVRICH')

        if size:
            task = f"""select stock_main.*,shirts, pants, crotch, leg,stock.amount from {dep}.stock_main
            inner join {dep}.stock on stock_main.sku = stock.sku
            inner join {dep}.stock_detailsize on stock_main.sku = stock_detailsize.sku
                where stock_main.sku like '%{sku}%'
                and stock_main.size = '{size}'
                and stock_main.descript like '%{name}%'
                and stock_main.breast >= {breastmin} and stock_main.breast <= {breastmax}
                and stock_main.maxwrest between {wrestmin} and {wrestmax}
                and stock_main.hip >= {hipmin} and stock_main.hip <= {hipmax}
                order by stock.amount + stock_main.amount DESC """
        else:
            task = f"""select stock_main.*,shirts, pants, crotch, leg,stock.amount from {dep}.stock_main
            inner join {dep}.stock on stock_main.sku = stock.sku
            inner join {dep}.stock_detailsize on stock_main.sku = stock_detailsize.sku
                    where stock_main.sku like '%{sku}%' 
                    and stock_main.descript like '%{name}%'
                    and stock_main.breast >= {breastmin} and stock_main.breast <= {breastmax}
                    and stock_main.maxwrest between {wrestmin} and {wrestmax}
                    and stock_main.hip >= {hipmin} and stock_main.hip <= {hipmax}
                    order by stock_main.amount + stock.amount DESC """
    else:
        task = f"""select stock_main.*,shirts, pants, crotch, leg,stock.amount from {dep}.stock_main
        inner join {dep}.stock on stock_main.sku = stock.sku
        inner join {dep}.stock_detailsize on stock_main.sku = stock_detailsize.sku
                 order by stock_main.amount + stock.amount DESC limit 100;"""
    
    task2 = f"""
            SELECT idsell,GROUP_CONCAT(data_size ORDER BY FIELD(size, 'XXS', 'XS', 'S', 'M', 'L', 'F', 'XL','XXL', '2XL','3XL','4XL','5XL','6XL'),size separator '\n') AS Result from {dep}.data_size
        group by idsell;
    """
    
    mycursor = db.query_custom(task2,dep)
    data_size = list(mycursor.fetchall())
    size_dict = {}
    for i in data_size:
        size_dict[i[0]] = i[1]
    mycursor = db.query_custom(task,dep)
    data = list(mycursor.fetchall())
    if not data:
            
        if req.method == 'POST':

            sku = req.POST.get("sku")
            name = req.POST.get("name")
            size = str(req.POST.get("size"))

            breastmax = float(req.POST.get("breastmax"))
            wrestmax =float(req.POST.get("wrestmax"))
            hipmax = float(req.POST.get("hipmax"))
            breastmin = float(req.POST.get("breastmin"))
            wrestmin = float(req.POST.get("wrestmin"))
            hipmin = float(req.POST.get("hipmin"))

            downloads = req.POST.getlist('checkSKU')

            if size:
                task = f"""select stock_main.*,shirts, pants, crotch, leg,0 from {dep}.stock_main
                    inner join {dep}.stock on stock_main.sku = stock.sku
                    inner join {dep}.stock_detailsize on stock_main.sku = stock_detailsize.sku
                    where stock_main.sku like '%{sku}%'
                    and stock_main.size = '{size}'
                    and stock_main.descript like '%{name}%'
                    and stock_main.breast >= {breastmin} and stock_main.breast <= {breastmax}
                    and stock_main.maxwrest between {wrestmin} and {wrestmax}
                    and stock_main.hip >= {hipmin} and stock_main.hip <= {hipmax}
                    order by stock_main.amount + stock.amount DESC """
            else:
                task = f"""select stock_main.*,shirts, pants, crotch, leg,0 from {dep}.stock_main
                        inner join {dep}.stock on stock_main.sku = stock.sku
                        inner join {dep}.stock_detailsize on stock_main.sku = stock_detailsize.sku
                        where stock_main.sku like '%{sku}%' 
                        and stock_main.descript like '%{name}%'
                        and stock_main.breast >= {breastmin} and stock_main.breast <= {breastmax}
                        and stock_main.maxwrest between {wrestmin} and {wrestmax}
                        and stock_main.hip >= {hipmin} and stock_main.hip <= {hipmax}
                        order by stock_main.amount + stock.amount DESC """
        else:
            task = f"""select {dep}.stock_main.*,shirts, pants, crotch, leg,0 from {dep}.stock_main
                        inner join stock_detailsize on stock_detailsize.sku = stock_main.sku
                    order by stock_main.amount + stock.amount DESC limit 100;"""
        mycursor = db.query_custom(task,dep)
        data = list(mycursor.fetchall())
        
    if downloads:
        print(task)
        sum_amount = 0
        for i in range(len(data)):
            try:
                amount = int(data[i][15]) + int(data[i][10])
            except:
                amount = 0
            sum_amount += amount
        if sum_amount > 0:
            sec = download_zip(user,data)
            return redirect(f'/media/image_admin/{user}/{sec}.zip')
        else:
            messages.error(req," Zip ไม่มีรูป ... ")
        
    for i in range(len(data)):
        data[i] += (i+1,)
        var = list(data[i])
        try:
            var[9] = size_dict[get_idsell(var[0])]
        except:
            pass
        if len(var[9]) < 10:
            var[9] = ''
        data[i] = tuple(var)

    # if not downloads:

    minbreast = db.query(f"select min(breast) from {get_role(req,'department')}.stock_main where breast != ''").fetchone()[0]
    maxbreast = db.query(f"select max(breast) from {get_role(req,'department')}.stock_main where breast != ''").fetchone()[0]
    minwrest = db.query(f"select min(minwrest) from {get_role(req,'department')}.stock_main where minwrest != ''").fetchone()[0]
    maxwrest = db.query(f"select max(maxwrest) from {get_role(req,'department')}.stock_main where maxwrest != ''").fetchone()[0]
    minhip = db.query(f"select min(hip) from {get_role(req,'department')}.stock_main where hip != ''").fetchone()[0]
    maxhip = db.query(f"select max(hip) from {get_role(req,'department')}.stock_main where hip != ''").fetchone()[0]

    task = f'''SELECT data_size.idsell,GROUP_CONCAT(data_size ORDER BY FIELD(data_size.size, 'XXS', 'XS', 'S', 'M', 'L', 'F', 'XL','XXL', '2XL','3XL','4XL','5XL','6XL'),data_size.size separator '\n')
                AS Result from data_size
                inner join stock_vrich on stock_vrich.sku = data_size.sku where stock_vrich.amount > 0
                group by data_size.idsell;'''
                
    mycursor = db.query_custom(task,dep)
    data_size = list(mycursor.fetchall())
    live_dict = {}

    for i in data_size:
        live_dict[i[0]] = replace_and_split(i[1])

    for i in range(len(data)):
        var = list(data[i])
        try:
            data[i] = data[i] + (live_dict[get_idsell(var[0])],)
        except:
            data[i] = data[i] + ('',)

    content = {'data': data,
                'breastmin':minbreast,
                'breastmax':maxbreast,
                'wrestmin':minwrest,
                'wrestmax':maxwrest,
                'hipmin':minhip,
                'hipmax':maxhip,
                'sizes':sizes
                }
                
    return render(req, 'image_table2.html', content)

def image_admin_with_slug(req,slug):

    dep = get_role(req,'department')
    result = db.query(f"select distinct(size) from {dep}.stock_main where size != '' ORDER BY FIELD(size, 'XXS', 'XS', 'S', 'M', 'L', 'F', 'XL', '2XL','3XL', '4XL','5XL','6XL')")
    result = list(result.fetchall())
    sizes = [i[0] for i in result]

    sku = slug

    task = f"""select stock_main.*, shirts, pants, crotch, leg,stock.amount from {dep}.stock_main
    inner join {dep}.stock on stock_main.sku = stock.sku
    inner join {dep}.stock_detailsize on stock_main.sku = stock_detailsize.sku
            where stock_main.sku like '%{sku}%' 
            order by stock_main.amount + stock.amount DESC """

    task2 = f"""
            SELECT idsell,GROUP_CONCAT(data_size ORDER BY FIELD(size, 'XXS', 'XS', 'S', 'M', 'L', 'F', 'XL','XXL', '2XL','3XL','4XL','5XL','6XL'),size separator '\n') AS Result from {dep}.data_size
        group by idsell;
    """
    mycursor = db.query(task2)
    data_size = list(mycursor.fetchall())
    size_dict = {}
    for i in data_size:
        size_dict[i[0]] = i[1]
    mycursor = db.query(task)
    # items_per_page = 10

    # paginator = Paginator(mycursor.fetchall(), items_per_page)
    data = list(mycursor.fetchall())
        
    for i in range(len(data)):
        data[i] += (i+1,)
        var = list(data[i])
        try:
            var[9] = size_dict[get_idsell(var[0])]
        except:
            pass
        if len(var[9]) < 10:
            var[9] = ''
        data[i] = tuple(var)

    # if not downloads:

    minbreast = db.query(f"select min(breast) from {get_role(req,'department')}.stock_main where breast != ''").fetchone()[0]
    maxbreast = db.query(f"select max(breast) from {get_role(req,'department')}.stock_main where breast != ''").fetchone()[0]
    minwrest = db.query(f"select min(minwrest) from {get_role(req,'department')}.stock_main where minwrest != ''").fetchone()[0]
    maxwrest = db.query(f"select max(maxwrest) from {get_role(req,'department')}.stock_main where maxwrest != ''").fetchone()[0]
    minhip = db.query(f"select min(hip) from {get_role(req,'department')}.stock_main where hip != ''").fetchone()[0]
    maxhip = db.query(f"select max(hip) from {get_role(req,'department')}.stock_main where hip != ''").fetchone()[0]

    task = f'''SELECT data_size.idsell,GROUP_CONCAT(data_size ORDER BY FIELD(data_size.size, 'XXS', 'XS', 'S', 'M', 'L', 'F', 'XL','XXL', '2XL','3XL','4XL','5XL','6XL'),data_size.size separator '\n')
                AS Result from data_size
                inner join stock_vrich on stock_vrich.sku = data_size.sku where stock_vrich.amount > 0
                group by data_size.idsell;'''
                
    mycursor = db.query_custom(task,dep)
    data_size = list(mycursor.fetchall())
    live_dict = {}

    for i in data_size:
        live_dict[i[0]] = replace_and_split(i[1])

    for i in range(len(data)):
        var = list(data[i])
        try:
            data[i] = data[i] + (live_dict[get_idsell(var[0])],)
        except:
            data[i] = data[i] + ('',)
    content = {'data': data,
                'breastmin':minbreast,
                'breastmax':maxbreast,
                'wrestmin':minwrest,
                'wrestmax':maxwrest,
                'hipmin':minhip,
                'hipmax':maxhip,
                'sizes':sizes
                }

    # Create a Paginator object

    # Get the requested page number from the URL parameters
    # page_number = req.GET.get('page')

    # Get the requested page of data
    # page_obj = paginator.get_page(page_number)
    # content['page_obj'] = page_obj

    return render(req, 'image_table2.html', content)
   
    # else:
        # sec = download_zip(data)
        # return redirect(f'/{settings.MEDIA_ROOT}/image_admin/{sec}/{sec}.zip')
# about api
@csrf_exempt
def download_zip(user,myresult):
    main(f'{settings.MEDIA_ROOT}/image_admin')
    sec = datetime.datetime.now().timestamp()
    sec = str(sec).split('.')[0]
    os.makedirs(f'{settings.MEDIA_ROOT}/image_admin/{user}/{sec}', exist_ok=True)
    for i in os.listdir(f'{settings.MEDIA_ROOT}/image_admin/{user}/'):
        if not os.path.isfile(f'{settings.MEDIA_ROOT}/image_admin/{user}/{i}'):
            for i2 in os.listdir(f'{settings.MEDIA_ROOT}/image_admin/{user}/{i}'):
                if os.path.isfile(f'{settings.MEDIA_ROOT}/image_admin/{user}/{i}/{i2}'):
                    if f'{settings.MEDIA_ROOT}/image_admin/{user}/{i}/{i2}'.endswith('.png'):
                        os.remove(f'{settings.MEDIA_ROOT}/image_admin/{user}/{i}/{i2}')
                
    myresult.sort(key=lambda x: x[0])

    # Initialize var to store unique IDs
    var = []

    for i in range(len(myresult)):
        try:
            amount = int(myresult[i][15]) + int(myresult[i][10])
        except:
            amount = 0
        if not myresult[i][3] == 'None' and amount > 0:
            if not get_idsell(myresult[i][0]) in var:
                var.append(get_idsell(myresult[i][0]))
                if amount == 1:
                    try:
                        with open(f'{settings.MEDIA_ROOT}/image_admin/{user}/{sec}/{myresult[i][0]}.png', 'wb') as f:
                            f.write(convert_url_to_bytes(myresult[i][3]))
                            f.close()
                            write_image(f'{settings.MEDIA_ROOT}/image_admin/{user}/{sec}/{myresult[i][0]}.png','ตัวสุดท้าย')
                    except:
                        print(myresult[i][0],'error')
                else:
                    with open(f'{settings.MEDIA_ROOT}/image_admin/{user}/{sec}/{myresult[i][0]}.png', 'wb') as f:
                        try:
                            f.write(convert_url_to_bytes(myresult[i][3]))
                        except:
                            # print(myresult[i][0],myresult[i][3])
                            pass
                        f.close()
                
    with ZipFile(f'{settings.MEDIA_ROOT}/image_admin/{user}/{sec}.zip', 'w') as zipObj:
        # Iterate over all the files in directory
        for folderName, subfolders, filenames in os.walk(f'{settings.MEDIA_ROOT}/image_admin/{user}/{sec}'):
            for filename in filenames:
                if filename.endswith('.png'):
                    # create complete filepath of file in directory
                    filePath = os.path.join(folderName, filename)
                    # Add file to zip
                    zipObj.write(filePath, basename(filePath))

    for i in os.listdir(f'{settings.MEDIA_ROOT}/image_admin/{user}/{sec}'):
        if i.endswith('.png'):
            os.remove(f'{settings.MEDIA_ROOT}/image_admin/{user}/{sec}/{i}')
    return sec

# main function
@csrf_exempt
def main(path):

    # initializing the count
    deleted_folders_count = 0
    deleted_files_count = 0

    # specify the path

    # specify the days

    # converting days to seconds
    # time.time() returns current time in seconds
    seconds = time.time() - (300)

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
                        remove_file(file_path)
                        deleted_files_count += 1  # incrementing count

        else:

            # if the path is not a directory
            # comparing with the days
            if seconds >= get_file_or_folder_age(path):

                # invoking the file
                remove_file(path)
                deleted_files_count += 1  # incrementing count

    else:

        pass

def remove_folder(path):
    shutil.rmtree(path)

def remove_file(path):
    # removing the file
    os.remove(path)

def get_file_or_folder_age(path):

    # getting ctime of the file/folder
    # time will be in seconds
    ctime = os.stat(path).st_ctime

    # returning the time
    return ctime

def test(req):
    return render(req,'test.html')

# def movies(request):
    movies = StockZort.objects.all()
    paginator = Paginator(movies, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request=request, template_name="blogs.html", context={'movies':page_obj})
@csrf_exempt
def stock_amount(req,sku):
    dep = get_role(req,'department')

    if req.method == "POST":
        amount = int(req.POST.get("adjust_amount"))
        zort_amount = int(req.POST.get("stock_amount"))
        adjust_type = req.POST.get("zort_adjust")
        ref = req.POST.get("ref")
        adjust_dict = {'plus':'เพิ่มเข้า stock','delete':'ลบออกจาก stock','adjust':'โยก','QC':'หลุด QC'}
        db.query_commit(f"insert into {dep}.log values ('{req.user}','ปรับรหัส {sku} {adjust_dict[adjust_type]} จำนวน {amount} หมายเหตุ {ref}',now())")
        # print(f"ปรับ โดย {req.user} รหัส {sku} {adjust_dict[adjust_type]} จำนวน {amount} หมายเหตุ {ref}")

    web = Web(get_api_register(dep,'apikey'),get_api_register(dep,'apisecret'),get_api_register(dep,'storename'))

    if adjust_type == 'delete':
        if zort_amount <= amount:
            web.post("UPDATEPRODUCTAVAILABLESTOCKLIST",sku,0 )
            db.query_commit(f"update {dep}.stock_main set amount = 0 where sku = '{sku}'")
            db.query_commit(f"update {dep}.stock set amount = amount + {int(zort_amount) - int(amount)} where sku = '{sku}'")
        else:
            web.post("UPDATEPRODUCTAVAILABLESTOCKLIST",sku,zort_amount-amount )
            db.query_commit(f"update {dep}.stock_main set amount = {zort_amount-amount} where sku = '{sku}'")
        messages.success(req,f"ลดสต็อคเรียบร้อย ... ")

    elif adjust_type == 'adjust':
        web.post("UPDATEPRODUCTAVAILABLESTOCKLIST",sku,int(zort_amount) + int(amount) )
        db.query_commit(f"update {dep}.stock_main set amount = {zort_amount + int(amount)} where sku = '{sku}'")
        db.query_commit(f"update {dep}.stock set amount = amount - {int(amount)} where sku = '{sku}'")
        messages.success(req,f"โยกสต็อกเรียบร้อย ... ")
    elif adjust_type == 'QC':
        if zort_amount <= amount:
            web.post("UPDATEPRODUCTAVAILABLESTOCKLIST",sku,0 )
            db.query_commit(f"update {dep}.stock_main set amount = 0 where sku = '{sku}'")
            db.query_commit(f"update {dep}.stock set amount = amount + {int(zort_amount) - int(amount)} where sku = '{sku}'")
        else:
            web.post("UPDATEPRODUCTAVAILABLESTOCKLIST",sku,zort_amount-amount )
            db.query_commit(f"update {dep}.stock_main set amount = {zort_amount-amount} where sku = '{sku}'")
        if db.check(f"select sku from stock_qc where sku = '{sku}'",dep):
            db.query_commit(f"update {dep}.stock_qc set amount = amount + {amount} where sku =  '{sku}'")
        else:
            db.query_commit(f"insert into {dep}.stock_qc values ('{sku}','{amount}')")
        messages.success(req,f"เพิ่มเข้าสต็อก QC เรียบร้อย ... ")
    else:
        db.query_commit(f"update {dep}.stock set amount = amount + {amount} where sku = '{sku}'")
        messages.success(req,f"เพิ่มสต็อคเรียบร้อย ... ")

    return redirect('page:image_admin_with_slug',slug=sku.split('-')[0])

@csrf_exempt
def get_product(req,sku):
    dep = get_role(req,'department')
    if req.method == 'POST':
        name = req.POST.get("edited_name")
        breast = req.POST.get("edited_breast")
        maxwrest = req.POST.get("edited_maxwrest")
        minwrest = req.POST.get("edited_minwrest")
        edited_shirts = req.POST.get("edited_shirts")
        edited_pants = req.POST.get("edited_pants")
        edited_crotch = req.POST.get("edited_crotch")
        edited_leg = req.POST.get("edited_leg")
        hip = req.POST.get("edited_hip")
        detail = req.POST.get("edited_detail")
        dataSize = req.POST.get("edited_dataSize")
        img_check = req.POST.get("img_check")
        dataSize_temp = f'➡️ Size {sku.split("-")[1]}'
        stock_detailsize = []
        if breast:
            dataSize_temp += f'รอบอก {breast}”'
        if minwrest:
            dataSize_temp += f'เอว {minwrest}-{maxwrest}”'
        if hip:
            dataSize_temp += f' สะโพก {hip}”'
        if edited_shirts:
            dataSize_temp += f' เสื้อยาว {edited_shirts}”'
            stock_detailsize.append(f"shirts = '{edited_shirts}'")
        if edited_pants:
            dataSize_temp += f' กางเกงยาว {edited_pants}”'
            stock_detailsize.append(f"pants = '{edited_pants}'")
        if edited_crotch:
            dataSize_temp += f' เป้ายาว {edited_crotch}”'
            stock_detailsize.append(f"crotch = '{edited_crotch}'")
        if edited_leg:
            dataSize_temp += f' รอบขา {edited_leg}”'
            stock_detailsize.append(f"leg = '{edited_leg}'")
        stock_detailsize_str = ', '.join(stock_detailsize)
        db.query_commit(f"update {dep}.stock_detailsize set {stock_detailsize_str} where sku = '{sku}'")
        dataSize_temp += dataSize
    data = name,breast,minwrest,maxwrest,hip,detail,dataSize_temp
    update_sql_by_sku(sku,data,get_role(req,"department"))
    messages.success(req,"อัพเดทสินค้าเรียบร้อย ... ")
    return redirect('page:image_admin_with_slug',slug=sku.split('-')[0])

def export_stock(req):
    dep = get_role(req,'department')
    task = f"""select cost.sku,descript,stock.amount + stock_main.amount as 'จำนวน',cost from stock_main
    inner join stock on stock.sku = stock_main.sku
    inner join cost on cost.sku = stock_main.sku
    where stock.amount + stock_main.amount  > 0
    order by sku """
    sec = datetime.datetime.now().timestamp()
    sec = str(sec).split('.')[0]
    export_excel(task,f"{sec}",dep)
    return redirect(f'/media/stock/{sec}.xlsx')

