from django.urls import path

from . import views

# URLConf
app_name = 'keyorder'
urlpatterns = [
    path('',views.main,name="main"),
    path('editorder/<int:slug>/',views.editorder,name="editorder"),
    path('summary/',views.summary,name="summary"),
    path('ExportOrder/',views.ExportOrder,name="ExportOrder"),
    path('Dashboard/',views.Dashboard,name="Dashboard"),
    path('Delete/Cart/<int:slug>/',views.DeleteCartItem,name="delete-cart-item"),
    path('DeleteProduct/',views.DeleteProduct,name="DeleteProduct"),
    path('Product/Details/<int:slug>/',views.productDetail,name="product-detail"),
    path('editproduct/',views.editproduct,name="editproduct"),
    path('summary/<str:slug>/',views.summary,name="summary-search"),
    path('check-idorder-exist/',views.checkIdorderExist,name="check-idorder-exist"),
    path('trackingno/',views.trackingno,name="trackingno"),
    path('add-trackingno/',views.addtrackingno,name="add-trackingno"),
    path('cartdetail/',views.cartdetail,name='cartdetail'),
    path('orderdetail/<int:slug>/',views.orderdetail,name='order-detail'),
    path('addproduct/',views.addproductPage),
    path('addproducts/',views.addproduct),
    path('print/',views.print_order,name="print-order"),
    path('addorder/<int:slug>/',views.addorder,name='addorder'),
    path('updateorder/<int:slug>/',views.updateorder,name='updateorder'),
    path('add-to-cart/<slug>/',views.add_to_cart,name="add-to-cart"),
    path('add-to-editorder/<idproduct>/<id>/',views.add_to_editorder,name="add-to-editorder"),
]
