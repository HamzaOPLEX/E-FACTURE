import json
import os
import shutil
from datetime import datetime, timedelta
from urllib.parse import unquote

from dashboard.APPfunctions.APPfunctions import *
from dashboard.Handlers.AUTH_Handler import RequireLogin, RequirePermission
from dashboard.Handlers.ERROR_Handlers import *
from dashboard.models import *
from dashboard.pdf_templates.Invoice.Invoice import DrawNotechPdf
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.http import FileResponse, JsonResponse
from django.shortcuts import HttpResponse, get_object_or_404, redirect, render

@RequireLogin
def FilterPageHandler(requests):
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects, id=userid)
    context = { 'pagetitle': 'Situation Des Clients', 'User': User, 'selecteditem': 'facture' }
    if requests.method == 'GET':
        setting = APP_Settings.objects.all().first()
        context['selectbody'] = [clientname.Client_Name for clientname in list(APP_Clients.objects.all())]
        context['Years'] = list(set([year.Date.strftime('%Y') for year in APP_Created_Facture.objects.all()]))
        template_path = str(setting.APP_lang)+'/SituationClient/situationclient_page.html'
        return render(requests,template_path,context)
    elif requests.method == 'POST' :
        pass
