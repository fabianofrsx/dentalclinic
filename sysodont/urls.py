from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls', namespace='core')),  # raiz direciona para core
    path('agendamento/', include('agendamento.urls', namespace='agendamento')),
    path('paciente/', include('paciente.urls', namespace= 'paciente')),
    path('financeiro/', include('financeiro.urls', namespace= 'financeiro')),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
]
