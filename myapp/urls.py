from django.urls import path
from . import views
from .views import CustomLoginView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.index, name='index'),  # Ana sayfa için index view
    path('filtersbycomment/', views.filtersbycomment, name='filtersbycomment'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', views.custom_logout, name='logout'),  # Logout URL'si
    path('user_status/', views.user_status, name='user_status'),
    path('finance/corporate/', views.finance_corporate, name='finance_corporate'),
    path('finance/selective/', views.finance_selective, name='finance_selective'),
    path('finance/primary/', views.finance_primary, name='finance_primary'),
]