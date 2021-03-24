from pprint import pprint
from dashboard.models import APP_Settings
from django.shortcuts import HttpResponse,redirect


class CheckCompanySettingMiddelWare:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self,request):
        ALLOWED_URLS = ['/settings/', '/settings/global-settings',
                        '/login/', '/logout/', '/login', '/logout','/admin','/admin/']
        if request.path in ALLOWED_URLS:
            response = self.get_response(request)
        if request.path not in ALLOWED_URLS:
            company_settings = APP_Settings.objects.all().first()
            if company_settings:
                response = self.get_response(request)
            else : 
                response = redirect("/settings/global-settings")
        return response
