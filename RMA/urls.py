from django.urls import path

from . import views

# URLConf
urlpatterns = [
    path('',views.main),
    path('stock/',views.stock),
    path('add/<number>/',views.add),
    path('confirm/<id>/',views.confirm),
    path('delete/<id>/',views.deleteRMA),
    path('addorder/',views.addorder),
]
