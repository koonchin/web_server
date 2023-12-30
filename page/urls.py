from django.urls import path

from . import views

app_name = 'page'
# URLConf
urlpatterns = [
    path('',views.image_admin,name='image_admin'),
    path('re/<slug>',views.image_admin_with_slug,name='image_admin_with_slug'),
    path('products/<sku>',views.get_product),
    path('equity/<sku>',views.stock_amount),
    path('test/',views.test),
    path('export/',views.export_stock),
]
