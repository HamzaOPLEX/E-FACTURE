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
from django.db.models import Sum

@RequireLogin
def FilterPageHandler_GET(requests):
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User, id=userid)
    context = { 'pagetitle': 'Situation Des Clients', 'User': User, 'selecteditem': 'facture' }
    if requests.method == 'GET':
        setting = APP_Settings.objects.all().first()
        context['selectbody'] = GetClientsListWith_ID()
        context['Years'] = list(set([year.Date.strftime('%Y') for year in APP_Created_Facture.objects.all()]))
        context['Facture_Numbers'] = list([n.number for n in APP_Created_Facture.objects.all()])
        template_path = str(setting.APP_lang)+'/SituationClient/situationclient_page.html'
        return render(requests,template_path,context)
    else :
        return redirect('/situation-client/')

@RequireLogin
def FilterPageHandler_POST(requests):
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User, id=userid)
    if requests.method == 'POST':
        try :
            ClientID = requests.POST['ClientID']
            Year = requests.POST['Year']
            month = requests.POST['month']
            jour = requests.POST['day']
            status = requests.POST['status']
            Fnumber = requests.POST['number']
            is_OK = False
            for i in (ClientID,Year,month,status) :
                if i != '-' and i != '':
                    is_OK = True
                else:
                    is_OK = False
                    break
            if is_OK:
                if ClientID != '*':
                    Client = get_object_or_404(APP_Clients,id=ClientID)
                    factures = APP_Created_Facture.objects.filter(Client=Client)
                if ClientID == '*' :
                    factures = APP_Created_Facture.objects.filter()
                if jour != '*'  and Year=='*' and month=='*':
                    factures = factures.filter(Date__day=jour)

                if jour != '*'  and Year!='*' and month=='*':
                    factures = factures.filter(Date__day=jour,Date__year=Year)

                if jour != '*'  and Year!='*' and month!='*':
                    factures = factures.filter(Date__day=jour,Date__year=Year,Date__month=month)

                if jour == '*'  and Year=='*' and month!='*':
                    factures = Afactures.filter(Date__month=month)

                if jour == '*'  and Year!='*' and month=='*':
                    factures = factures.filter(Date__year=Year)

                if status != "*":
                    factures = factures.filter(isPaid=status)
    
                if Fnumber != "*" :
                    factures = factures.filter(number=Fnumber)

                paid = []
                non_paid = []
                # Get Client Paid & Non-Paid Factres
                month = 1
                for i in range(12):
                    all_paid_factures = factures.filter(isPaid='Oui',Date__month=month)
                    all_none_paid_factures = factures.filter(isPaid='Non',Date__month=month)
                    paid.append(len(all_paid_factures))
                    non_paid.append(len(all_none_paid_factures))
                    month = month + 1
                facture_table_data = generate_table_of_created_factures(showaction='Detail-Edit', factures=factures)

                TotalAvance = factures.aggregate(Sum('Avance'))['Avance__sum']
                TotalHT = factures.aggregate(Sum('HT'))['HT__sum']
                TotalTva = factures.aggregate(Sum('TVA'))['TVA__sum']
                TotalTTC = factures.aggregate(Sum('TTC'))['TTC__sum']
                TotalData = {
                                "TotalAvance":TotalAvance,
                                "TotalHT":TotalHT,
                                "TotalTva":TotalTva,
                                "TotalTTC":TotalTTC
                            }
                MSG = {'MSG': 'Search was done', 'PAID': paid,'NON_PAID': non_paid, 'FacturesData': facture_table_data,'TotalData':TotalData}
                return JsonResponse(MSG,status=200)

            if not is_OK: 
                ERR_MSG = {'ERR_MSG':'all fields are require'}
                return JsonResponse(ERR_MSG,status=500)
        except Exception as ERR_MSG:               
            ERR_MSG = {'ERR_MSG': str(ERR_MSG)}
            return JsonResponse(ERR_MSG, status=500)
    else:
        return redirect('/situation-client/')

