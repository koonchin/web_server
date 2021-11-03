from django.shortcuts import render,redirect
from function import *
import os
import shutil
import time
from zipfile import ZipFile
from os.path import basename
from django.core.paginator import Paginator
from datetime import datetime
# Create your views here.

def image_admin(req):
    size_dict = {1: None, 2: 'S', 3: 'M', 4: 'L', 5: 'XL', 6: '2XL', 7: '3XL'}
    inches_dict = {'breast': 'รอบอก', 'wrest': 'เอว',
                   'hip': 'สะโพก', 'len': 'กางเกงยาว'}
    dep = get_role(req,'department')
    downloads = None
    if req.method == 'POST':
        sku = req.POST.get("sku")
        name = req.POST.get("name")
        size = req.POST.get("size")
        breastmax = int(req.POST.get("breastmax"))
        wrestmax =int(req.POST.get("wrestmax"))
        hipmax = int(req.POST.get("hipmax"))
        breastmin = int(req.POST.get("breastmin"))
        wrestmin = int(req.POST.get("wrestmin"))
        hipmin = int(req.POST.get("hipmin"))

        downloads = req.POST.getlist('checkSKU')
        size = size_dict[int(size)]
        if size:
            task = f"""select sku,descript,amount,size,image,data_size from {dep}.stock_zort
                where sku like '%{sku}%' and amount > 0
                and size = '{size}'
                and descript like '%{name}%'
                and breast >= {breastmin} and breast <= {breastmax}
                and minwrest >= {wrestmin} and maxwrest <= {wrestmax}
                and hip >= {hipmin} and hip <= {hipmax}
                order by amount DESC """
        else:
            task = f"""select sku,descript,amount,size,image,data_size from {dep}.stock_zort
                    where sku like '%{sku}%' and amount > 0
                    and descript like '%{name}%'
                    and breast >= {breastmin} and breast <= {breastmax}
                    and minwrest >= {wrestmin} and maxwrest <= {wrestmax}
                    and hip >= {hipmin} and hip <= {hipmax}
                    order by amount DESC """
    else:
        task = f"""select sku,descript,amount,size,image,data_size from {dep}.stock_zort
                where amount > 0
                order by amount DESC"""
    mycursor = db.query(task)
    data = list(mycursor.fetchall())
    if downloads:
        sec = download_zip(data)
        return redirect(f'/media/image_admin/{sec}/{sec}.zip')
    else:
        for i in range(len(data)):
            data[i] += (i,)
            var = list(data[i])
            var[5] = str(var[5]).replace('/', '"')
            var[5] = ' '.join([inches_dict.get(i, i)
                                for i in var[5].split()])
            data[i] = tuple(var)
        # if not downloads:

        minbreast = db.query(f"select min(breast) from {get_role(req,'department')}.stock_zort where breast != ''").fetchone()[0]
        maxbreast = db.query(f"select max(breast) from {get_role(req,'department')}.stock_zort where breast != ''").fetchone()[0]
        minwrest = db.query(f"select min(minwrest) from {get_role(req,'department')}.stock_zort where minwrest != ''").fetchone()[0]
        maxwrest = db.query(f"select max(maxwrest) from {get_role(req,'department')}.stock_zort where maxwrest != ''").fetchone()[0]
        minhip = db.query(f"select min(hip) from {get_role(req,'department')}.stock_zort where hip != ''").fetchone()[0]
        maxhip = db.query(f"select max(hip) from {get_role(req,'department')}.stock_zort where hip != ''").fetchone()[0]

        content = {'data': data,
                    'breastmin':minbreast,
                    'breastmax':maxbreast,
                    'wrestmin':minwrest,
                    'wrestmax':maxwrest,
                    'hipmin':minhip,
                    'hipmax':maxhip,
                    }
        return render(req, 'image_table.html', content)
    # else:
        # sec = download_zip(data)
        # return redirect(f'/media/image_admin/{sec}/{sec}.zip')
# about api

def download_zip(myresult):
    var = []
    main('media/image_admin')
    sec = datetime.now().timestamp()
    sec = str(sec).split('.')[0]
    os.makedirs(f'media/image_admin/{sec}', exist_ok=True)
    for i in os.listdir(f'media/image_admin/'):
        if not os.path.isfile(f'media/image_admin/{i}'):
            for i2 in os.listdir(f'media/image_admin/{i}'):
                if os.path.isfile(f'media/image_admin/{i}/{i2}'):
                    if f'media/image_admin/{i}/{i2}'.endswith('.png'):
                        os.remove(f'media/image_admin/{i}/{i2}')
                
                
    for i in range(len(myresult)):
        if not myresult[i][4] == 'None':
            if not str(myresult[i][0])[:6] in var:
                var.append(str(myresult[i][0])[:6])
                try:
                    with open(f'media/image_admin/{sec}/{myresult[i][0]}.png', 'wb') as f:
                        f.write(convert_url_to_bytes(myresult[i][4]))
                except:
                    pass
                
    with ZipFile(f'media/image_admin/{sec}/{sec}.zip', 'w') as zipObj:
        # Iterate over all the files in directory
        for folderName, subfolders, filenames in os.walk(f'media/image_admin/{sec}'):
            for filename in filenames:
                if filename.endswith('.png'):
                    # create complete filepath of file in directory
                    filePath = os.path.join(folderName, filename)
                    # Add file to zip
                    zipObj.write(filePath, basename(filePath))

    for i in os.listdir(f'media/image_admin/{sec}'):
        if i.endswith('.png'):
            os.remove(f'media/image_admin/{sec}/{i}')
    return sec

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

    # removing the folder
    if not shutil.rmtree(path):

        # success message
        print(f"{path} is removed successfully")

    else:

        # failure message
        print(f"Unable to delete the {path}")


def remove_file(path):

    # removing the file
    if not os.remove(path):

        # success message
        print(f"{path} is removed successfully")

    else:

        # failure message
        print(f"Unable to delete the {path}")


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