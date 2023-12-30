from django.urls import path

from . import views

# URLConf
urlpatterns = [
    path('callback/',views.callback),
    path('soldout/',views.callback_soldout),
    path('wrongsend/',views.callback_wrong_send),
    path('dailyreport/',views.callback_daily_report),
    path('update/',views.editorder),
    path('updatetracking/',views.updatetracking),
    path('add/',views.addorder),
    path('editproduct/',views.editproduct),
    path('update_maruay/',views.editorder_maruay),
    path('updatetracking_maruay/',views.updatetracking_maruay),
    path('add_maruay/',views.addorder_maruay),
    path('editproduct_maruay/',views.editproduct_maruay),
    path('EMS_webhook/',views.EMS_webhok),
]
