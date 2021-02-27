from django.contrib import admin
from django.urls import path, include

from dashboard.views import HTTP_403,HTTP_404,HTTP_500

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
]

handler404 = 'dashboard.views.HTTP_404'
handler500 = 'dashboard.views.HTTP_500'
handler403 = 'dashboard.views.HTTP_403'
