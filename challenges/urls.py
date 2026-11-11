from django.urls import path
from . import views

app_name = 'challenges'

urlpatterns = [
    path('', views.challenge_list_view, name='list'),
    path('new/', views.challenge_create_view, name='create'),
    path('<int:pk>/', views.challenge_detail_view, name='detail'),
    path('<int:pk>/edit/', views.challenge_edit_view, name='edit'),
    path('<int:pk>/delete/', views.challenge_delete_view, name='delete'),
    path('<int:pk>/vote/', views.vote_toggle_view, name='vote_toggle'),
    path('<int:pk>/comment/', views.comment_add_view, name='comment_add'),
    path('comment/<int:pk>/delete/', views.comment_delete_view, name='comment_delete'),
]

