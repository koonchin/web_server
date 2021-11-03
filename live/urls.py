from django.urls import path
from . import views

# URLConf
urlpatterns = [
    path('main/', views.main_2),
    path('room/', views.room),
    path('add/<name>',views.add_page,name='add'),
    path('del/<name>',views.del_page,name='del'),
]