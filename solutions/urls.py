from django.urls import path
from . import views

app_name = 'solutions'

urlpatterns = [
    path('challenge/<int:challenge_id>/new/', views.solution_create_view, name='create'),
    path('<int:pk>/', views.solution_detail_view, name='detail'),
    path('<int:pk>/edit/', views.solution_edit_view, name='edit'),
    path('<int:pk>/delete/', views.solution_delete_view, name='delete'),
    path('<int:pk>/accept/', views.solution_accept_toggle_view, name='accept_toggle'),
]

