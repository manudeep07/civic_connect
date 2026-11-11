from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_index_view, name='index'),
    path('admin/approve/<int:pk>/', views.admin_approve_challenge, name='admin_approve'),
    path('admin/reject/<int:pk>/', views.admin_reject_challenge, name='admin_reject'),
]

