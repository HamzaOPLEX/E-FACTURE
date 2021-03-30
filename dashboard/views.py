from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import HttpResponse, redirect, render, get_object_or_404
from dashboard.models import *
from .APPfunctions.APPfunctions import *
from .Handlers import Facture_Handler
from dashboard.Handlers.AUTH_Handler import RequireLogin, RequirePermission
from dashboard.Handlers.ERROR_Handlers import *
from django.db.models import Sum

@RequireLogin
def Dashboard(requests):
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects, id=userid)
    context = {'pagetitle': 'Tableau de bord',
               'User': User, 'selecteditem': 'dashboard'}
    if requests.method == "GET":
        ###### Dashboard Header Handler
        # Get lenght of some objects from database

        len_users = len(APP_User.objects.all())
        len_clients = len(APP_Clients.objects.all())
        len_products = len(APP_Products.objects.all())
        len_factures = len(APP_Created_Facture.objects.all())
        len_devis = len(APP_Created_Devis.objects.all())
        # Pass them to context
        context['Lenghts'] = {'len_users': len_users, 'len_clients': len_clients,
                              'len_products': len_products, 'len_factures': len_factures, 'len_devis': len_devis}
        ####################################

        ###### Dashboard Factures Table of this Month
        # Get current month number
        this_month = int(datetime.today().month)
        this_year = int(datetime.today().year)
        # Use "this_month" variable to filter all Created Facture that with in this month
        This_Month_Created_Factures = APP_Created_Facture.objects.filter(
            Date__month=this_month,
            Date__year=this_year
        )
        # Use "This_Month_Created_Factures" to generate a table of items
        tablebody = generate_table_of_created_factures(
            showaction='Detail-Edit',
            factures=This_Month_Created_Factures
        )
        # Pass Generated Table into context
        context['tablebody'] = tablebody
        ####################################

        ###### Dashboard Created products of this Month
        # Use "this_month" variable to filter all Created Products that with in this month
        This_Month_Created_Products = APP_Products.objects.filter(
            Date__month=this_month,
            Date__year=this_year
        )
        # Use "This_Month_Created_Products" to generate a table of items
        producttablebody = generate_table_of_products(
            showaction=False,
            Products=This_Month_Created_Products
        )
        # Pass Generated Table into context
        context['producttablebody'] = producttablebody
        ####################################

        ###### Dashboard Created Clients of this Month
        # Use "this_month" variable to filter all Created Clients that with in this month
        This_Month_Created_Clients = APP_Clients.objects.filter(
            Date__month=this_month,
            Date__year=this_year
        )
        # Use "This_Month_Created_Products" to generate a table of items
        clienttablebody = generate_table_of_clients(
            showaction=False,
            allclients=This_Month_Created_Clients
        )
        # Pass Generated Table into context
        context['clienttablebody'] = clienttablebody
        ####################################

        ################### Chart Handler ###################
        paid = []
        non_paid = []
        month = 1
        for i in range(12):
            all_paid_factures = len(APP_Created_Facture.objects.filter(isPaid='Oui', Date__year=this_year, Date__month=month))
            all_none_paid_factures = len(APP_Created_Facture.objects.filter(isPaid='Non', Date__year=this_year, Date__month=month))
            paid.append(all_paid_factures)
            non_paid.append(all_none_paid_factures)
            month = month + 1

        context['all_paid_factures'] = paid
        context['all_none_paid_factures'] = non_paid
        ################### End Chart Handler ###################

        ################### Chiffre D'affair Handler ###################
        TVA_taux = int(APP_Settings.objects.all().first().Company_TVATAUX)
        HT = APP_Facture_items.objects.filter(Date__year=this_year).aggregate(Sum('PT'))['PT__sum']
        if not HT:
            HT = 0
        TVA = HT / 100 * TVA_taux
        TTC = HT + TVA
        context['HT'] = HT
        context['TVA_taux'] = TVA_taux
        context['TTC'] = TTC
        ################### End Chiffre D'affair Handler ###################



        # if User.userpermission == 'Admin':
        #     now = datetime.now()
        #     this_time_yesterday = now - timedelta(hours=24)
        #     Last24HoureHistory = APP_History.objects.filter(
        #         DateTime__gte=this_time_yesterday, DateTime__lte=now)
        #     History_table_body = generate_table_of_history(
        #         Last24HoureHistory, simpletable=True)
        #     context['History_table_body'] = History_table_body


        settings = APP_Settings.objects.all().first()
        return render(requests, str(settings.APP_lang)+'/Dashboard/dashboard.html', context)

@RequirePermission
def Settings(requests):
    context = {'pagetitle': 'Page de Réglage'}
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects, id=userid)
    len_users = len(APP_User.objects.all())
    len_clients = len(APP_Clients.objects.all())
    len_products = len(APP_Products.objects.all())
    len_templates = 0  # len(APP_User.objects.all())
    context['Lenghts'] = {'len_users': len_users, 'len_clients': len_clients,
                          'len_products': len_products, 'len_templates': len_templates}
    context['User'] = User
    if requests.method == "GET":
        context['selecteditem'] = 'settings'
        settings = APP_Settings.objects.all().first()
        return render(requests, str(settings.APP_lang)+'/Settings/settings.html', context)


########################################################
# Events Handler
########################################################
@RequirePermission
def ShowAllHistory(requests):
    context = {'pagetitle': 'gérer les paramètres généraux de l\'application'}
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects, id=userid)
    context['selecteditem'] = 'dashboard'
    context['User'] = User
    allhistory = APP_History.objects.all()
    if requests.method == 'GET':
        tablebody = generate_table_of_history(allhistory)
        context['tablebody'] = tablebody
        return render(requests, 'Events/All-History.html', context)
########################################################


########################################################
# Globale Settings Handler
########################################################
@RequirePermission
def GlobaleSettings(requests):
    context = {'pagetitle': 'gérer les paramètres généraux de l\'application'}
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects, id=userid)
    context['selecteditem'] = 'settings'
    context['User'] = User

    settings = APP_Settings.objects.all().first()
    if requests.method == 'GET':
        context['setting'] = settings
        return render(requests, str(settings.APP_lang)+'/Settings/global-settings.html', context)
    elif requests.method == 'POST':
        ICE = str(requests.POST['ICE']).strip().upper()
        TVATAUX = requests.POST['TVATAUX']
        Place = requests.POST['place']
        LANG = requests.POST['LANG']
        COLOR = requests.POST['COLOR']
        if ICE and TVATAUX and Place and COLOR:
            if settings:
                settings.Company_ICE = ICE
                settings.Company_Place = Place
                settings.Company_TVATAUX = TVATAUX
                settings.APP_lang = LANG
                settings.Invoice_Color = COLOR
                settings.save()
                messages.info(
                    requests, 'Les paramètres ont été modifiés avec succès')
                return redirect('/settings/global-settings')
            elif not settings:
                APP_Settings.objects.create(
                    Company_ICE=ICE, Company_TVATAUX=TVATAUX, Company_Place=Place, APP_lang=LANG,Invoice_Color=COLOR)
                messages.info(
                    requests, 'Les paramètres ont été créés avec succès')
                return redirect('/settings/global-settings')
        else:
            messages.info(
                requests, 'veuillez vérifier que toutes les informations sont correctes')
            return redirect('/settings/global-settings')
########################################################
