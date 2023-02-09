from django.shortcuts import render
from django.conf import settings
# Create your views here.
from django.views.decorators.csrf import csrf_exempt
import json,datetime
from function import *
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
     TextSendMessage,TemplateSendMessage, ButtonsTemplate, URIAction
)
import xlsxwriter

# webhook line bot QC PART ----------------------------

def template():
    # Create a URIAction for the file
    uri_action = URIAction(
        label='Open File',
        uri='https://139-162-28-194.ip.linodeusercontent.com/media/export_data.xlsx'
    )

    # Create a ButtonsTemplate with the URIAction
    template = ButtonsTemplate(
        thumbnail_image_url='https://secure.zortout.com/Home/DisplayProductImage?pid=13636476',
        title='File Template',
        text='Click the button to open the file',
        actions=[uri_action]
    )

    # Create a TemplateSendMessage with the ButtonsTemplate
    template_message = TemplateSendMessage(
        alt_text='File template',
        template=template
    )
    return template_message

def export():
    task = 'select DATE_ADD(date, INTERVAL 7 HOUR),id,image,name from muslin.qc_data'
    result = db.query(task)
    result = list(result.fetchall())
    for i in result:
        with open(f"{settings.MEDIA_ROOT}/{i[1]}.jpg",'wb') as f:
            f.write(i[2])

    workbook = xlsxwriter.Workbook(f'{settings.MEDIA_ROOT}/export_data.xlsx')
    # Create an new Excel file and add a worksheet.
    worksheet = workbook.add_worksheet()
    # Widen the first column to make the text clearer.
    worksheet.set_column('A:A', 30)
    for i in range(len(result)):
        row_index = i + 1
        
        row = (row_index - 1) * 20
        if i == 0:
            row = row_index

        # Insert an image.
        worksheet.write(f'A{row}', str(result[i][0]))
        worksheet.write(f'B{row}', result[i][3])
        worksheet.insert_image(f'C{row}', f'{settings.MEDIA_ROOT}/{result[i][1]}.jpg', {'x_scale': 0.2, 'y_scale': 0.2})

    workbook.close()

    for i in result:
        os.remove(f"{settings.MEDIA_ROOT}/{i[1]}.jpg")

class QC:
    def __init__(self) -> None:
        self.image = ''
        self.name = ''
        self.check = False

qc = QC()

channel_secret = '34a6dea6ea32658d3b481f6a3f35c7dd'
channel_access_token = 'yhPE6U2DxqW7tb+keI+qWVdtDSpqRW0zZ1rBBquECcScuQv1THI8w4AmgaI4Y9+CMpqhiAIeFteu+skyGtrfQs+tJRJa6EgBdT/MxnAmJGWZpSJRmmzd0eA3nc3aOFTyS/8OoRQsNAcZvVPdikpLaAdB04t89/1O/w1cDnyilFU='

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

@csrf_exempt
def callback(request):
    # get X-Line-Signature header value
    signature = request.META['HTTP_X_LINE_SIGNATURE']

    # get request body as text
    body = request.body.decode('utf-8')
    # handle webhook body
    try:
        handler.handle(body, signature)
    except:
        print('error')
    return render(request,'webhook.html')

@handler.default()
def message_text(event):
    if event.message.type == 'text':

        text = event.message.text
        print(text)
        if text == 'clear':
            qc.check = False
            qc.image = ''
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"เคลียร์เรียบร้อย !!")
            )
            qc.check = False
        elif text == 'export excel':
            export()
            template_message = template()
            # Send the message
            line_bot_api.reply_message(
                event.reply_token,
                template_message)

        else:
            if qc.check:
                user = line_bot_api.get_profile(event.source.user_id).display_name
                task = """ INSERT INTO muslin.qc_data(id, name, image,date,user)\
                            VALUES (%s,%s,%s,now(),%s)"""
                db.query_with_image(task, (0, text, qc.image,user))
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="บันทึกสำเร็จ !!")
                )
                qc.check = False
            elif not(qc.check):
                pass
    elif event.message.type == 'image':
        qc.check = True
        image_content = line_bot_api.get_message_content(event.message.id).content
        qc.image = image_content
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='ใส่รายละเอียด : ')
        )

    else:
        qc.check = False
        pass

# webhook line bot QC PART ----------------------------

# webhook line bot WRONG SEND PART ----------------------------

def insert_wrong_send(data):
    dep,user,wrong_send_department,detail = data
    db.query_commit(f'insert into {dep}.wrong_send value (0,"{user}","{wrong_send_department}","{detail}",now())')
    task = "select max(id) from wrong_send"
    result = db.query_custom(task,dep)
    result = list(result.fetchall())
    id = result[0][0]
    return id

def export_wrong_send():
    task = 'select DATE_ADD(date, INTERVAL 7 HOUR),id,image,name from muslin.qc_data'
    result = db.query(task)
    result = list(result.fetchall())
    for i in result:
        with open(f"{settings.MEDIA_ROOT}/{i[1]}.jpg",'wb') as f:
            f.write(i[2])

    workbook = xlsxwriter.Workbook(f'{settings.MEDIA_ROOT}/export_data.xlsx')
    # Create an new Excel file and add a worksheet.
    worksheet = workbook.add_worksheet()
    # Widen the first column to make the text clearer.
    worksheet.set_column('A:A', 30)
    for i in range(len(result)):
        row_index = i + 1
        
        row = (row_index - 1) * 20
        if i == 0:
            row = row_index

        # Insert an image.
        worksheet.write(f'A{row}', str(result[i][0]))
        worksheet.write(f'B{row}', result[i][3])
        worksheet.insert_image(f'C{row}', f'{settings.MEDIA_ROOT}/{result[i][1]}.jpg', {'x_scale': 0.2, 'y_scale': 0.2})

    workbook.close()

    for i in result:
        os.remove(f"{settings.MEDIA_ROOT}/{i[1]}.jpg")

class Wrong_send:
    def __init__(self) -> None:
        self.image = []
        self.name = ''
        self.check = False

wrong_send = Wrong_send()

channel_secret_wrong_send = '3a7643011721b77d9d3003b891039e20'
channel_access_token_wrong_send = '7jkCde1p6aAZLxquGd4CrJaxniaHqEEGJDKxBY2uFiCgKZfIchTwuCGPRRt4n687DEoD4+G+2Ghy0CDIuJzJ1tcjsbDKJAoGmUlYhqUDn8OkcPW2XHUQUObTQF2Aqmteb4AbeftjxuTpMitZb921SwdB04t89/1O/w1cDnyilFU='

line_bot_api_wrong_send = LineBotApi(channel_access_token_wrong_send)
handler_wrong_send = WebhookHandler(channel_secret_wrong_send)

@csrf_exempt
def callback_wrong_send(request):
    # get X-Line-Signature header value
    signature = request.META['HTTP_X_LINE_SIGNATURE']

    # get request body as text
    body = request.body.decode('utf-8')
    # handle webhook body
    try:
        handler_wrong_send.handle(body, signature)
    except:
        print('error')
    return render(request,'webhook.html')

@handler_wrong_send.default()
def message_text(event):
    try:
        if event.message.type == 'text':

            text = event.message.text
            print(text)
            if text == 'clear':
                wrong_send.check = False
                wrong_send.image = []
                line_bot_api_wrong_send.reply_message(
                event.reply_token,
                TextSendMessage(text=f"เคลียร์เรียบร้อย !!")
                )
                wrong_send.check = False
            elif text == 'export excel':
                export()
                template_message = template()
                # Send the message
                line_bot_api_wrong_send.reply_message(
                    event.reply_token,
                    template_message)

            else:
                if wrong_send.check:
                    dep,wrong_send_department,detail = text.split('/')
                    user = line_bot_api_wrong_send.get_profile(event.source.user_id).display_name
                    data = dep,user,wrong_send_department,detail
                    id = insert_wrong_send(data)
                    for i in wrong_send.image:
                        task = f""" INSERT INTO {dep}.wrong_send_image(id, image)\
                                    VALUES (%s,%s)"""
                        db.query_with_image(task, (id, i))
                    line_bot_api_wrong_send.reply_message(
                        event.reply_token,
                        TextSendMessage(text="บันทึกสำเร็จ !!")
                    )
                    wrong_send.check = False
                elif not(wrong_send.check):
                    pass
                
        elif event.message.type == 'image':
            wrong_send.check = True
            image_content = line_bot_api_wrong_send.get_message_content(event.message.id).content
            wrong_send.image.append(image_content)
        else:
            wrong_send.check = False
            pass
    except Exception as E:
            wrong_send.check = False
            wrong_send.image = []
            line_bot_api_wrong_send.reply_message(
            event.reply_token,
            TextSendMessage(text=f'บันทึกไม่สำเร็จ : {E} ')
            )
# webhook line bot WRONG SEND PART ----------------------------

# webhook line bot SOLD_OUT PART ----------------------------
class SOLDOUT:
    def __init__(self) -> None:
        self.image = ''
        self.name = ''
        self.check = False

soldout = SOLDOUT()

def random_char(y):
       return ''.join(random.choice(string.ascii_letters) for x in range(y))

def insert_soldout(data):
    dep,user,header,detail,img_name = data
    db.query_commit(f"insert into {dep}.soldout values (0,'{user}','{header}','{detail}','ยังไม่เคลียร์',now(),'',NULL,'stock','')")
    task = "select max(id) from soldout"
    result = db.query_custom(task,dep)
    result = list(result.fetchall())
    id = result[0][0]
    db.query_commit(f"insert into {dep}.soldoutimage values ({id},'media/soldout/{img_name}.jpg')")
    return id

channel_secret_sold_out = 'ec27c5632b4fd85f0d88650fa19e29d1'
channel_access_token_sold_out = 'jZYUZseFejcfL1U9K3CFEKqfLBCD/qc9g9BF1ljrZUArRTzU22t1OfIDCAzABSnHIZA4fIPOWUXkznfzzp8dhQfFW1EH5JdueEsL+c3LT0Ce9pAwUmAhNGBXit72zjBH7et2y6+4iAQBqy8h1LTDvQdB04t89/1O/w1cDnyilFU='

line_bot_api_sold_out = LineBotApi(channel_access_token_sold_out)
handler_sold_out = WebhookHandler(channel_secret_sold_out)

@csrf_exempt
def callback_soldout(request):
    # get X-Line-Signature header value
    signature = request.META['HTTP_X_LINE_SIGNATURE']

    # get request body as text
    body = request.body.decode('utf-8')
    # handle webhook body
    handler_sold_out.handle(body, signature)
    return render(request,'webhook.html')


@handler_sold_out.default()
def message_text(event):
    try:
        if event.message.type == 'text':

            text = event.message.text
            print(text)
            if text == 'clear':
                soldout.check = False
                soldout.image = ''
                line_bot_api_sold_out.reply_message(
                event.reply_token,
                TextSendMessage(text=f"เคลียร์เรียบร้อย !!")
                )
                soldout.check = False
            else:
                if soldout.check:
                    img_name = random_char(10)
                    with open(f'{settings.MEDIA_ROOT}/soldout/{img_name}.jpg','wb') as f:
                        f.write(soldout.image)

                    user = line_bot_api_sold_out.get_profile(event.source.user_id).display_name
                    dep,header,detail = text.split('/')
                    data = dep,user,header,detail,img_name
                    id = insert_soldout(data)
                    line_bot_api_sold_out.reply_message(
                        event.reply_token,
                        TextSendMessage(text=f"บันทึกเร็จ : https://139-162-28-194.ip.linodeusercontent.com/blog/soldout/detail/{id}/")
                    )
                    soldout.check = False
                elif not(soldout.check):
                    pass

        elif event.message.type == 'image':
            soldout.check = True
            image_content = line_bot_api_sold_out.get_message_content(event.message.id).content
            soldout.image = image_content
        else:
            soldout.check = False
            pass
    except Exception as E:
        soldout.check = False
        soldout.image = ''
        line_bot_api_sold_out.reply_message(
            event.reply_token,
            TextSendMessage(text=f'บันทึกไม่สำเร็จ :{E}')
        )

# webhook line bot SOLD_OUT PART ----------------------------

@csrf_exempt
def editorder(req):
    dep = "muslin"
    if req.method == 'POST':
        try:
            sku = req.POST.get("datas")
            res = json.loads(sku)
            if not res['status'] == 'Voided':
                task =f"""update {dep}.deli_zort
                    set status = '{str(res['status'])}',customername='{str(res['customername'])}',trackingno='{str(res['trackingno'])}',shippingtime='{datetime.datetime.now()}',
                    paymentstatus='{str(res['paymentstatus'])}'
                    where idorder = {res['id']}"""
                
                db.query_commit(task)
                db.query_commit(f"delete from {dep}.order_main where IDorder = '{res['id']}'")
                for i in res['list']:
                    db.query_commit(f"insert into {dep}.order_main\
                        values ('{res['id']}','{i['pricepernumber']}','{i['sku']}','{res['amount']}','{i['number']}')")
            else:
                db.query_commit(f"delete from {dep}.deli_zort\
                    where idorder = {res['id']}")
        except Exception as e:
            print(e)
    return render(req,'webhook.html')

@csrf_exempt
def addorder(req):
    dep = "muslin"
    if req.method == 'POST':
        try:
            sku = req.POST.get("datas")
            res = json.loads(sku)
            if not res['trackingno']:
                res['trackingno'] = ''
            task = f"insert into {dep}.deli_zort\
                values ('{res['id']}','{res['number']}','{res['status']}','{res['customername']}','{datetime.datetime.now()}','{str(res['trackingno'])}',0,NULL,NULL,\
                 '{str(res['paymentstatus'])}','{str(res['shippingaddress'])}','{str(res['shippingphone'])}')"
            
            db.query_commit(task)
            for i in res['list']:
                task = f"insert into {dep}.order_main\
                    values ('{res['id']}','{i['pricepernumber']}','{i['sku']}','{res['amount']}','{i['number']}')"
                db.query_commit(task)

        except Exception as e:
            print(e)

    return render(req,'webhook.html')

@csrf_exempt
def updatetracking(req):
    dep = "muslin"
    if req.method == 'POST':
        try:
            sku = req.POST.get("datas")
            res = json.loads(sku)
            task = f"""update {dep}.deli_zort\
                set trackingno='{str(res['trackingno'])}'
                where idorder = {res['id']}"""
            
            db.query_commit(task)

        except Exception as e:
            print(e)

    return render(req,'webhook.html')

@csrf_exempt
def editproduct(req):
    def get_amount(sku,amount):
        result = db.query(f"select amount from muslin.stock where sku = '{sku}'")
        result = list(result.fetchall())[0][0]
        result = int(result)
        new_amount = 3 - amount
        if result - new_amount >= 0:
            return 3,result - new_amount
        else:
            return amount + result,0

    dep = "muslin"
    web = Web(get_api_register(dep,'apikey'),get_api_register(dep,'apisecret'),get_api_register(dep,'storename'))
    try:
        sku = req.POST.get("datas")
        res = json.loads(sku)
    except:
        return render(req,'webhook.html')
    if req.method == 'POST':
        try:
            if int(res['available']) < 3:
                send_line('start')
                zort_amount,stock_amount = get_amount(res['sku'],res['available'])
                send_line(f"zort will have {zort_amount} stock amount will have {stock_amount}")
                db.query_commit(f"update {dep}.stock set amount = {stock_amount} where sku = '{res['sku']}'")
                web.post("UPDATEPRODUCTAVAILABLESTOCKLIST",res['sku'],zort_amount)
        except Exception as e:
            print(e)
        db.query_commit(f'update {dep}.stock_main set descript = "{res["name"]}" where sku = "{res["sku"]}"')
    return render(req,'webhook.html')


@csrf_exempt
def editorder_maruay(req):
    dep = "maruay"
    if req.method == 'POST':
        try:
            sku = req.POST.get("datas")
            res = json.loads(sku)
            if not res['status'] == 'Voided':
                task =f"""update maruay.deli_zort\
                    set status = '{str(res['status'])}',customername='{str(res['customername'])}',trackingno='{str(res['trackingno'])}',shippingtime='{datetime.datetime.now()}',paymentstatus=>
                    where idorder = {res['id']}"""
                
                db.query_commit(task)
                db.query_commit(f"delete from maruay.order_main where IDorder = '{res['id']}'")
                for i in res['list']:
                    db.query_commit(f"insert into maruay.order_main\
                        values ('{res['id']}','{i['pricepernumber']}','{i['sku']}','{res['amount']}','{i['number']}')")
            else:
                db.query_commit(f"delete from maruay.deli_zort\
                    where idorder = {res['id']}")
        except Exception as e:
            print(e)
    return render(req,'webhook.html')

@csrf_exempt
def addorder_maruay(req):
    dep = "maruay"
    if req.method == 'POST':
        try:
            sku = req.POST.get("datas")
            res = json.loads(sku)
            if not res['trackingno']:
                res['trackingno'] = ''
            task = f"insert into maruay.deli_zort\
                values ('{res['id']}','{res['number']}','{res['status']}','{res['customername']}','{datetime.datetime.now()}','{str(res['trackingno'])}',0,NULL,NULL,\
                 '{str(res['paymentstatus'])}','{str(res['shippingaddress'])}','{str(res['shippingphone'])}')"
            
            db.query_commit(task)
            for i in res['list']:
                task = f"insert into maruay.order_main\
                    values ('{res['id']}','{i['pricepernumber']}','{i['sku']}','{res['amount']}','{i['number']}')"
                db.query_commit(task)

        except Exception as e:
            print(e)

    return render(req,'webhook.html')

@csrf_exempt
def updatetracking_maruay(req):
    dep = "maruay"
    if req.method == 'POST':
        try:
            sku = req.POST.get("datas")
            res = json.loads(sku)
            task = f"""update maruay.deli_zort\
                set trackingno='{str(res['trackingno'])}'
                where idorder = {res['id']}"""
            db.query_commit(task)

        except Exception as e:
            print(e)

    return render(req,'webhook.html')

@csrf_exempt
def editproduct_maruay(req):
    dep = 'maruay'
    def get_amount(sku,amount):
        result = db.query(f"select amount from {dep}.stock where sku = '{sku}'")
        result = list(result.fetchall())[0][0]
        result = int(result)
        new_amount = 3 - amount
        if result - new_amount >= 0:
            return 3,result - new_amount
        else:
            return amount + result,0

    web = Web(get_api_register(dep,'apikey'),get_api_register(dep,'apisecret'),get_api_register(dep,'storename'))
    try:
        sku = req.POST.get("datas")
        res = json.loads(sku)
    except:
        return render(req,'webhook.html')
    if req.method == 'POST':
        try:
            if int(res['available']) < 3:
                send_line('start')
                zort_amount,stock_amount = get_amount(res['sku'],res['available'])
                send_line(f"zort will have {zort_amount} stock amount will have {stock_amount}")
                db.query_commit(f"update {dep}.stock set amount = {stock_amount} where sku = '{res['sku']}'")
                web.post("UPDATEPRODUCTAVAILABLESTOCKLIST",res['sku'],zort_amount)
        except Exception as e:
            print(e)
        db.query_commit(f'update {dep}.stock_main set descript = "{res["name"]}" where sku = "{res["sku"]}"')
    return render(req,'webhook.html')
