from django.urls import path
from django.contrib.auth.views import LogoutView

from . import views

urlpatterns = [
    path('', views.login, name='login'),  # URL tanımlama kısmı 
    path('yoneticiGiris/', views.yoneticiGiris, name='yoneticiGiris'),  # URL tanımlama kısmı
    path('sifremiUnuttum/', views.sifremiUnuttum, name='sifremiUnuttum'),  # URL tanımlama kısmı
    path('home/', views.home, name='home'),  # URL tanımlama kısmı
    path('bilgilerim/', views.bilgilerim, name='bilgilerim'),  # URL tanımlama kısmı
    path('ilaclarım/', views.ilaclarım, name='ilaclarım'),  # URL tanımlama kısmı
    path('register/', views.register, name='register'),
    path('bilgiGuncelle/', views.bilgiGuncelle, name='bilgiGuncelle'),
    path('index/', views.index, name='index'),
    path('signout/', views.signout, name='signout'),
    path('returnIndex/', views.returnIndex, name='returnIndex'),
    path('medReq/', views.medReq, name='medReq'),
    path('data/', views.data, name='data'),
     path('delete_medication/<int:user_medication_id>/', views.delete_medication, name='delete_medication'),  # Updated URL pattern
]
