from datetime import datetime, timedelta

from dashboard.APPfunctions.APPfunctions import Fix_Date,generate_table_of_clients
from dashboard.Handlers.AUTH_Handler import RequireLogin, RequirePermission
from dashboard.Handlers.ERROR_Handlers import *
from dashboard.models import *
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.core.exceptions import *
from django.contrib.admin.utils import NestedObjects

@RequirePermission
def ManageClients(requests):
    # Get Loged User Id from Session_id
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User, id=userid)
    # Context
    context = {'pagetitle': 'Gérer Vos Clients',
               'User': User, 'selecteditem': 'settings'}
    # path to Templatesta
    settings = APP_Settings.objects.all().first()
    templatepath = str(settings.APP_lang)+'/Settings/Manage-Clients.html'
    if requests.method == "GET":
        # Generate Table Of Clients and pass the Table in the context
        allclients = APP_Clients.objects.all()
        tablebody = generate_table_of_clients(allclients=allclients)
        context['tablebody'] = tablebody
        context['setting'] = settings
        return render(requests, templatepath, context)
    elif requests.method == "POST":
        ClientName = str(requests.POST['ClientName']).strip().lower()
        ICE = str(requests.POST['ICE']).strip().upper()
        City = str(requests.POST['City']).strip().title()
        if ClientName and ICE and City:
            try:
                APP_Clients.objects.get(
                    Client_Name=ClientName,
                    ICE=ICE,
                )
                ERR_MSG = f'Le client {ClientName}:{ICE} existe déjà !'
                return JsonResponse({"ERR_MSG": ERR_MSG}, status=400)
            except APP_Clients.DoesNotExist:
                client = APP_Clients.objects.create(
                    Client_Name=ClientName,
                    ICE=ICE,
                    City = City
                )
                actiondetail = f'{User.username} creé un client avec le nome {ClientName}  en {Fix_Date(str(datetime.today()))}'
                APP_History.objects.create(
                    CreatedBy=User,
                    action='creé un client',
                    action_detail=actiondetail,
                    DateTime=str(datetime.today())
                )
                MSG = f'Le client {ClientName}:{ICE} a été créé avec succès'
                Client_DATA = {
                    'Client_Name':client.Client_Name,
                    'City':client.City,
                    'ICE':client.City,
                }
                response_data = {"MSG": MSG,'CLIENT_ID':client.id,'ClientData':Client_DATA}
                return JsonResponse(response_data, status=200)
        else:
            ERR_MSG = f'veuillez remplir toutes les informations'
            return JsonResponse({"ERR_MSG": ERR_MSG}, status=400)


@RequirePermission
def DeleteClient(requests, id):
    if requests.method == 'POST':
        userid = requests.session['session_id']
        User = get_object_or_404(APP_User, id=userid)
        pwd = requests.POST['password']
        client2delete = get_object_or_404(APP_Clients, id=id)
        ClientName = client2delete.Client_Name
        context = {'pagetitle': 'Oooops !','User': User, 'selecteditem': 'settings'}
        settings = APP_Settings.objects.all().first()
        if check_password(pwd, User.password):
            try :
                client2delete.delete()
                messages.error(requests, f"le Client {client2delete.Client_Name} a été supprimé avec succès")
                actiondetail = f'{User.username} supprimer un client avec le nome {ClientName}  en {Fix_Date(str(datetime.today()))}'
                APP_History.objects.create(
                    CreatedBy=User,
                    action='supprimer un client',
                    action_detail=actiondetail,
                    DateTime=str(datetime.today())
                )
                return redirect('/settings/manage-clients')
            except Exception as Err:
                collector = NestedObjects(using="default")
                collector.collect([client2delete])
                ref = list(collector.data)[1::]
                ALL_REFRECES = []
                for obj in ref :
                    obj = obj.objects.filter(Client=client2delete)
                    for o in obj:
                        ALL_REFRECES.append(o)
                context['ref'] = ALL_REFRECES
                context['setting'] = settings
                return render(requests,str(settings.APP_lang)+'/ErrorPages/ClientDeletionError.html',context)
        else:
            messages.error(requests, "Ooops ! Mot de passe incorrect")
            return redirect('/settings/manage-clients')
    else:
        return redirect('/settings/manage-clients')


@RequirePermission
def EditClient(requests, id):
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User, id=userid)
    client = get_object_or_404(APP_Clients, id=id)
    oldClientName = client.Client_Name
    oldICE = client.ICE
    oldCity = client.City
    if requests.method == 'POST':
        client_name = requests.POST['ClientName']
        ICE = requests.POST['ICE']
        City = requests.POST['City']
        if client_name and ICE and City:
            client.Client_Name = client_name
            client.ICE = ICE
            client.City = City
            client.save()
            actiondetail = f"""{User.username} hamza éditer le client de 
                                {oldClientName}:{oldICE}:{oldCity} à 
                                {client.Client_Name}:{client.ICE}:{client.City}  
                                {Fix_Date(str(datetime.today()))}
                            """
            APP_History.objects.create(
                CreatedBy=User,
                action='éditer un client',
                action_detail=actiondetail,
                DateTime=str(datetime.today())
            )
            messages.info(requests, 'Le client a été mis à jour avec succès')
            return redirect('/settings/manage-clients')
        else:
            messages.info(requests, 'Veuillez remplir toutes les informations')
            return redirect('/settings/manage-clients')
    elif requests.method == 'GET':
        return redirect('/settings/manage-clients')
