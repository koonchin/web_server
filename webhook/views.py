
from django.http import JsonResponse
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

# webhook line bot QC PART ----------------------------

def template():
    # Create a URIAction for the file
    uri_action = URIAction(
        label='Open File',
        uri='https://139-177-190-161.ip.linodeusercontent.com/media/export_data.xlsx'
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

# def export(firstdate,lastdate):
#     task = f'select DATE_ADD(date, INTERVAL 7 HOUR),id,image,name from muslin.qc_data where date > "{firstdate}" and date < "{lastdate}"'
#     result = db.query(task)
#     result = list(result.fetchall())
#     for i in result:
#         with open(f"{settings.MEDIA_ROOT}/{i[1]}.jpg",'wb') as f:
#             f.write(i[2])

#     workbook = xlsxwriter.Workbook(f'{settings.MEDIA_ROOT}/export_data.xlsx')
#     # Create an new Excel file and add a worksheet.
#     worksheet = workbook.add_worksheet()
#     # Widen the first column to make the text clearer.
#     worksheet.set_column('A:A', 30)
#     for i in range(len(result)):
#         row_index = i + 1
        
#         row = (row_index - 1) * 20
#         if i == 0:
#             row = row_index

#         # Insert an image.
#         worksheet.write(f'A{row}', str(result[i][0]))
#         worksheet.write(f'B{row}', result[i][3])
#         worksheet.insert_image(f'C{row}', f'{settings.MEDIA_ROOT}/{result[i][1]}.jpg', {'x_scale': 0.2, 'y_scale': 0.2})

#     workbook.close()

#     for i in result:
#         os.remove(f"{settings.MEDIA_ROOT}/{i[1]}.jpg")
def extract_digits(input_string):
    # Use regular expression to find all digits in the input string
    digits = re.findall(r'\d+', input_string)
    
    # Combine the digits into a single string
    result = ''.join(digits)
    
    try:
        return int(result)
    except:
        return 0

def export(firstdate, lastdate):
    data_dict = {
    4000: 'D',
    80: 'D',
    81: 'D',
    82: 'D',
    83: 'D',
    347: 'M',
    360: 'M',
    526: 'M',
    527: 'M',
    792: 'M',
    797: 'M',
    798: 'M',
    938: 'M',
    941: 'M',
    989: 'M',
    1017: 'M',
    1081: 'M',
    1083: 'M',
    1084: 'M',
    1092: 'M',
    1093: 'M',
    1098: 'M',
    1126: 'M',
    1127: 'M',
    1137: 'M',
    1138: 'M',
    1148: 'M',
    1149: 'M',
    1201: 'M',
    1202: 'M',
    1203: 'M',
    1206: 'M',
    1215: 'M',
    1216: 'M',
    3000: 'M',
    330: 'O',
    482: 'O',
    1099: 'O',
    1158: 'O',
    1175: 'O',
    1179: 'O',
    1183: 'O',
    1186: 'O',
    1188: 'O',
    1198: 'O',
    1207: 'O',
    1208: 'O',
    1209: 'O',
    1213: 'O',
    2000: 'O'
    }

    task = f'select DATE_ADD(date, INTERVAL 7 HOUR),id,image,name from muslin.qc_data where date > "{firstdate}" and date < "{lastdate}"'
    result = db.query(task)
    result = list(result.fetchall())

    workbook = xlsxwriter.Workbook(f'{settings.MEDIA_ROOT}/export_data.xlsx')
    # Create a dictionary to map the sheet names with the respective data
    sheet_data = {}
    sheet_name_list = []
    # Initialize the row index within each sheet
    sheet_row_index = {}

    # Iterate over the results
    for i in range(len(result)):
        # Get the current sheet name
        temp = get_text_after_alphabet(result[i][3].strip())
        first_letter = temp[0]
        if first_letter == 'M' and not str(temp[1]).isdigit():
            sheet_name = "Maruay"
        else:
            second_letter = temp[1]
            if str(second_letter).isdigit():
                second_letter = temp[0]
            sheet_name = f"{second_letter.upper()}"
            if second_letter.upper() in ['B','C','D']:
                sheet_name = 'B,C,D'
            elif second_letter.upper() not in ['A','B','C','D','G']:
                digit = extract_digits(temp.split('-')[0])
                if int(digit) in data_dict:
                    sheet_name = data_dict[int(digit)]
                elif digit > 1999 and digit < 3000:
                    sheet_name = 'O'
                elif digit > 2999 and digit < 4000:
                    sheet_name = 'M'
                elif digit > 3999 and digit < 5000:
                    sheet_name = 'D'
                else:
                    if second_letter.upper() in ['Y']:
                        sheet_name = "Y"
                    else:
                        sheet_name = "Satin"

        # Check if the sheet_name already exists in the dictionary
        if sheet_name not in sheet_data:
            sheet_data[sheet_name] = []

        # Check if the sheet_row_index exists for the current sheet, initialize if not
        if sheet_name not in sheet_row_index:
            sheet_row_index[sheet_name] = 1

        # Get the current row index and increment it for the next iteration
        row_index = sheet_row_index[sheet_name]
        sheet_row_index[sheet_name] += 20

        # Save the image
        with open(f"{settings.MEDIA_ROOT}/{result[i][1]}.jpg", 'wb') as f:
            f.write(result[i][2])

        # Insert data and images into the worksheet
        if sheet_name not in sheet_name_list:
            worksheet = workbook.add_worksheet(sheet_name)
            worksheet.set_column('A:A', 30)
            sheet_name_list.append(sheet_name)
        else:
            worksheet = workbook.get_worksheet_by_name(sheet_name)

        worksheet.write(f'A{row_index}', str(result[i][0]))
        worksheet.write(f'B{row_index}', result[i][3])
        worksheet.insert_image(f'C{row_index}', f'{settings.MEDIA_ROOT}/{result[i][1]}.jpg', {'x_scale': 0.2, 'y_scale': 0.2})
    # Sort the sheet_name_list alphabetically
    sheet_name_list = sorted(sheet_name_list)

    # Reorder the worksheets based on the sorted sheet_name_list
    workbook.worksheets_objs.sort(key=lambda x: sheet_name_list.index(x.get_name()))

    workbook.close()

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
        elif 'export excel' in text:
            _, firstdate, lastdate = text.split(',')
            try:
                export(firstdate,lastdate)
                print('exported')
                # template_message = template()
                # Send the message
                line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="https://139-177-190-161.ip.linodeusercontent.com/media/export_data.xlsx"))
            except Exception as E:
                line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"{E} error 130")
                )

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
                        TextSendMessage(text=f"บันทึกเร็จ : htthttps://139-177-190-161.ip.linodeusercontent.com/blog/soldout/detail/{id}/")
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
        #line_bot_api_sold_out.reply_message(
        #    event.reply_token,
        #    TextSendMessage(text=f'บันทึกไม่สำเร็จ :{E}')
        #)

# webhook line bot SOLD_OUT PART ----------------------------

# webhook line bot DAILY REPORT PART ----------------------------
class DailyReport:
    def __init__(self) -> None:
        self.name = ''
        self.check = False
dailyreport = DailyReport()

channel_secret_daily_report = 'fbb1d0a129910dfb8bb7b2d43c910318'
channel_access_token_daily_report = 'w6F1ffyyanDJ+PMtmekbkLiKyNqQID1cWIM1u9oKwdRymskGI9BMCEplfSDsueuv/zOwv401JLWIAYNXucK6E3CuGnZWwTJxMgi91cIaY9L0tVYMPcdW3VuYDr3eEgJ+p6/bzcIeNf+21naBySayUwdB04t89/1O/w1cDnyilFU='

line_bot_api_daily_report = LineBotApi(channel_access_token_daily_report)
handler_daily_report = WebhookHandler(channel_secret_daily_report)

@csrf_exempt
def callback_daily_report(request):
    # get X-Line-Signature header value
    signature = request.META['HTTP_X_LINE_SIGNATURE']

    # get request body as text
    body = request.body.decode('utf-8')
    # handle webhook body
    handler_daily_report.handle(body, signature)
    return render(request,'webhook.html')


@handler_daily_report.default()
def message_text(event):
    try:
        if event.message.type == 'text':
            text = event.message.text
            print(text)
            if text == 'ยอดขายรายเดือน':
                dep = 'muslin'
                web = Web(get_api_register(dep,'apikey'),get_api_register(dep,'apisecret'),get_api_register(dep,'storename'))
                result = web.send_sales_report_monthly(dep)
                dep = 'maruay'
                web = Web(get_api_register(dep,'apikey'),get_api_register(dep,'apisecret'),get_api_register(dep,'storename'))
                result_jj = web.send_sales_report_monthly(dep)
                line_bot_api_daily_report.reply_message(
                event.reply_token,
                TextSendMessage(text=f"{text}\nmuslin\n{result}\n\n{text}\nmaruay\n{result_jj}")
                )
            elif text == 'ยอดขายวันนี้':
                dep = 'muslin'
                web = Web(get_api_register(dep,'apikey'),get_api_register(dep,'apisecret'),get_api_register(dep,'storename'))
                yesterday_date = datetime.datetime.now().strftime('%Y-%m-%d')
                result = web.send_sales_report(dep,yesterday_date)
                dep = 'maruay'
                web = Web(get_api_register(dep,'apikey'),get_api_register(dep,'apisecret'),get_api_register(dep,'storename'))
                result_jj = web.send_sales_report(dep,yesterday_date)
                line_bot_api_daily_report.reply_message(
                event.reply_token,
                TextSendMessage(text=f"{text}\nmuslin\n{result}\n\n{text}\nmaruay\n{result_jj}")
                )

            elif text == 'ยอดขายเมื่อวาน':
                dep = 'muslin'
                web = Web(get_api_register(dep,'apikey'),get_api_register(dep,'apisecret'),get_api_register(dep,'storename'))
                yesterday_date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
                result = web.send_sales_report(dep,yesterday_date)
                dep = 'maruay'
                web = Web(get_api_register(dep,'apikey'),get_api_register(dep,'apisecret'),get_api_register(dep,'storename'))
                result_jj = web.send_sales_report(dep,yesterday_date)
                line_bot_api_daily_report.reply_message(
                event.reply_token,
                TextSendMessage(text=f"{text}\nmuslin\n{result}\n\n{text}\nmaruay\n{result_jj}")
                )
            if text == 'ยอดแอด':
                spend_list = [get_ads_spend(access_tok, acc_id,'today') for acc_id in ad_acc_list]
                amount = sum(spend_list)
                
                spend_list_jj = [get_ads_spend(access_tok, acc_id,'today') for acc_id in ad_acc_list_maruay]
                amount_jj = sum(spend_list_jj)
                line_bot_api_daily_report.reply_message(
                event.reply_token,
                TextSendMessage(text=f"{text} muslin วันนี้ : {format(int(amount),',')}\n{text}maruay วันนี้ : {format(int(amount_jj),',')}")
                )
    except Exception as E:
        line_bot_api_daily_report.reply_message(
           event.reply_token,
           TextSendMessage(text=f'บันทึกไม่สำเร็จ :{E}')
        )

# webhook line bot DAILY REPORT PART ----------------------------

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

@csrf_exempt
def EMS_webhok(request):
    web = Web("7KRzYzjPqknzzSM2nVcooo3sWNF6EK4Oyq9QtGI8uyk=","RA9VD1AjwaHo8UW0uNk924SnxN0xIFIGdlelDEcTEE=","Muslin.info@gmail.com")
    web1 = Web("pteRXLvqBNcUXlgIB3RDHxBn3vXoi9cwRp6u/v9M=","GbJK2j7YS5dJtVaBomSsdyenjYuEwdI2A4gLPbKrRAI=","Maruay18.co.th@gmail.com")

    if request.method == 'POST':
        try:
            # Parse the incoming JSON data from the webhook
            data = json.loads(request.body)

            # Perform actions based on the webhook data
            # You can process the data and take appropriate actions here
            status = str(data['items'][0]['status'])
            barcode = data['items'][0]['barcode']
            if status == '103':
                a = f"muslin : {str(web.update_order_by_track(barcode))}"
                b = f"maruay : {str(web1.update_order_by_track(barcode))}"
            send_line_webhook(a)
            send_line_webhook(b)
            # Send a response to acknowledge the webhook
            response_data = {'message': 'Webhook received successfully'}
            return JsonResponse(response_data, status=200)

        except json.JSONDecodeError as e:
            # Handle JSON decoding errors
            response_data = {'error': 'Invalid JSON data'}
            send_line_webhook(e)
            return JsonResponse(response_data, status=400)

    else:
        # Return a 405 Method Not Allowed response for non-POST requests
        return JsonResponse({'error': 'Method not allowed'}, status=405)
