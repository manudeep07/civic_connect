from django.urls import path
from . import views

app_name = 'partnerships'

urlpatterns = [
    path('', views.partnership_list_view, name='list'),
    path('directory/', views.partner_directory_view, name='directory'),
    path('request/', views.partnership_request_create_view, name='request_create'),
    path('<int:pk>/respond/', views.partnership_respond_view, name='respond'),
]

