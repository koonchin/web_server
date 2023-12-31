from django.urls import path

from . import views

# URLConf
urlpatterns = [
    path('',views.blog),
    path('soldout/',views.soldOut),
    path('detail/<id>/',views.detail),
    path('delete_blog/<id>/',views.delete_blog),
    path('soldout/detail/<id>/',views.soldoutdetail),
    path('add/',views.insertBlog),
    path('soldoutadd/',views.soldoutinsertBlog),
    path('confirm/<id>/',views.confirm),
    path('soldout/confirm/<id>/',views.soldoutconfirm),
    path('delete/<id>/',views.deleteReserve),
    path('reserve/',views.reserve),
    path('export_reserve/',views.export_reserve),
    path('addreserve/',views.addreserve),
]
