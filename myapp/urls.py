from django.urls import path
from . import views
from .views import index,tiktok_view
from django.contrib.auth import views as auth_views



urlpatterns = [

    path('login/', views.login_view, name='login'),  # Giriş için URL
    path('logout/', views.logout_view, name='logout'),  # Logout işlemi için URL

    # Finans Kategorisi
    path('finance/corporate/', views.finance_corporate, name='finance_corporate'),
    path('finance/selective/', views.finance_selective, name='finance_selective'),
    path('finance/primary/', views.finance_primary, name='finance_primary'),

    # Mey Kategorisi
    path('mey/selective/', views.mey_selective, name='mey_selective'),
    path('mey/primary/', views.mey_primary, name='mey_primary'),

    # Snacks-tr Kategorisi
    path('snacks/corporate/', views.snacks_corporate, name='snacks_corporate'),
    path('snacks/selective/', views.snacks_selective, name='snacks_selective'),
    path('snacks/primary/', views.snacks_primary, name='snacks_primary'),

    # Mey-International Kategorisi
    path('mey_int/primary/', views.mey_int_primary, name='mey_int_primary'),  # Düzeltilmiş

    path('', index, name='index'),  # Ana sayfa olarak index view'ı
    path('tiktok/', views.tiktok_view, name='tiktok_page'),

]

