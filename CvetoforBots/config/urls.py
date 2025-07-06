from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('bots/admin/', admin.site.urls),
    path('bots/docs/', include('CvetoforBots.apps.core.urls')),
    path('bots/', include('CvetoforBots.apps.transactions.urls')),
]
