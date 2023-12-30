from django.core.files.storage import FileSystemStorage
from django.shortcuts import render,redirect
from function import *
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
        dbb = request.POST.get('Dobybot')

        if dbb:
            db.query_commit(f"insert into {dep}.blog values (0,'{request.user}','{header}','{detail}','ยังไม่เคลียร์',now(),'',NULL,'{role}','Dbb')")
        else:
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
    task = f"select header,detail,imagepath from blog inner join blogimage on blog.id = blogimage.id where blog.id = {id}"
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
        # Base query
        task = "SELECT id, fname, stock_main.sku, comment, date FROM reserve INNER JOIN stock_main ON reserve.sku = stock_main.sku"

        # Check if fname or sku is provided and add conditions accordingly
        if fname or sku:
            task += " WHERE"
            if fname:
                task += f" fname LIKE '%{fname}%'"
            if fname and sku:
                task += " OR"
            if sku:
                task += f" stock_main.sku LIKE '%{sku}%'"

        # Add the remaining part of the query
        task_detail = f"""
        SELECT data_size.idsell, COUNT(*) 
        FROM data_size 
        INNER JOIN stock_main ON data_size.sku = stock_main.sku 
        INNER JOIN reserve ON reserve.sku = stock_main.sku
        """

        # Check if fname or sku is provided and add conditions accordingly
        if fname or sku:
            task_detail += " WHERE"
            if fname:
                task_detail += f" fname LIKE '%{fname}%'"
            if fname and sku:
                task_detail += " OR"
            if sku:
                task_detail += f" stock_main.sku LIKE '%{sku}%'"

        task_detail += """
        GROUP BY data_size.idsell 
        ORDER BY COUNT(*) DESC;
        """
    else:
        task = 'select id,fname,stock_main.sku,comment,date from reserve inner join stock_main on reserve.sku = stock_main.sku'
        task_detail = """
        SELECT data_size.idsell, COUNT(*) 
        FROM data_size 
        INNER JOIN stock_main ON data_size.sku = stock_main.sku 
        INNER JOIN reserve ON reserve.sku = stock_main.sku 
        GROUP BY data_size.idsell 
        ORDER BY count(*) desc;
        """
    detail = list(db.query_custom(task,dep).fetchall())
    result = db.query_custom(task_detail,dep)
    data = list(result.fetchall())
    task = "select sku,descript from stock_main"
    skus = db.query_custom(task,dep)
    skus = list(skus.fetchall())

    context=  {'data':data,
                "skus":skus,
                'result':detail}

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

def delete_blog(req,id):
    dep = get_role(req,'department')
    task = f'delete from {dep}.blog where id = {id}'
    db.query_commit(task)
    return redirect('/blog/')

def export_reserve(req):
    dep = get_role(req,"department")
    task = f"""select fname,stock_main.sku,comment,DATE_ADD(date, INTERVAL 7 HOUR) from reserve inner join stock_main on stock_main.sku = reserve.sku"""
    result = db.query_custom(task,dep)
    result = list(result.fetchall())
    columns = ['Facebook name', 'Sku', 'Detail', 'Date']

    # Create a DataFrame using the result and columns
    df = pd.DataFrame(result, columns=columns)

    # Assuming 'df' is your DataFrame, you can now export it to an Excel file
    with pd.ExcelWriter(f'{settings.MEDIA_ROOT}/output.xlsx', engine='xlsxwriter') as writer:
        # Write the original data to the first sheet
        df.to_excel(writer, sheet_name='Sheet1', index=False)

        # Group by 'sku' and count the occurrences, create a new DataFrame
        sku_counts = df.groupby('Sku').size().reset_index(name='amount')

        # Write the grouped data to the second sheet
        sku_counts.to_excel(writer, sheet_name='Sheet2', index=False)
    return redirect('/media/output.xlsx')
