from pprint import pprint
from dashboard.models import APP_Settings
from django.shortcuts import HttpResponse,redirect
import re

class CheckCompanySettingMiddelWare:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self,request):
        ALLOWED_URLS = [
                            '/settings',
                            '/login', 
                            '/logout',
                            '/admin'
                        ]
        for path in ALLOWED_URLS :
            # for each allowed url create a regex to match evry think that come after it
            path = path + '.*'
            regx = re.compile(path)
            try : 
                regx = regx.search(request.path).group(0)
                if regx:
                    bypass_check = True
                    break
            except Exception:
                bypass_check = False


        if bypass_check == True:
            response = self.get_response(request)
        if bypass_check == False:
            try :
                company_settings = APP_Settings.objects.all().first()
            except ProgrammingError:
                # if table does not exist just set var as false
                company_settings = False
            if company_settings:
                response = self.get_response(request)
            else : 
                response = redirect("/settings/global-settings")
        return response
