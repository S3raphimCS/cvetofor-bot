from django.urls import path

from CvetoforBots.apps.core import views


urlpatterns = [
    path('<slug:slug>/', views.view_pdf, name='view_pdf'),
]
