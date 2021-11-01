from django.urls import path

from . import views

# URLConf
urlpatterns = [
    path('', views.hello),
    path('check/',views.check),
    path('result/',views.result),
    path('barcode/',views.barcode),
    path('barcode_/',views.barcode_),
    path('checkstock/',views.checkstock),
]
