from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('challenges/', include('challenges.urls', namespace='challenges')),
    path('solutions/', include('solutions.urls', namespace='solutions')),
    path('collaborations/', include('collaborations.urls', namespace='collaborations')),
    path('partnerships/', include('partnerships.urls', namespace='partnerships')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
