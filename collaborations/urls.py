from django.urls import path
from . import views

app_name = 'collaborations'

urlpatterns = [
    path('', views.project_list_view, name='list'),
    path('solution/<int:solution_id>/create/', views.project_create_from_solution_view, name='create_from_solution'),
    path('challenge/<int:challenge_id>/create/', views.project_create_from_challenge_view, name='create_from_challenge'),
    path('<int:pk>/', views.project_detail_view, name='detail'),
    path('<int:pk>/edit/', views.project_edit_view, name='edit'),
    path('<int:pk>/members/add/', views.project_member_add_view, name='member_add'),
    path('<int:pk>/members/<int:membership_id>/remove/', views.project_member_remove_view, name='member_remove'),
    path('<int:pk>/join/', views.project_quick_join_view, name='join'),
]

