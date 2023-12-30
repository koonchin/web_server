from django.contrib import messages
from django.shortcuts import redirect, render
from function import *
# Create your views here.

def add_reserve_order(dep,productData,data):
    
    # information
    db.query_commit(f"insert into {dep}.addorder values (0, '{data[0]}', '{data[1]}', '{data[2]}', '{data[3]}', '{data[4]}', '{data[5]}', '{data[6]}', 0, now(),{data[7]})")

    # product
    product,amount,price = productData

    # make dict amount
    web = Web(get_api_register(dep,'apikey'),get_api_register(dep,'apisecret'),get_api_register(dep,'storename'))
    task = db.query(f"select sku,amount from {dep}.stock_main")
    task = list(task.fetchall())
    amount_dict = {}
    for i in task:
        amount_dict[i[0]] = int(i[1])

    task = db.query_custom(f"select stock.sku,stock.amount + stock_main.amount from stock_main inner join stock on stock.sku = stock_main.sku",dep)
    task = list(task.fetchall())
    total_dict = {}
    for i in task:
        total_dict[i[0]] = int(i[1])

    # database
    task = f"select max(idaddorder) from addorder"
    result = db.query_custom(task,dep)
    maxid = list(result.fetchall())[0][0]
    for i in range(len(product)):
        if total_dict[product[i]] < amount[i]:
            db.query_commit(f"insert into {dep}.addorder_detail values ({maxid},'{product[i]}','{amount[i]}','{price[i]}',0)")
            db.query_commit(f"insert into {dep}.log values ('จอง','ปรับรหัส {product[i]} ยังไม่มีของ ลด {amount[i]} ให้ จอง id ที่ {maxid}',now())")
        else:
            if amount_dict[product[i]] <= amount[i] :
                web.post("UPDATEPRODUCTAVAILABLESTOCKLIST",product[i],0 )
                db.query_commit(f"update {dep}.stock_main set amount = 0 where sku = '{product[i]}'")
                db.query_commit(f"update {dep}.stock set amount = amount + {int(amount_dict[product[i]]) - int(amount[i])} where sku = '{product[i]}'")
            else:
                web.post("UPDATEPRODUCTAVAILABLESTOCKLIST",product[i],amount_dict[product[i]]-amount[i] )
                db.query_commit(f"update {dep}.stock_main set amount = {amount_dict[product[i]]-amount[i]} where sku = '{product[i]}'")

            db.query_commit(f"insert into {dep}.addorder_detail values ({maxid},'{product[i]}','{amount[i]}','{price[i]}',1)")
            db.query_commit(f"insert into {dep}.log values ('จอง','ปรับรหัส {product[i]} ลด {amount[i]} ให้ จอง id ที่ {maxid}',now())")

def addorder(req):
    dep = get_role(req,'department')
    number = 999
    # product
    product  = [req.POST.get(f"{number}productid{i+1}").split(' ')[0] for i in range(50) if req.POST.get(f"{number}productid{i+1}")]
    amount  = [req.POST.get(f"{number}amountid{i+1}") for i in range(50) if req.POST.get(f"{number}amountid{i+1}")  ]
    price  = [req.POST.get(f"{number}priceid{i+1}") for i in range(50) if req.POST.get(f"{number}priceid{i+1}")  ]
    
    # information
    discount = req.POST.get('999discount')
    shippingamount = req.POST.get('999deli_fee')
    sum = req.POST.get('999sum')
    name = req.POST.get('999cstname')
    tel = req.POST.get('999tel2')
    addr = req.POST.get('addr')
    deli_channel = req.POST.get('shippingCompany')
    paymentmethod = req.POST.get('Payment')

    data = [name, addr, tel, deli_channel, paymentmethod, discount, shippingamount,sum]
    productData = product,amount,price
    add_reserve_order(dep,productData,data)
    return redirect("/RMA/")
    
def reserveForReturn(id,product,amountReturn,dep):
    web = Web(get_api_register(dep,'apikey'),get_api_register(dep,'apisecret'),get_api_register(dep,'storename'))
    amount = db.query(f"select descript,amount from {dep}.stock_main")
    amount = list(amount.fetchall())
    amount_dict = {}
    for i in amount:
        amount_dict[i[0].replace(' ','').strip()] = int(i[1])

    sku_data = db.query(f"select descript,sku from {dep}.stock_main")
    sku_data = list(sku_data.fetchall())
    sku_data_dict = {}
    for i in sku_data:
        sku_data_dict[i[0].replace(' ','').strip()] = i[1]
    x = {}
    for i in range(len(product)):
        x[product[i].replace(' ','').strip()] = int(amountReturn[i])

    for sku in product:
        amount = x[sku.replace(' ','').strip()]
        amount = int(amount)
        if amount_dict[sku.replace(' ','').strip()] <= amount:
            web.post("UPDATEPRODUCTAVAILABLESTOCKLIST",sku_data_dict[sku.replace(' ','').strip()],0 )
            task = f"update {dep}.stock_main set amount = 0 where sku = '{sku_data_dict[sku.replace(' ','').strip()]}'"
            db.query_commit(task)
            task = f"update {dep}.stock set amount = amount + {int(amount_dict[sku.replace(' ','').strip()]) - int(amount)} where sku = '{sku_data_dict[sku.replace(' ','').strip()]}'"
            db.query_commit(task)
        else:
            web.post("UPDATEPRODUCTAVAILABLESTOCKLIST",sku_data_dict[sku.replace(' ','').strip()],amount_dict[sku.replace(' ','').strip()]-amount )
            task = f"update {dep}.stock_main set amount = {amount_dict[sku.replace(' ','').strip()]-amount} where sku = '{sku_data_dict[sku.replace(' ','').strip()]}'"
            db.query_commit(task)
        db.query_commit(f"insert into {dep}.log values ('RMA','ปรับรหัส {sku_data_dict[sku.replace(' ','').strip()]} ลด {amount} ให้ RMA ID {id}',now())")

def form_RMA(dep,number,cstname,phone,addr,Payment,discount,shippingamount,total_price,total,product,shippingchannel,reason):
    discount = discount * -1
    descript = db.query(f"select sku,descript from {dep}.stock_main")
    descript = list(descript.fetchall())
    descript_dict = {}
    for i in descript:
        descript_dict[i[1].replace(' ','').strip()] = i[0]

    data_list = []

    for i in product:
        name = i[0]
        sku = descript_dict[name.replace(' ','').strip()]
        amount = int(i[1])
        price = int(i[2])

        data_form = {"sku":sku,"name":name,"number":amount,"pricepernumber":price,"discount":"0","totalprice":price * amount}
        data_list.append(data_form)

    if 'cod' in shippingchannel.lower():
        isCOD = True
        cstname += " (COD)"
        zort_form = {
            "reference":reason,
            "number":f"{number} return",
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
            "reference":reason,
            "number":f"{number} return",
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
            "paymentmethod" : Payment,
            "paymentamount":total,
            "list":data_list
            }

    return zort_form

def main(req):
    dep = get_role(req,'department')

    result = db.query(f"select stock_main.descript,cost.price from {dep}.cost inner join {dep}.stock_main on stock_main.sku = cost.sku where cost.price is not null")
    result = list(result.fetchall())
    price_dict = {}
    for i in result:
        price_dict[i[0].strip().replace(' ','')] = i[1]
    if req.method == "GET":
        result = db.query(f"select idorder,number,customername,orderdate,trackingno,addr,tel from {dep}.deli_zort\
            union select idorder,idorder,cstname,date,trackingNo,addr,tel from {dep}.deli_vrich\
        order by orderdate desc limit 10;")

        data = list(result.fetchall())

        result = db.query(f"select order_main.IDorder,stock_main.descript,order_main.price,deli_zort.orderdate from {dep}.order_main\
            inner join {dep}.stock_main on stock_main.sku = order_main.sku\
            inner join {dep}.deli_zort on {dep}.deli_zort.idorder = {dep}.order_main.idorder\
            union select idorder,stock_main.descript,price,date from {dep}.deli_vrich\
            inner join {dep}.stock_main on stock_main.sku = deli_vrich.sku order by orderdate desc limit 300;")

        popup_data = list(result.fetchall())
        
    else:
        number = req.POST.get("number")  
        trackingNo = req.POST.get("trackingno")

        result = db.query(f"""select idorder,number,customername,orderdate,trackingno,addr,tel from {dep}.deli_zort
        where number like '%{number}%' and trackingNo like '%{trackingNo}%'
        union select idorder,idorder,cstname,date,trackingNo,addr,tel from {dep}.deli_vrich
        where idorder like '%{number}%' and trackingNo like '%{trackingNo}%'""")
        data = list(result.fetchall())

        task = f"""
        select deli_zort.IDorder,stock_main.descript,order_main.price,deli_zort.orderdate from order_main
            inner join stock_main on stock_main.sku = order_main.sku
            inner join deli_zort on deli_zort.idorder = order_main.idorder
            where deli_zort.idorder in (select idorder from deli_zort where number like '%{number}%' and trackingno like '%{trackingNo}%' order by orderdate desc)
            union select idorder,stock_main.descript,price,date from deli_vrich
            inner join stock_main on stock_main.sku = deli_vrich.sku
            where IDorder in (select idorder from deli_vrich
			where idorder like '%{number}%' and trackingNo like '%{trackingNo}%' order by date desc) limit 300;
        """
        result = db.query_custom(task,dep)

        popup_data = list(result.fetchall())

    task = f"select stock_main.descript from {dep}.stock_main inner join {dep}.stock on stock.sku = stock_main.sku where stock.amount + stock_main.amount > 0;"
    result = db.query(task)
    sku = list(result.fetchall())
    sku = [i[0] for i in sku]

    context = {'data':data,
                'skus':sku,
                "popup_data":popup_data,
                "price_dict":price_dict}
    return render(req,'return.html',context)

def add(req,number):
    name = str(number).split(' ')[1]
    number = str(number).split(' ')[0]
    dep = get_role(req,'department')
    web = Web(get_api_register(dep,"apikey"),get_api_register(dep,"apisecret"),get_api_register(dep,"storename"))

    if req.method == "POST":

        result = db.query_custom(f"""select descript from deli_zort 
        inner join order_main on order_main.idorder = deli_zort.idorder
        inner join stock_main on order_main.sku = stock_main.sku
        where deli_zort.idorder like '%{number}%'
        union select stock_main.descript from deli_vrich 
        inner join stock_main on stock_main.sku = deli_vrich.sku
        where idorder like '%{number}%'

        """,dep)
        popup_data = list(result.fetchall())
        popup_data = [i[0] for i in popup_data]

        product  = [req.POST.get(f"{number}productid{i+1}") for i in range(50) if req.POST.get(f"{number}productid{i+1}")  ]
        amount  = [req.POST.get(f"{number}amountid{i+1}") for i in range(50) if req.POST.get(f"{number}amountid{i+1}")  ]
        price  = [req.POST.get(f"{number}priceid{i+1}") for i in range(50) if req.POST.get(f"{number}priceid{i+1}")  ]

        return_product = []
        for i in range(100):
            for item in range(len(popup_data)):
                if req.POST.getlist(f"return{number}{i + 1}{popup_data[item]}"):
                    return_product.append(req.POST.getlist(f"return{number}{i + 1}{popup_data[item]}")[0]) 

        # สำหรับตาราง RMA_order
        csttel = req.POST.get(f"{number}tel2")
        cstname = req.POST.get(f"{number}cstname")
        addr = req.POST.get("addr")

        # สำหรับตาราง RMA
        csttrackingno = req.POST.get("csttrackingno")
        type_return = req.POST.get("type")
        reason = req.POST.get("reason")
        etc_input = req.POST.get("etc_input")
        order_status = req.POST.get("when_to_send")
        shippingCompany = req.POST.get("shippingCompany")
        Payment = req.POST.get("Payment")

        deli_fee = int(req.POST.get(f"{ number}deli_fee"))
        total_price = int(req.POST.get(f"{number}totalPrice"))
        total = int(req.POST.get(f"{number}sum"))
        if len(number) < 7:
            platform = 'VRICH'
        else:
            platform = 'ZORT'

        # ถ้าเลือก อื่นๆ ให้ สาเหตุ = อื่นๆ
        if etc_input != '':
            reason = etc_input

    if type_return == 'ตีกลับ':
        reason = 'ตีกลับ'

    if order_status == 'ส่งทันที':
        status = 'คีย์ออเดอร์แล้ว'
        data = form_RMA(dep,name,cstname,csttel,addr,Payment,total - total_price - deli_fee,deli_fee,total_price,total,list(zip(product,amount,price)),shippingCompany,reason)
        web.post_order(data)
    else:
        status = 'รอคีย์'

    db.query_commit(f"""
    insert into {dep}.RMA values (0, '{cstname}','{csttrackingno}', '{type_return}','{reason}','{platform}', now(),'{status}' , '{order_status}', NULL,'{csttel}','{addr}','{shippingCompany}','{name}',
    '{total}',{total - total_price - deli_fee},'{deli_fee}','{total_price}','{Payment}')
    """)

    result = db.query(f"select id from {dep}.RMA where number = '{name}'")
    result = list(result.fetchall())[0][0]
    if status == 'รอคีย์':
        reserveForReturn(result,product,amount,dep)
    for i in range(len(product)):
        db.query_commit(f"insert into {dep}.RMA_data values ({result},'{product[i]}', '{amount[i]}', '{price[i]}')")
    for i in range(len(return_product)):
        db.query_commit(f"insert into {dep}.RMA_before values ({result},'{return_product[i]}','รอของ')")

    return redirect('/RMA/')
    # return render(req,'RMA.html',context)

def stock(req):
    dep = get_role(req,'department')
    if req.method == "GET":
        task = """
        select distinct RMA.id,number,cstname,csttrackingno,key_time,RMA_before.status,order_status,reason,RMA.addr from RMA 
        inner join RMA_before on RMA_before.id = RMA.id where recieve_time is NULL limit 100;"""
        result = db.query_custom(task,dep)
        result = list(result.fetchall())

        task = "select id,descript from RMA_before order by id desc limit 100;"
        products = db.query_custom(task,dep)
        products = list(products.fetchall())
    else:
        number = req.POST.get("number")  
        cstname = req.POST.get("cstname")  
        csttrackingno = req.POST.get("csttrackingno")   

        task = f"""
        select distinct RMA.id,number,cstname,csttrackingno,key_time,RMA_before.status,order_status,reason,RMA.addr from RMA 
        inner join RMA_before on RMA_before.id = RMA.id where recieve_time is NULL and number like '%{number}%' and csttrackingno like '%{csttrackingno}%' and cstname like '%{cstname}%' limit 100;"""
        result = db.query_custom(task,dep)
        result = list(result.fetchall())

        task = f"""select id,descript from RMA_before where id in (select distinct RMA.id from RMA 
        inner join RMA_before on RMA_before.id = RMA.id where recieve_time is NULL and number like '%{number}%' and csttrackingno like '%{csttrackingno}%' and cstname like '%{cstname}%')  limit 100;"""
        products = db.query_custom(task,dep)
        products = list(products.fetchall())
    context = {'data':result,
                'products':products,
                }
    return render(req,'RMA.html',context)

def confirm(req,id):

    compare = lambda x, y: Counter(x) == Counter(y)

    dep = get_role(req,'department')
    web = Web(get_api_register(dep,"apikey"),get_api_register(dep,"apisecret"),get_api_register(dep,"storename"))
    # ตาราง RMA
    
    if req.method == "POST":
        comment = req.POST.get(f"{id}Comment")
        address = req.POST.get(f"{id}Address")
    task = f"select * from RMA_before where id = '{id}'"
    result = db.query_custom(task,dep)
    result = list(result.fetchall())

    web_products  = [req.POST.get(f"return{id}{i + 1}") for i in range(300) if req.POST.get(f"return{id}{i + 1}")  ]
    before_products = [i[1] for i in result]
    x = Counter(web_products)
    y = Counter(before_products)
    if x == y:

        task = f"""
        select descript,stock_main.amount from stock_main
        """
        result = db.query_custom(task,dep)
        result = list(result.fetchall())
        descript_dict = {}

        sku_data = db.query(f"select descript,sku from {dep}.stock_main")
        sku_data = list(sku_data.fetchall())
        sku_data_dict = {}
        for i in sku_data:
            sku_data_dict[i[0]] = i[1]

        for i in result:
            descript_dict[i[0]] = int(i[1])

        for i in y:
            payload_list = []
            payload_list.append({"sku":sku_data_dict[i],"stock":1,"cost":0})
            payload = {}
            payload['stocks'] = payload_list
            web.increase_stock(payload,'W0005')
            db.query_commit(f"insert into {dep}.log values ('RMA','เพิ่มสต็อกเพราะรีเทิร์น รหัส {sku_data_dict[i]} จำนวนที่เพิ่ม {y[i]} id {id}' ,now())")

        task = f"select * from RMA where id = '{id}'"
        result = db.query_custom(task,dep)
        result = list(result.fetchall())[0]
        order_status = result[8]

        if order_status != "ส่งทันที":

            number = result[13]
            reason = result[4]
            cstname = result[1]
            csttel = result[10]
            addr = result[11]
            Payment = result[18]
            discount = result[15]
            deli_fee = result[16]
            total_price = result[17]
            total = result[14]
            shippingCompany = result[12]

            task = f"select * from RMA_data where id = {id}"
            result = db.query_custom(task,dep)
            result = list(result.fetchall())

            product = [i[1] for i in result]
            amount = [i[2] for i in result]
            price = [i[3] for i in result]
            # if order_status != 'ส่งทันที':

            task = f"""
            select sku,stock_main.amount + RMA_data.amount from stock_main
            inner join RMA_data on RMA_data.descript = stock_main.descript
            where stock_main.descript in (select descript from RMA_data where id = {id});
            """
            result = db.query_custom(task,dep)
            result = list(result.fetchall())

            for i in result:
                web.post("UPDATEPRODUCTAVAILABLESTOCKLIST",i[0],int(i[1]))
            data = form_RMA(dep,number,cstname,csttel,addr,Payment,discount,deli_fee,total_price,total,list(zip(product,amount,price)),shippingCompany,reason)
            print('here')
            web.post_order(data)
            send_line_return(f"ออเดอร์รีเทิร์นร้าน {dep} ได้รับพัสดุแล้ว เลขรายการ {number} return")
            messages.success(req,"คีย์ออเดอร์ และ เพิ่มสต็อกเรียบร้อย ... ")
        else:
            messages.success(req,"เพิ่มสต็อกเรียบร้อย ... ")
        db.query_commit(f"update {dep}.RMA set recieve_time = now(),status = 'คีย์แล้ว',order_status = 'ยืนยันพัสดุเรียบร้อย' where id = {id}")
        db.query_commit(f"update {dep}.RMA_before set status = 'คีย์ออเดอร์แล้ว' where id = {id}")

    else:
        db.query_commit(f"update {dep}.RMA set addr = '{address}' where id = {id}")
        task = f"""
        select number from RMA where id = {id}
        """
        result = db.query_custom(task,dep)
        result = list(result.fetchall())[0][0]

        send_line_return(f"ลูกค้ารายการ {result} มีปัญหา comment {comment} ร้าน {dep}")
        messages.error(req,"ส่งไลน์ให้แอดมินเรียบร้อย ... ")

    task = """
    select RMA.id,number,cstname,csttrackingno,key_time,RMA_before.status,order_status,addr from RMA 
    inner join RMA_before on RMA_before.id = RMA.id where recieve_time is NULL limit 100;"""
    result = db.query_custom(task,dep)
    result = list(result.fetchall())

    task = "select id,descript from RMA_before limit 100;"
    products = db.query_custom(task,dep)
    products = list(products.fetchall())

    return redirect('/RMA/stock/')

def deleteRMA(req,id):
    dep = get_role(req,'department')
    db.query_commit(f"delete from {dep}.RMA where id = {id}")
    db.query_commit(f"delete from {dep}.RMA_before where id = {id}")
    db.query_commit(f"delete from {dep}.RMA_data where id = {id}")
    return redirect("/RMA/stock/")