from django.contrib import admin
from dashboard.models import *
# Register your models here.




Models = (APP_History, APP_User,APP_Warning,APP_Facture_items,APP_Created_Facture,APP_Clients,APP_Settings)

admin.site.register(Models)