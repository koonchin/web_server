from django.urls import path

from . import views

# URLConf
urlpatterns = [
    path('', views.hello),
    path('export/', views.exportCheckin),
    path('exportrma/', views.exportrma),
    path('transfer/', views.transferVrich),
    path('postZero/', views.postZeroFunction),
    path('managelive/', views.managelive),
    path('file/', views.simple_upload),
    path('check/',views.check),
    path('check/<track>',views.confirm),
    path('result/',views.result),
    path('barcode/',views.barcode),
    path('barcode_/',views.barcode_),
    path('checkstock/',views.checkstock),
    path('countprint/',views.countprint),
    path('stock_check/',views.stock_check),
    path('VrichForm/',views.upstock_page),
    path('UpdateExcel/',views.UpdateExcel),
    path('UpdateExcelAndBringBack/',views.UpdateExcelAndBringBack),
    path('KorkaiUpload/',views.KorkaiUpload),
    path('UpdateOrderVrich/',views.UpdateOrderVrich),
    path('upstock/',views.upload_checkstock),
    path('secretUpstock/',views.secretUpstock),
    path('checkdiff/',views.upload_checkdiff),
    path('counted/',views.counted_print),
    path('uploadimage/',views.upload_image),
    path('uploadimage/file/',views.upload_image),
]
