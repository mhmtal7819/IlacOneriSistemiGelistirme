from django.urls import path
from django.contrib.auth.views import LogoutView


from.import views

urlpatterns = [
   path('',views.login,name='login'), #url tanımlama kısmı 
   path('yoneticiGiris/',views.yoneticiGiris,name='yoneticiGiris'), #url tanımlama kısmı
   path('sifremiUnuttum/',views.sifremiUnuttum,name='sifremiUnuttum'), #url tanımlama kısmı
   path('home/',views.home,name='home'), #url tanımlama kısmı
   path('bilgilerim/',views.bilgilerim,name='bilgilerim'), #url tanımlama kısmı
   path('ilaclarım/',views.ilaclarım,name='ilaclarım'), #url tanımlama kısmı
   path('contact/',views.contact,name='contact'), #url tanımlama kısmı
   path('register/',views.register,name='register'),
   path('bilgiGuncelle/',views.bilgiGuncelle,name='bilgiGuncelle'),
   path('index/',views.index,name='index'),
   path('signout/', views.signout, name='signout'),
   path('returnIndex/', views.returnIndex, name='returnIndex'),
   path('medReq/', views.medReq, name='medReq'),
   path('data/', views.data, name='data'),
   
   
]