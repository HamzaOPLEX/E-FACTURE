from datetime import datetime, timedelta

from dashboard.APPfunctions.APPfunctions import Fix_Date,generate_table_of_clients
from dashboard.Handlers.AUTH_Handler import RequireLogin, RequirePermission
from dashboard.Handlers.ERROR_Handlers import *
from dashboard.models import APP_Clients, APP_History, APP_User
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render


@RequirePermission
def ManageClients(requests):
    # Get Loged User Id from Session_id
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects, id=userid)
    # Context
    context = {'pagetitle': 'Gérer Vos Clients',
               'User': User, 'selecteditem': 'settings'}
    # path to Template
    templatepath = 'Settings/Manage-Clients.html'
    if requests.method == "GET":
        # Generate Table Of Clients and pass the Table in the context
        allclients = APP_Clients.objects.all()
        tablebody = generate_table_of_clients(allclients=allclients)
        context['tablebody'] = tablebody
        return render(requests, templatepath, context)
    elif requests.method == "POST":
        ClientName = str(requests.POST['ClientName']).strip().lower()
        ICE = str(requests.POST['ICE']).strip().upper()
        City = str(requests.POST['City']).strip().title()
        if ClientName and ICE and City:
            try:
                APP_Clients.objects.get(
                    Client_Name=ClientName,
                    ICE=ICE
                )
                messages.info(
                    requests, f'Le client {ClientName}:{ICE} existe déjà !')
                return redirect('/settings/manage-clients')
            except APP_Clients.DoesNotExist:
                APP_Clients.objects.create(
                    Client_Name=ClientName,
                    ICE=ICE,
                    City=City
                )
                actiondetail = f'{User.username} creé un client avec le nome {ClientName}  en {Fix_Date(str(datetime.today()))}'
                APP_History.objects.create(
                    CreatedBy=User,
                    action='creé un client',
                    action_detail=actiondetail,
                    DateTime=str(datetime.today())
                )
                messages.info(
                    requests, f'Le client {ClientName}:{ICE} a été créé avec succès')
                return redirect('/settings/manage-clients')
        else:
            messages.info(
                requests, f'veuillez remplir toutes les informations')
            return redirect('/settings/manage-clients')


@RequirePermission
def DeleteClient(requests, id):
    if requests.method == 'POST':
        userid = requests.session['session_id']
        User = get_object_or_404(APP_User, id=userid)
        pwd = requests.POST['password']
        client2delete = get_object_or_404(APP_Clients, id=id)
        ClientName = client2delete.Client_Name
        if check_password(pwd, User.password):
            messages.error(
                requests, f"le Client {client2delete.Client_Name} a été supprimé avec succès")
            client2delete.delete()
            actiondetail = f'{User.username} supprimer un client avec le nome {ClientName}  en {Fix_Date(str(datetime.today()))}'
            APP_History.objects.create(
                CreatedBy=User,
                action='supprimer un client',
                action_detail=actiondetail,
                DateTime=str(datetime.today())
            )
            return redirect('/settings/manage-clients')
        else:
            messages.error(requests, "Ooops ! Mot de passe incorrect")
            return redirect('/settings/manage-clients')
    else:
        return HTTP_404(requests)


@RequirePermission
def EditClient(requests, id):
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects, id=userid)
    client = get_object_or_404(APP_Clients, id=id)
    oldClientName = client.Client_Name
    oldICE = client.ICE
    oldCity = client.City
    if requests.method == 'POST':
        client_name = requests.POST['ClientName']
        ICE = requests.POST['ICE']
        City = requests.POST['City']
        if client_name and ICE and City:
            factures_of_that_client = APP_Created_Facture.objects.filter(
                Client_Name=client.Client_Name,
                ICE=client.ICE,
                Place=client.City
            )
            for client_info in factures_of_that_client:
                client_info.Client_Name = client_name
                client_info.ICE = ICE
                client_info.Place = City
                client_info.save()
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
        client = get_object_or_404(APP_Clients, id=id)
        client_info = {
            'ClientName': client.Client_Name,
            'ICE': client.ICE,
            'City': client.City
        }
        return JsonResponse(client_info)
