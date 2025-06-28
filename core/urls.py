from django.urls import path
from . import views
from .views import login_view, logout_view, dashboard

app_name = 'core'  # <-- define o namespace aqui

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('', dashboard, name='dashboard'),
    path('dashboard/', dashboard),
]