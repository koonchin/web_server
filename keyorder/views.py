
import os,datetime
from django.shortcuts import render,redirect
from django.core.files.storage import FileSystemStorage
from function import db,get_role,export_excel
from django.contrib import messages
# Create your views here.

# PRODUCT LIST PAGE
def main(req):
    slug = ''
    if req.method == "POST":
        if req.POST.get('slug'):
            slug = req.POST.get('slug')
    # SHOW ALL IN KEYORDER PRODUCT TABLE
    dep = get_role(req,'department')
    task = f"select id,name,price,image,image2,image3 from keyorder where (id like '%{slug}%' or name like '%{slug}%') and (status = 0)"
    result = db.query_custom(task,dep)
    result = list(result.fetchall())
    context = {"result":result}
    return render(req,'keyorder.html',context=context)

# PRODUCT LIST PAGE OF EDITORDER
def editorder(req,slug):
    filter = ''
    if req.POST.get('slug'):
        filter = req.POST.get('slug')
    # SHOW ALL IN KEYORDER PRODUCT TABLE
    dep = get_role(req,'department')
    task = f"select id,name,price,image,image2,image3 from keyorder where (id like '%{filter}%' or name like '%{filter}%') and (status = 0)"
    result = db.query_custom(task,dep)
    result = list(result.fetchall())
    context = {"result":result,
                "id":slug}
    return render(req,'keyorder_editpage.html',context=context)

# CART DETAIL PAGE PER USER
def cartdetail(req):
    dep = get_role(req,'department')
    task = f'select id,name,keyorder_cart.amount,keyorder_cart.price from keyorder_cart\
        inner join keyorder on keyorder.id = keyorder_cart.productname where user = "{req.user}"'
    result = db.query_custom(task,dep)
    result = list(result.fetchall())
    context = {'result':result}
    return render(req,'keyordercartdetail.html',context=context)

# ORDER DETAIL PER ID
def orderdetail(req,slug):
    dep = get_role(req,'department')
    # PRODUCT DATA PART
    task = f'select productid,name,keyorder_orderdetail.amount,keyorder_orderdetail.price from keyorder_orderdetail\
        inner join keyorder on keyorder.id = keyorder_orderdetail.productid where keyorder_orderdetail.id = "{slug}"'
    result = db.query_custom(task,dep)
    order_detail = list(result.fetchall())

    # CUSTOMER DATA PART
    task = f"select name,tel,fee,address,trackingno,payment_status,discount from keyorder_order where id = {slug}"
    result = db.query_custom(task,dep)
    customerdetail = list(result.fetchall())[0]
    name = customerdetail[0]
    tel = customerdetail[1]
    address = customerdetail[3]
    trackingno = customerdetail[4]
    paymentstatus = customerdetail[5]
    fee = customerdetail[2]
    discount = customerdetail[6]
    context = {'result':order_detail,
                'name':name,
                'tel':tel,
                'id':slug,
                'address':address,
                'fee':fee,
                'discount':discount,
                'trackingno':trackingno,
                'paymentstatus':paymentstatus,
                }

    return render(req,'keyorderdetail.html',context=context)

# PATH PRINT_ORDER HAVE 3 FUNCTION (SEARCH,DELETE,PRINT)
def print_order(req):
    dep = get_role(req,'department')
    # CHECK WHICH BUTTON CLICK
    Print = req.POST.get('print')
    search = req.POST.get('search')
    delete = req.POST.get('delete')
    if Print:
        checked_order = req.POST.getlist('foo')
        CUSTOMER = []
        # IF NOT SELECTED CHECKBOX PRINT EVERY ORDER THAT NOT PRINTED
        if not checked_order:
            result = db.query_custom('select id from keyorder_order where printedtime is null',dep)
            result = list(result.fetchall())
            checked_order = [i[0] for i in result]
        
        for order in checked_order:
            # UPDATE PRINT_TIME TO NOW() & PREPARE CUSTOMER DATA
            db.query_commit(f"update {dep}.keyorder_order set printedtime = now() where id = {order}")
            task = f'select id,name,address,tel,payment_status,totalprice from keyorder_order where id = {order}'
            result= db.query_custom(task,dep)
            customer = list(result.fetchall())

            # PREPARE PRODUCT DATA TO PRINT
            task = f'select keyorder.name,keyorder_orderdetail.amount from keyorder inner join keyorder_orderdetail on keyorder.id = keyorder_orderdetail.productid where keyorder_orderdetail.id = {order}'
            result= db.query_custom(task,dep)
            PRODUCT = list(result.fetchall())
            product = [(i[0],i[1]) for i in PRODUCT]

            # INSERT SO IN PRINT DATA
            for i in range(len(customer)):
                customer[i] = list(customer[i])
                customer[i].append(product)
                customer[i].append("SO-{:05d}".format(customer[i][0]))
            CUSTOMER.append(customer)
        context = {'results':CUSTOMER}
        return render(req,"printorder.html",context=context)
    elif search:
        # CHECK INPUT OF IDORDER NAME OR DETAIL
        idorder = req.POST.get('idorder')
        if not idorder:
            idorder = ' '
        # CHECK IF FILTER BY DATETIME TOO
        DateTime = req.POST.get('Date_Time')
        if DateTime:
            FirstTime,LastTime = cleanedDateTime(DateTime)
            # ADD TO SPLIT IN PATH
            idorder =idorder + "*" + FirstTime + "*" + LastTime
            return redirect("keyorder:summary-search",slug=idorder)
        return redirect("keyorder:summary-search",slug=idorder)
    elif delete:
        checked_order = req.POST.getlist('foo')
        # FOR LOOP DELETE ORDER THAT CHECKED FROM CHECKBOX
        for i in checked_order:
            DeleteOrder(req,i)
        return redirect("keyorder:summary")

# ORDER PAGE
def summary(req,slug=''):
    if slug == ' ':
        slug = ''
    dep = get_role(req,'department')
    # PREPARE DATA TO SHOW IN SUMMARY PAGE
    task = f'select keyorder_order.id,keyorder_order.name,keytime,keyorder_order.totalprice,payment_status,printedtime from keyorder_order \
        inner join keyorder_orderdetail on keyorder_order.id = keyorder_orderdetail.id\
        where (number like "%{slug}%" or keyorder_order.name like "%{slug}%" or tel like "%{slug}%"\
        or address like "%{slug}%" or trackingno like "%{slug}%") and (keyorder_order.status = "key") group by id order by number'
    # IF HAVE * MEANS HAVE DATETIME TO FILTER
    if '*' in slug:
        slug,FirstTime,LastTime = slug.split('*')
        task = f'''select keyorder_order.id,keyorder_order.name,keytime,keyorder_order.totalprice,payment_status,printedtime from keyorder_order
        inner join keyorder_orderdetail on keyorder_order.id = keyorder_orderdetail.id
        where 
        (number like "%{slug}%" or keyorder_order.name like "%{slug}%" or tel like "%{slug}%"or address like "%{slug}%" or trackingno like "%{slug}%")
         and (keyorder_order.status = "key") and 
         (keyorder_order.keytime >=  '{FirstTime}' and keyorder_order.keytime <= '{LastTime}') group by id order by number'''
    result = db.query_custom(task,dep)
    result = list(result.fetchall())

    # CONVERT 1 to SO-00001
    for i in range(len(result)):
        result[i] = list(result[i])
        # CONVERT 0 , 1 TO PAID , COD
        if result[i][4] == '1':
            result[i][4] = 'ชำระแล้ว'
        else:
            result[i][4] = 'COD'
        result[i].append("SO-{:05d}".format(result[i][0]))

    context = {'result':result}

    return render(req,'summary.html',context=context)

# ADD PRODUCT PAGE
def addproductPage(req):
    return render(req,'addproduct.html')

# ADD PRODUCT FUNCTION OR UPDATE PRODUCT
def addproduct(req):
    dep = get_role(req,'department')
    if req.method == 'POST':
        # TO CHECK DATA FROM ADD PRODUCT OR FROM UPDATE PRODUCT 
        id = req.POST.get("checkexist")
        # TEXT
        name = req.POST.get("name")    
        amount = req.POST.get("amount")
        price = req.POST.get("price")
        cost = req.POST.get("cost")

        # CREATE FOLDER FOR STORE IMAGE IF NOT FROM UPDATE PRODUCT
        if not id:
            task = 'select max(id) from keyorder'
            result = db.query_custom(task,dep)
            sec = list(result.fetchall())[0][0]
            sec = int(sec) + 1 
            sec = str(sec)
            os.makedirs(fr'media\keyorder\{sec}', exist_ok=True)
        else:
            # IF UPDATE PRODUCT REMOVE OLD IMAGE
            sec = id
            for i in os.listdir(f'media/keyorder/{id}'):
                os.remove(os.path.join(f'media/keyorder/{id}',i))
        # STACK IMAGE PATH
        MYFILE = []
        # FOR LOOP 3 IMAGE FIELDS
        for ID in range(3):
            # NAME OF IMAGE UPLOAD
            myfile = req.FILES.getlist(f'myfile{ID}')
            for i in myfile:
                fs = FileSystemStorage()
                filename = fs.save(f"keyorder/{sec}/{i.name}", i)

                # RECORD EACH IMAGE
                MYFILE.append(i.name)
        # IF OLD PRODUCT SO OLD DATA TO NEW
        if id:
            task = f"update {dep}.keyorder set name = '{name}', price = '{price}', amount = '{amount}', cost = '{cost}',\
                image = 'media/keyorder/{id}/{MYFILE[0]}',\
                image2 = 'media/keyorder/{id}/{MYFILE[1]}',\
                image3 = 'media/keyorder/{id}/{MYFILE[2]}'\
                where id = {id}"
            db.query_commit(task)
        else:
        # INSERT INTO DATABASE AS NEW PRODUCT
            task = f"insert into {dep}.keyorder values (0,'{name}','{price}','{amount}','{cost}','media/keyorder/{sec}/{MYFILE[0]}',\
                'media/keyorder/{sec}/{MYFILE[1]}','media/keyorder/{sec}/{MYFILE[2]}',0)"
            db.query_commit(task)

    # SHOW ALL IN KEYORDER PRODUCT TABLE
    dep = get_role(req,'department')
    task = f"select id,name,price,image,image2,image3 from keyorder where status = 0"
    result = db.query_custom(task,dep)
    result = list(result.fetchall())
    context = {"result":result}
    return render(req, 'keyorder.html',context)

# ADD PRDUCT TO CART
def add_to_cart(req,slug):
    dep = get_role(req,'department')

    # CHECK IF EXIST UPDATE AMOUNT ELSE INSERT NEW
    task = f"select 1 from keyorder_cart where productname = '{slug}' and user = '{req.user}'"
    if db.check(task):
        task = f"update {dep}.keyorder_cart set amount = amount + 1\
             where productname = '{slug}' and user = '{req.user}'"
        db.query_commit(task)
        messages.success(req,"update quantity .... ")
    else:
        # IF NOT EXIST FROM CART INSERT NEW TO IT
        task = f'select price from keyorder where id = "{slug}"'
        result= db.query_custom(task,dep)
        price = list(result.fetchall())[0][0]
        task = f'insert into {dep}.keyorder_cart values ("{req.user}","{slug}",1,{price})'
        
        db.query_commit(task)
        messages.success(req,"add new item to cart")

    return redirect("keyorder:cartdetail")

# EDIT ORDER PAGE
def add_to_editorder(req,id,idproduct):
    dep = get_role(req,'department')

    # CHECK IF EXIST UPDATE AMOUNT ELSE INSERT NEW
    task = f"select 1 from keyorder_orderdetail where productid = '{idproduct}' and id = '{id}'"
    if db.check(task):
        task = f"update {dep}.keyorder_orderdetail set amount = amount + 1\
             where productid = '{idproduct}'and id = '{id}'"
        db.query_commit(task)
        messages.success(req,"update quantity .... ")
    else:
        # IF NOT EXIST INSERT NEW PRODUCT TO ORDER
        task = f'select price from keyorder where id = "{idproduct}"'
        result= db.query_custom(task,dep)
        price = list(result.fetchall())[0][0]
        task = f'insert into {dep}.keyorder_orderdetail values ("{id}","{idproduct}",1,{price},{price})'
        db.query_commit(task)   
        messages.success(req,"add new item to cart")

    return redirect("keyorder:order-detail",slug=id)

# ADD ORDER FUNCTION
def addorder(req,slug):
    dep = get_role(req,'department')

    # PREPARE TO CREATE ORDER 
    tel= req.POST.get('tel')
    name = req.POST.get('name')
    fee= req.POST.get('fee')
    discount= req.POST.get('discount')
    address= req.POST.get('address')
    totalprice= req.POST.get('totalprice')
    status= req.POST.get('status')
    if not fee:
        fee = 0
    if not discount:
        discount = 0

    task = f'insert into {dep}.keyorder_order values (0,"","{tel}","{name}","{fee}","{discount}","{address}",now(),null,"key","{status}","{totalprice}","")'
    db.query_commit(task)

    # GET ID TO REFER IN DETAIL DATABASE
    task = f'select max(id) from keyorder_order'
    result = db.query_custom(task,dep)
    id = list(result.fetchall())[0][0]

    # UPDATE CART & INSERT DETAIL DATABASE
    for i in range(slug + 10):
        product = req.POST.get(f'product{i + 1}')
        amount = req.POST.get(f'amount{i + 1}')
        price = req.POST.get(f'price{i + 1}')
        if product and amount and price:
            task  = f'delete from {dep}.keyorder_cart where user = "{req.user}"'
            db.query_commit(task)
            task = f"insert into {dep}.keyorder_orderdetail values ('{id}','{product}','{amount}','{price}','{totalprice}')"
            db.query_commit(task)
    db.query_commit(f'update {dep}.keyorder_order set number = "{"SO-{:05d}".format(id)}" where id = {id}')

    return redirect("keyorder:summary")

# UPDATE ORDER FUNCTION 
def updateorder(req,slug):
    dep = get_role(req,'department')

    # PREPARE TO UPDATE ORDER 
    tel= req.POST.get('tel')
    name = req.POST.get('name')
    fee= req.POST.get('fee')
    discount= req.POST.get('discount')
    address= req.POST.get('address')
    totalprice= req.POST.get('totalprice')
    status= req.POST.get('status')
    trackingno= req.POST.get('trackingno')
    if not fee:
        fee = 0

    task = f'update {dep}.keyorder_order set tel = "{tel}",name = "{name}",discount = "{discount}",fee = "{fee}",address = "{address}",payment_status = "{status}",totalprice = "{totalprice}",trackingno = "{trackingno}" where id = {slug}'
    db.query_commit(task)

    # GET LENGHT OF ORDER TO FOR LOOP THROUGR IT
    task = f'select id from keyorder_orderdetail where id = {slug}'
    result = db.query_custom(task,dep)
    lenght_order= len(list(result.fetchall())[0])

    # UPDATE CART & INSERT DETAIL DATABASE
    task  = f'delete from {dep}.keyorder_orderdetail where id = "{slug}"'
    db.query_commit(task)

    for i in range(lenght_order + 10):
        product = req.POST.get(f'product{i + 1}')
        amount = req.POST.get(f'amount{i + 1}')
        price = req.POST.get(f'price{i + 1}')
        if product and amount and price:
            task = f"insert into {dep}.keyorder_orderdetail values ('{slug}','{product}','{amount}','{price}','{totalprice}')"
            db.query_commit(task)

    return redirect("keyorder:summary")

# UPDATE TRACKINGNO PAGE
def trackingno(req):
    return render(req,'trackingno.html')

# UPDATE TRACKINGNO FUNCTION   
def addtrackingno(req):
    dep = get_role(req,'department')
    if req.method == "POST":
        idorder = int(req.POST.get('idorder'))
        trackingno = req.POST.get('trackingno')
        task = f'update {dep}.keyorder_order set trackingno = "{trackingno}" where id = {idorder}'
        db.query_commit(task)
        messages.success(req,'updated trackingno ....')
        return render(req,'trackingno.html')
    messages.error(req,'something wrong ...')
    return render(req,'trackingno.html')

# SUP FUNCTION TO CHECK ID ORDER EXIST OR NOT TO ADD TRACKING
def checkIdorderExist(req):
    dep = get_role(req,'department')
    if req.method == "POST":
        idorder = req.POST.get('idorder')
        task = f'select 1 from keyorder_order where id = {int(idorder)}'
        if db.check(task,dep):
            messages.success(req,'idorder matched ....')
            context = {'idorder':idorder}
            return render(req,'trackingno-add.html',context=context)
    messages.error(req,'No matched id ...')
    return render(req,'trackingno.html')

# EDIT PRODUCT PAGE
def editproduct(req):
    dep = get_role(req,'department')
    task = 'select id,name,price,amount,cost,image from keyorder where status = 0'
    slug = req.POST.get('productcode')
    if slug:
        task = f'select id,name,price,amount,cost,image from keyorder where (id like "%{slug}%" or name like "%{slug}%") and (status = 0)'
    result = db.query_custom(task,dep)
    result = list(result.fetchall())
    context = {'result':result}
    return render(req,'editproduct.html',context=context)

# PRODUCT DETAIL PAGE
def productDetail(req,slug):
    dep = get_role(req,'department')
    task = f'select name,amount,price,cost,image,image2,image3 from keyorder where id = {slug}'
    result = db.query_custom(task,dep)
    result = list(result.fetchall())[0]
    name,amount,price,cost,image,image2,image3 = result
    context = {'id':slug,'name':name,'amount':amount,'price':price,'cost':cost,'image':image,'image2':image2,'image3':image3,}
    return render(req,"product-detail.html",context=context)

# DELETE PRODUCT FUNCTION
def DeleteProduct(req):
    dep = get_role(req,'department')
    checked_order = req.POST.getlist('foo')
    for order in checked_order:
        db.query_commit(f"update {dep}.keyorder set status = 1 where id = {order}")
    messages.error(req,'delete complete ... ')
    return redirect('keyorder:editproduct')

# DELETE ORDER FUNCTION
def DeleteOrder(req,id):
    dep = get_role(req,'department')
    db.query_commit(f'update {dep}.keyorder_order set status = "delete" where id = {id}')

# DELETE CART PRODUCT FUNCTION
def DeleteCartItem(req,slug):
    dep = get_role(req,'department')
    db.query_commit(f"delete from {dep}.keyorder_cart where user = '{req.user}' and productname = {slug} ")
    return redirect('keyorder:cartdetail')

# DASHBOARD PAGE
def Dashboard(req):       
    dep = get_role(req,'department')
    # PREPARE PRODUCTNAME & SUM AMOUNT THAT SOLD
    task = 'select name,sum(keyorder_orderdetail.amount) from keyorder_orderdetail \
    inner join keyorder on keyorder_orderdetail.productid = keyorder.id\
    group by keyorder_orderdetail.productid'
    if req.method == 'POST':
        DateTime = req.POST.get('Date_Time')
        slug = req.POST.get('slug')
        # IF HAVE DATETIME TO FILTER
        if DateTime:
            FirstTime,LastTime = cleanedDateTime(DateTime)
            task = f"""
            select keyorder.name,sum(keyorder_orderdetail.amount) from keyorder_orderdetail 
            inner join keyorder on keyorder_orderdetail.productid = keyorder.id
            inner join keyorder_order on keyorder_order.id = keyorder_orderdetail.id
            where (keytime >=  '{FirstTime}' and keytime <= '{LastTime}') and (keyorder.name like '%{slug}%' or keyorder.id like '%{slug}%')
            group by keyorder_orderdetail.productid;
            """
        else:
            task = f"""
            select keyorder.name,sum(keyorder_orderdetail.amount) from keyorder_orderdetail 
            inner join keyorder on keyorder_orderdetail.productid = keyorder.id
            inner join keyorder_order on keyorder_order.id = keyorder_orderdetail.id
            where keyorder.name like '%{slug}%' or keyorder.id like '%{slug}%'
            group by keyorder_orderdetail.productid;
            """
    result = db.query_custom(task,dep)
    result = list(result.fetchall())
    context = {'result':result}
    return render(req,'dashboard.html',context=context)

# SPLIT DATETIME RANGE
def cleanedDateTime(DateTime):
    FirstTime = DateTime.split(' -')[0]
    LastTime = DateTime.split('- ')[1]
    FirstTime = datetime.datetime.strptime(FirstTime, "%d/%m/%Y").strftime("%Y-%m-%d")
    LastTime = datetime.datetime.strptime(LastTime, "%d/%m/%Y").strftime("%Y-%m-%d")
    return FirstTime,LastTime

# EXPORT ORDER DETAIL TO EXCEL
def ExportOrder(req):
    DateTime = req.POST.get('Date_Time')

    dep = get_role(req,'department')
    task = """select number,keyorder_order.name,tel,address,keytime,keyorder_order.totalprice,fee,address,trackingno,
        if(payment_status = 1,"โอน","COD") as "Payment Method",keyorder_orderdetail.amount as "จำนวนสินค้า"
        ,keyorder.name as "ชื่อสินค้า" from keyorder_order
        inner join keyorder_orderdetail on keyorder_order.id = keyorder_orderdetail.id
        inner join keyorder on keyorder_orderdetail.productid = keyorder.id"""

    if DateTime:
        FirstTime,LastTime = cleanedDateTime(DateTime)
        task = f"""select number,keyorder_order.name,tel,address,keytime,keyorder_order.totalprice,fee,address,trackingno,
            if(payment_status = 1,"โอน","COD") as "Payment Method",keyorder_orderdetail.amount as "จำนวนสินค้า"
            ,keyorder.name as "ชื่อสินค้า" from keyorder_order
            inner join keyorder_orderdetail on keyorder_order.id = keyorder_orderdetail.id
            inner join keyorder on keyorder_orderdetail.productid = keyorder.id
            where keytime >= '{FirstTime}' and keytime <= '{LastTime}'
            """
    
    sec = datetime.datetime.now().timestamp()
    sec = str(sec).split('.')[0]
    export_excel(task,f"{sec}",dep)
    return redirect(f'/media/stock/{sec}.xlsx')
