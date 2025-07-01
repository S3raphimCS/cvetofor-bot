from django.urls import path

from CvetoforBots.apps.transactions.views import YookassaWebHookView


urlpatterns = [
    path('notifications/', YookassaWebHookView.as_view()),
]
