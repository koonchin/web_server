from django.urls import path

from . import views

# URLConf
urlpatterns = [
    path('',views.image_admin),
    path('test/',views.main),
    path('blog/',views.movies),
]