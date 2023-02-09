from django.core.files.storage import FileSystemStorage
from django.shortcuts import render,redirect
from function import *
from stock.views import result
# Create your views here.

def blog(req):
    dep = get_role(req,'department')
    role = get_role(req,'role')
    task = """
    select blog.id,header,max(imagepath),created_by,answer from blog inner join blogimage on blog.id = blogimage.id where submit_time is NULL
    group by blog.id
    """
    result = db.query_custom(task,dep)
    result = list(result.fetchall())
    task = """
    select descript from stock_main
    """
    sku = db.query_custom(task,dep)
    sku = list(sku.fetchall())
    sku = [i[0] for i in sku]
    task = """
    select header from blog
    group by header
    order by count(header) desc
    """
    headerlist = db.query_custom(task,dep)
    headerlist = list(headerlist.fetchall())
    headerlist = [i[0] for i in headerlist]
    context = {"result":result,
    'skus':sku,
    'headerlist':headerlist}
    return render(req,'home.html',context)

def soldOut(req):
    dep = get_role(req,'department')
    task = """
    select soldout.id,header,max(imagepath),created_by,answer,status from soldout inner join soldoutimage on soldout.id = soldoutimage.id
    group by soldout.id order by id desc
    """
    result = db.query_custom(task,dep)
    result = list(result.fetchall())
    
    task = """
    select header from soldout
    group by header
    order by count(header) desc
    """
    headerlist = db.query_custom(task,dep)
    headerlist = list(headerlist.fetchall())
    headerlist = [i[0] for i in headerlist]
    context = {"result":result,
    'headerlist':headerlist}
    return render(req,'soldOut.html',context)

def soldoutinsertBlog(request):
    dep = get_role(request,'department')
    role = get_role(request,'role')
    if request.method == 'POST':
        header = request.POST.get('header')
        detail = request.POST.get('detail')
        db.query_commit(f"insert into {dep}.soldout values (0,'{request.user}','{header}','{detail}','ยังไม่เคลียร์',now(),'',NULL,'{role}','')")
        send_line_blog_admin(f"มีแจ้งเตือนของหมด หัวข้อ {header} ร้าน {dep}")
        if request.FILES['myfile']:
            myfile = request.FILES.getlist('myfile')
            for i in myfile:
                fs = FileSystemStorage()
                filename = fs.save(f"soldout/{i.name}", i)
                task = "select max(id) from soldout"
                result = db.query_custom(task,dep)
                result = list(result.fetchall())
                id = result[0][0]
                db.query_commit(f"insert into {dep}.soldoutimage values ({id},'media/soldout/{i.name}')")
    return redirect("/blog/soldout/")

def insertBlog(request):
    dep = get_role(request,'department')
    role = get_role(request,'role')
    if request.method == 'POST':
        header = request.POST.get('header')
        detail = request.POST.get('detail')
        db.query_commit(f"insert into {dep}.blog values (0,'{request.user}','{header}','{detail}','ยังไม่เคลียร์',now(),'',NULL,'{role}','')")
        if role != 'stock':
            send_line_blog(f"มี blog ใหม่ หัวข้อ {header} ร้าน {dep}")
        else:
            send_line_blog_admin(f"มี blog ใหม่ หัวข้อ {header} ร้าน {dep}")
        if request.FILES['myfile']:
            myfile = request.FILES.getlist('myfile')
            for i in myfile:
                fs = FileSystemStorage()
                filename = fs.save(f"blogs/{i.name}", i)
                task = "select max(id) from blog"
                result = db.query_custom(task,dep)
                result = list(result.fetchall())
                id = result[0][0]
                db.query_commit(f"insert into {dep}.blogimage values ({id},'media/blogs/{i.name}')")
    return redirect("/blog/")

def detail(req,id):
    dep = get_role(req,'department')
    role = get_role(req,'role')
    if role == 'admin':
        task = f"select header,detail,imagepath from blog inner join blogimage on blog.id = blogimage.id where blog.id = {id}"
    else:
        task = f"select header,if(answer = '',detail,answer),imagepath from blog inner join blogimage on blog.id = blogimage.id where blog.id = {id}"
    result = db.query_custom(task,dep)
    result = list(result.fetchall())
    details = result[0][0]
    header = result[0][1]
    image = [i[2] for i in result]
    context = {"details":details,
                "header":header,
                'image':image,
                "id":id,}
    return render(req,'detail.html',context)

def soldoutdetail(req,id):
    dep = get_role(req,'department')
    task = f"select header,detail,imagepath from soldout inner join soldoutimage on soldout.id = soldoutimage.id where soldout.id = {id}"
    result = db.query_custom(task,dep)
    result = list(result.fetchall())
    details = result[0][0]
    header = result[0][1]
    image = [i[2] for i in result]
    context = {"details":details,
                "header":header,
                'image':image,
                "id":id,}
    return render(req,'soldoutdetail.html',context)

def confirm(req,id):
    dep = get_role(req,'department')
    role = get_role(req,'role')
    answer = req.POST.get(f"{id}answer")
    if not answer:
        answer = ''

    if role == 'stock':
        task = f"update {dep}.blog set status = 'เคลียร์แล้ว',submit_by = '{req.user}',submit_time = now(),answer = '{answer}' where id = {id}"
    else:
        task = f"update {dep}.blog set submit_by = '{req.user}',answer = '{answer}' where id = {id}"
    db.query_commit(task)
    return redirect("/blog/")

def soldoutconfirm(req,id):
    dep = get_role(req,'department')
    confirm = req.POST.get("confirm")
    cancel = req.POST.get("cancel")
    greeting = req.POST.get("greeting")
    task = f"select submit_time,header,status from soldout where id = {id}"
    result = db.query_custom(task,dep)
    result = list(result.fetchall())
    if result[0][0] and result[0][2] == 'เคลียร์แล้ว' and confirm:
        task = f"update {dep}.soldout set header = '{result[0][1]}  (CLEAR)' where id = {id}"
        db.query_commit(task)
        return redirect("/blog/soldout/")
    else:
        pass
    if confirm:
        task = f"update {dep}.soldout set status = 'เคลียร์แล้ว',submit_by = '{req.user}',submit_time = now() where id = {id}"
    elif cancel:
        task = f"update {dep}.soldout set status = 'ยกเลิก',submit_by = '{req.user}',submit_time = now() where id = {id}"
    else:
        task = f"update {dep}.soldout set status = 'ทัก',submit_by = '{req.user}' where id = {id}"
    db.query_commit(task)
    return redirect("/blog/soldout/")

def reserve(req):
    dep = get_role(req,'department')
    if req.method == "POST":
        fname = req.POST.get('fname')
        sku = req.POST.get('sku')
        task = f"""
        select id,fname,sku,comment from reserve where fname like '%{fname}%' and sku like '%{sku}%'
        """
    else:
        task = """
        select id,fname,sku,comment from reserve
        """
    result = db.query_custom(task,dep)
    result = list(result.fetchall())
    result = db.query_custom(task,dep)
    data = list(result.fetchall())
    task = """
    select descript from stock_main
    """
    skus = db.query_custom(task,dep)
    skus = list(skus.fetchall())
    skus = [i[0] for i in skus]
    context=  {'data':data,
                "skus":skus}


    return render(req,"reserve.html",context)

def addreserve(req):
    dep = get_role(req,'department')
    fname = req.POST.get('fname')
    sku = req.POST.get('sku')
    comment = req.POST.get('comment')
    db.query_commit(f"insert into {dep}.reserve values (0,'{fname}','{sku}','{comment}',now())")

    return redirect('/blog/reserve/')

def deleteReserve(req,id):
    dep = get_role(req,'department')
    db.query_commit(f'delete from {dep}.reserve where id = {id}')
    return redirect('/blog/reserve/')
