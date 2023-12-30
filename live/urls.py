from django.urls import path
from . import views

# URLConf
urlpatterns = [
    path('main/', views.main),
    path('export_excel/', views.export_live_excel),
    path('import_excel/', views.import_excel),
    path('prism/<idsell>', views.prism),
    path('addnote/', views.addnote),
    path('room/', views.room),
    path('add/<name>',views.add_page,name='add'),
    path('del/<name>',views.del_page,name='del'),
]