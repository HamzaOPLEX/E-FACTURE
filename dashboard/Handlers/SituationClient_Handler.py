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
def FilterPageHandler_GET(requests):
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects, id=userid)
    context = { 'pagetitle': 'Situation Des Clients', 'User': User, 'selecteditem': 'facture' }
    if requests.method == 'GET':
        setting = APP_Settings.objects.all().first()
        context['selectbody'] = GetClientsListWith_ID()
        context['Years'] = list(set([year.Date.strftime('%Y') for year in APP_Created_Facture.objects.all()]))
        template_path = str(setting.APP_lang)+'/SituationClient/situationclient_page.html'
        return render(requests,template_path,context)
    else :
        return redirect('/situation-client/')

@RequireLogin
def FilterPageHandler_POST(requests):
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects, id=userid)
    if requests.method == 'POST':
        ClientID = requests.POST['ClientID']
        Year = requests.POST['Year']
        month = requests.POST['month']
        jour = requests.POST['day']
        status = requests.POST['status']
        is_OK = False
        for i in (ClientID,Year,month,status) :
            if i != '-' and i != '':
                is_OK = True
            else:
                is_OK = False
                break
        if is_OK:
            Client = get_object_or_404(APP_Clients,id=ClientID)

            filter_config = {}
            if jour == '*' and Year=='*' and month=='*':
                factures = APP_Created_Facture.objects.filter(Client=Client)
            if jour != '*'  and Year=='*' and month=='*':
                factures = APP_Created_Facture.objects.filter(Client=Client,Date__day=jour)
            if jour != '*'  and Year!='*' and month=='*':
                factures = APP_Created_Facture.objects.filter(Client=Client,Date__day=jour,Date__year=Year)
            if jour != '*'  and Year!='*' and month!='*':
                factures = APP_Created_Facture.objects.filter(Client=Client,Date__day=jour,Date__year=Year,Date__month=month)
            if jour == '*'  and Year=='*' and month!='*':
                factures = APP_Created_Facture.objects.filter(Client=Client,Date__month=month)
            if jour == '*'  and Year!='*' and month=='*':
                factures = APP_Created_Facture.objects.filter(Client=Client,Date__year=Year)

            if status != "*":
                factures = factures.filter(isPaid=status)
 


            paid = []
            non_paid = []
            # Get Client Paid & Non-Paid Factres
            month = 1
            for i in range(12):
                all_paid_factures = APP_Created_Facture.objects.filter(isPaid='Oui',Client=Client ,Date__month=month)
                all_none_paid_factures = APP_Created_Facture.objects.filter(isPaid='Non', Client=Client ,Date__month=month)
                paid.append(len(all_paid_factures))
                non_paid.append(len(all_none_paid_factures))
                month = month + 1

            facture_table_data = generate_table_of_created_factures(showaction='Detail-Edit', factures=factures)

            MSG = {'MSG': 'Search was done', 'PAID': paid,
                   'NON_PAID': non_paid, 'FacturesData': facture_table_data}
            return JsonResponse(MSG,status=200)

        if not is_OK: 
            ERR_MSG = {'ERR_MSG':'all fields are require'}
            return JsonResponse(ERR_MSG,status=400)

    else:
        return redirect('/situation-client/')

