from django.urls import path
from . import views
from .views import index
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('latest/<str:category>/<str:subcategory>/', views.latest_data, name='latest_data'),
    path('dashboard/<str:channel_name>/', views.channel_dashboard, name='channel_dashboard'),
    path('most_engaged/<str:category>/<str:subcategory>/<str:source>/', views.most_engaged_content, name='most_engaged_content'),
]

