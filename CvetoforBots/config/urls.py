from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('docs/', include('CvetoforBots.apps.core.urls')),
    path('', include('CvetoforBots.apps.transactions.urls')),
]
