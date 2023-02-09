from django.urls import path
from . import views

# URLConf
urlpatterns = [
    path('main/', views.main),
    path('addnote/', views.addnote),
    path('room/', views.room),
    path('add/<name>',views.add_page,name='add'),
    path('del/<name>',views.del_page,name='del'),
]