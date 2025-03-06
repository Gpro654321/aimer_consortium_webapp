from django.urls import path

from django.shortcuts import redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView

from .views import admin_dashboard,workshop_dashboard, workshop_statewise_chart, export_workshop_csv


urlpatterns = [
    path('', admin_dashboard, name='admin_dashboard'),
    #path('', LoginView.as_view(next_page='/admin_dashboard/'), name='login'),  # Default Django login
    path('workshop/<int:workshop_id>/', workshop_dashboard, name='workshop_dashboard'),
    path('workshop/<int:workshop_id>/map/', workshop_statewise_chart, name='workshop_statewise_chart'),
    path('workshop/<int:workshop_id>/export/', export_workshop_csv, name='export_workshop_csv'),

    
    path('logout/', LogoutView.as_view(next_page='/admin/login/'), name='logout'),
]





