from django.contrib import admin
from efacture.models import *
# Register your models here.




Models = (
            APP_History, 
            APP_User,
            APP_Warning,
            APP_Facture_items,
            APP_Created_Facture,
            APP_Clients,
            APP_Settings,
            APP_Created_BL,
            APP_Created_Devis,
            APP_Devis_items,
        )

admin.site.register(Models)