import os
import shutil
from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import HttpResponse, redirect, render, get_object_or_404
from django.http import FileResponse, JsonResponse
from dashboard.models import *
from .APPfunctions.APPfunctions import *
from .pdf_templates.Invoice.Invoice import DrawNotechPdf
from .Handlers import Facture_Handler
from urllib.parse import unquote
import json
from dashboard.Handlers.AUTH_Handler import RequireLogin, RequirePermission

# Authentication : Login
def Login(requests):
    context = {}
    if requests.method == "GET":
        if requests.session.session_key and requests.session.exists(requests.session.session_key):
            return redirect('/')
        else:
            return render(requests, 'Authentication/login.html', context)
    elif requests.method == "POST":
        username = requests.POST['username']
        password = requests.POST['password']
        try:
            user = APP_User.objects.get(username=username)
            if user.account_status == 'Active':
                usrpwd = user.password
                if check_password(password, usrpwd):
                    requests.session['session_id'] = user.id
                    value = requests.COOKIES.get('REDIRECT_AFTER_LOGIN')
                    if value:
                        redirect_to = value
                    elif value is None:
                        redirect_to = '/dashboard'  # default
                    return redirect(redirect_to)
                else: 
                    raise APP_User.DoesNotExist('APP_User matching query does not exist.')
            else : 
                return Your_Account_Has_Been_Suspended(requests)
        except APP_User.DoesNotExist or Exception:
            messages.error(requests, f"Mot de passe ou nom d'utilisateur incorrect")
            return render(requests, 'Authentication/login.html', context)

# Authentication : Logout
@RequireLogin
def Logout(requests):
    if requests.session.get('session_id'):
        requests.session.flush()
    return redirect('/login/')

@RequireLogin
def Dashboard(requests):
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects,id=userid)
    context = {'pagetitle': 'Tableau de bord', 'User': User,'selecteditem':'dashboard'}
    if requests.method == "GET":
        ###### Dashboard Header Handler
        # Get lenght of some objects from database
        len_users = len(APP_User.objects.all())
        len_clients =  len(APP_Clients.objects.all())
        len_products = len(APP_Products.objects.all())
        len_factures = len(APP_Created_Facture.objects.all())
        # Pass them to context
        context['Lenghts'] = {'len_users':len_users,'len_clients':len_clients,'len_products':len_products,'len_factures':len_factures}
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

        if User.userpermission == 'Admin' :
            now = datetime.now()
            this_time_yesterday = now - timedelta(hours=24)
            Last24HoureHistory = APP_History.objects.filter(DateTime__gte=this_time_yesterday, DateTime__lte=now)
            History_table_body = generate_table_of_history(Last24HoureHistory, simpletable=True)
            context['History_table_body'] = History_table_body


        return render(requests, 'Dashboard/dashboard.html', context)

@RequireLogin
def Profile(requests):
    context = {'pagetitle': 'User Profile'}
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects,id=userid)
    if requests.method == "GET":
        factures = list(APP_Created_Facture.objects.filter(CreatedBy=User))
        tablebody = []
        for facture in factures:
            facture_number = facture.facture_number
            client = facture.Client_Name
            date = facture.Date
            D = {}
            D['N'] = facture_number
            D['client'] = client
            D['date'] = date
            factureid = facture.id
            D['Action'] = f'''<a class="btn btn-info btn-sm" href="/list-all-facturs/edit/{factureid}" title="Edit" data-toggle="tooltip"><i class="fas fa-pencil-alt"></i>\n</a> 
                            <a class="btn btn-danger btn-sm" href="#" onclick='DeleteFunctionPopUp("/profile/delete/{factureid}")' title="Delete" data-toggle="tooltip"><i class="fas fa-trash"></i></a>\n
                            <a class="btn btn-primary btn-sm" href="/list-all-facturs/detail/open/{factureid}" title="detail" data-toggle="tooltip"><i class="fas fa-folder"></i></a>\n'''
            tablebody.append(D)
        context['tablebody'] = tablebody
        context['User'] = User
        return render(requests, 'Profile/profile.html', context)

@RequireLogin
def Delete_My_Acount(requests):
    context = {'pagetitle': 'Delete My Account'}
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects,id=userid)
    context['User'] = User
    if requests.method == "POST":
        password = requests.POST['password']
        if password and check_password(password,User.password):
            shutil.rmtree(User.ProfileFolderPath, ignore_errors=True)
            User.delete()
            requests.session.flush()
            messages.error(requests, "votre compte a été supprimé avec succès")
            return redirect('/login/')
        else :
            messages.error(requests, "Oops, Mot de passe incorrect !")
            return redirect('/profile/')
    else :
        return HTTP_404(requests, context)

@RequireLogin
def Change_Password(requests):
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects,id=userid)
    if requests.method == "POST":
        oldpwd = requests.POST['oldpwd']
        newpwd = requests.POST['newpwd']
        retypednewpwd = requests.POST['retypednewpwd']
        if check_password(oldpwd,User.password) and newpwd == retypednewpwd:
            User.password = make_password(newpwd)
            User.save()
            actionmsg = f'{User.username} changer son mot de passe'
            APP_History.objects.create(CreatedBy=User, action='Changer mot de pass', action_detail=actionmsg)
            messages.error(requests, 'mot de passe changé avec succès :)')
            return redirect('/profile/')
        else:
            messages.error(requests, 'Oooops ! Ancien mot de passe incorrect :( ')
            return redirect('/profile/')
    else : 
        return HTTP_404(requests, context)

@RequirePermission
def Settings(requests):
    context = {'pagetitle': 'Page de Réglage'}
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects,id=userid)
    len_users = len(APP_User.objects.all())
    len_clients =  len(APP_Clients.objects.all())
    len_products = len(APP_Products.objects.all())
    len_templates = 0 #len(APP_User.objects.all())
    context['Lenghts'] = {'len_users':len_users,'len_clients':len_clients,'len_products':len_products,'len_templates':len_templates}
    context['User'] = User
    if requests.method == "GET":
        context['selecteditem'] = 'settings'
        return render(requests, 'Settings/settings.html', context)

########################################################
# Manage Products
########################################################

@RequirePermission
def ManageProducts(requests):
    # Get Loged User Id from Session_id
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects, id=userid)
    # Context
    context = {'pagetitle': 'Gérer Les Produits','User':User,'selecteditem':'settings'}
    # path to Template 
    templatepath = 'Settings/Manage-Products.html'
    if requests.method == "GET":
        # Generate Table Of Products and pass the Table in the context
        Products = list(APP_Products.objects.all())
        context['tablebody'] = generate_table_of_products(Products=Products)
        return render(requests, templatepath, context)
    elif requests.method == "POST":
        # Get ProductName and remove Any Space
        ProductName = str(requests.POST['ProductName']).strip().lower()
        PU = requests.POST['PU']
        if ProductName and PU:
            # Check if Exist if not Create new one 
            try:
                APP_Products.objects.get(DESIGNATION=ProductName)
                messages.info(requests, f'Le Produit "{ProductName}" existe déjà !')
                return redirect('/settings/manage-products')
            except APP_Products.DoesNotExist:
                APP_Products.objects.create(DESIGNATION=ProductName, PU=PU)
                actiondetail = f'{User.username} creé un nouveau produit avec le nome {ProductName}  en {Fix_Date(str(datetime.today()))}'
                APP_History.objects.create(
                                            CreatedBy=User, 
                                            action='creé un nouveau produit',
                                            action_detail=actiondetail, 
                                            DateTime=str(datetime.today())
                                        )
                messages.info(requests, f'Le produit {ProductName} a été créé avec succès')
                return redirect('/settings/manage-products')
        else:
            messages.info(requests, f'veuillez remplir toutes les informations')
            return redirect('/settings/manage-products')

@RequirePermission
def DeleteProduct(requests, id):
    if requests.method == 'POST':
        userid = requests.session['session_id']
        User = get_object_or_404(APP_User, id=userid)
        pwd = requests.POST['password']
        products2delete = get_object_or_404(APP_Products, id=id)
        ProductName = products2delete.DESIGNATION
        if check_password(pwd, User.password):
            messages.error(requests, f"le Client {products2delete.DESIGNATION} a été supprimé avec succès")
            products2delete.delete()
            actiondetail = f'{User.username} supprimer un produit avec le nome {ProductName}  en {Fix_Date(str(datetime.today()))}'
            APP_History.objects.create(
                                        CreatedBy=User, 
                                        action='supprimer un produit',
                                        action_detail=actiondetail, 
                                        DateTime=str(datetime.today())
                                    )
            return redirect('/settings/manage-products')
        else:
            messages.error(requests, "Ooops ! Mot de passe incorrect")
            return redirect('/settings/manage-products')
    else:
        return HTTP_404(requests)

@RequirePermission
def EditProduct(requests, id):
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User, id=userid)
    if requests.method == 'POST':
        ProductName = requests.POST['ProductName']
        PU = requests.POST['PU']
        if ProductName and PU:
            product = get_object_or_404(APP_Products, id=id)
            product.DESIGNATION = ProductName
            product.PU = PU
            product.save()
            actiondetail = f'{User.username} edité un produit avec le nome {ProductName}  en {Fix_Date(str(datetime.today()))}'
            APP_History.objects.create(
                                        CreatedBy=User, 
                                        action='edité un produit',
                                        action_detail=actiondetail, 
                                        DateTime=str(datetime.today())
                                    )
            messages.info(requests, 'Le produit a été mis à jour avec succès')
            return redirect('/settings/manage-products')
        else:
            messages.info(requests, 'Veuillez remplir toutes les informations')
            return redirect('/settings/manage-products')
    elif requests.method == 'GET':
        product = get_object_or_404(APP_Products, id=id)
        product_info = {
            'ProductName': product.DESIGNATION,
            'PU': product.PU,
        }
        return JsonResponse(product_info)

########################################################

########################################################
# Manage Clients
########################################################

@RequirePermission
def ManageClients(requests):
    # Get Loged User Id from Session_id
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects, id=userid)
    # Context
    context = {'pagetitle': 'Gérer Vos Clients', 'User': User,'selecteditem':'settings'}
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
                messages.info(requests, f'Le client {ClientName}:{ICE} existe déjà !')
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
                messages.info(requests, f'Le client {ClientName}:{ICE} a été créé avec succès')
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
            messages.error(requests, f"le Client {client2delete.Client_Name} a été supprimé avec succès")
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
            for client_info in factures_of_that_client :
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

########################################################

########################################################
# Manage Users
########################################################

@RequirePermission
def ManageUsers(requests):
    context = {'pagetitle': 'Gérer Vos Utilisateurs'}
    templatepath = 'Settings/Manage-Users.html'
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects, id=userid)
    context['User'] = User
    context['selecteditem'] = 'settings'
    if requests.method == "GET":
        all_users = APP_User.objects.all()
        tablebody = []
        for user in all_users:
            id = user.id
            if id != userid:
                username = user.username
                status = user.account_status
                permission = user.userpermission
                D = {}
                D['id'] = id
                D['username'] = username
                D['permission'] = permission
                D['status'] = status
                D['Action'] = f"""<a class='btn btn-info  btn-sm' href='manage-users/edit/{id}' target='_blank' title='Edit' data-toggle='tooltip'>
                                                <i class='fas fa-pencil-alt'></i>\n</a>
                                  <a class='btn btn-danger btn-sm' href='#' title='Delete' onclick='EnterPwdToDeletePopup(\"/settings/deleteacount/{id}\");' data-toggle='tooltip'>
                                                <i class='fas fa-trash'></i></a>\n
                                  <a class='btn btn-warning btn-sm' target='_blank' href='manage-users/profile/{id}' title='detail' data-toggle='tooltip'>
                                                <i class='fas fa-folder'></i></a>\n"""
                tablebody.append(D)

        context['tablebody'] = tablebody
        return render(requests, templatepath, context)

@RequirePermission
def EditUser(requests, id):
    context = {'pagetitle': 'Edité un utilisateur'}
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects,id=userid)
    context['selecteditem'] = 'settings'
    context['User'] = User
    if requests.method == 'POST':
        username = str(requests.POST['username']).strip().lower()
        gender = requests.POST['gender']
        type = requests.POST['Type']
        status = requests.POST['Status']
        if username and gender and type and status:
            user = get_object_or_404(APP_User,id=id)
            user.gender = gender
            user.userpermission = type
            user.account_status = status
            user.save()
            actiondetail = f"{User.username} édit un utilisateur avec le nom {user.username} {Fix_Date(str(datetime.today()))}"
            APP_History.objects.create(
                CreatedBy=User,
                action=f'édit un utilisateur',
                action_detail=actiondetail,
                DateTime=str(datetime.today())
            )
            messages.info(requests, f"l'utilisateur {username} a été Edité avec succès")
            return redirect('/settings/manage-users')
        else:
            messages.error(requests, "veuillez saisir des correct informations")
            return redirect('/settings/manage-users')
    elif requests.method == 'GET' :
        edit_user = get_object_or_404(APP_User,id=id)
        context['edituser'] = edit_user
        return render(requests, 'Settings/Edit-User.html', context)

@RequirePermission
def DeleteUser(requests,id):
    if requests.method == 'POST':  # if HTTP method is POST
        userid = requests.session['session_id']
        User = get_object_or_404(APP_User,id=userid)
        pwd = requests.POST['password']
        user2delete = get_object_or_404(APP_User,id=id)
        if check_password(pwd,User.password):
            messages.error(requests, f"l'utilisateur {user2delete.username} a été supprimé avec succès")
            user2delete.delete()
            actiondetail = f"{User.username} supprimer un utilisateur avec le nom {user2delete.username} {Fix_Date(str(datetime.today()))}"
            APP_History.objects.create(
                CreatedBy=User,
                action=f'supprimer un utilisateur',
                action_detail=actiondetail,
                DateTime=str(datetime.today())
            )
            return redirect('/settings/manage-users')
        else :
            messages.error(requests, "Ooops ! Mot de passe incorrect")
            return redirect('/settings/manage-users')
    else:
        return HTTP_404(requests)

@RequirePermission
def ShowUserProfile(requests, id):
    context = {'pagetitle': 'Show User Profile'}
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects, id=userid)
    if requests.method == "GET":
        try:
            UserTarget = APP_User.objects.get(id=id)
            factures = list(
                APP_Created_Facture.objects.filter(CreatedBy=UserTarget))
            tablebody = []
            for facture in factures:
                facture_number = facture.facture_number
                client = facture.Client_Name
                date = facture.Date
                D = {}
                D['N'] = facture_number
                D['client'] = client
                D['date'] = date
                factureid = facture.id
                D['Action'] = f'<a class="btn btn-info btn-sm" href="/list-all-facturs/edit/{factureid}" title="Edit" data-toggle="tooltip"><i class="fas fa-pencil-alt"></i>\n</a> <a class="btn btn-danger btn-sm" href="/list-all-facturs/delete/{factureid}" title="Delete" data-toggle="tooltip"><i class="fas fa-trash"></i></a>\n<a class="btn btn-primary btn-sm" href="/list-all-facturs/detail/open/{factureid}" title="detail" data-toggle="tooltip"><i class="fas fa-folder"></i></a>\n'
                tablebody.append(D)
            context['tablebody'] = tablebody
            context['FactureFilesTable'] = FactureFilesTable
            context['UserTarget'] = UserTarget
            context['User'] = User
            return render(requests, 'Settings/showprofile.html', context)
        except APP_User.DoesNotExist:
            return HTTP_404(requests)
    else:
        return HTTP_404(requests)

@RequirePermission
def ChangeUserPassword(requests, id):
    context = {'pagetitle': 'Changer le mot de pass'}
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects, id=userid)
    context['selecteditem'] = 'settings'
    context['User'] = User
    if requests.method == 'POST':
        fpwd = requests.POST['fpwd']
        spwd = requests.POST['spwd']
        if fpwd and spwd and fpwd == spwd:
            fpwd = make_password(fpwd)
            try:
                user = APP_User.objects.get(id=id)
                user.password = fpwd
                user.save()
                messages.info(requests, f"Le mot de passe a été changé avec succès")
                actiondetail = f"{User.username} changer le mot de pass de l'utilisateur {user.username} {Fix_Date(str(datetime.today()))}"
                APP_History.objects.create(
                    CreatedBy=User,
                    action=f'changer Psswd de {user.username} ',
                    action_detail=actiondetail,
                    DateTime=str(datetime.today())
                )
                return redirect(f'/settings/manage-users/edit/{id}')
            except APP_User.DoesNotExist:
                return HTTP_404(requests, context)
        else:
            messages.error(
                requests, "veuillez saisir des correct informations")
            return render(requests, 'Settings/changepwduser.html', context)
    elif requests.method == 'GET':
        try:
            edit_user = APP_User.objects.get(id=id)
            context['edituser'] = edit_user
            return render(requests, 'Settings/changepwduser.html', context)
        except APP_User.DoesNotExist:
            return HTTP_404(requests, context)

@RequirePermission
def AddUser(requests):
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects, id=userid)
    if requests.method == 'POST':  # if HTTP method is POST
        username = str(requests.POST['username']).strip().lower()
        fpwd = requests.POST['fpwd']    # First pwd
        spwd = requests.POST['spwd']    # second pwd
        gender = requests.POST['gender']
        type = requests.POST['Type']
        status = requests.POST['Status']
        if username and fpwd and spwd and gender and type and status and fpwd == spwd:
            try:  # check if username exist
                APP_User.objects.get(username=username)
                messages.error(
                    requests, "OOOps ! Ce nom d'utilisateur existe déjà !")
                return redirect('/settings/manage-users')
            except APP_User.DoesNotExist:
                fpwd = make_password(fpwd)
                profilepath = f'profiles/{username}'
                if not os.path.exists(profilepath):
                    os.makedirs(profilepath)
                APP_User.objects.create(username=username, password=fpwd, gender=gender,ProfileFolderPath=profilepath, userpermission=type, account_status=status)
                actiondetail = f"{User.username} creé un utilisateur avec le nom {username} {Fix_Date(str(datetime.today()))}"
                APP_History.objects.create(
                    CreatedBy=User,
                    action=f'creé un utilisateur',
                    action_detail=actiondetail,
                    DateTime=str(datetime.today())
                )
                messages.info(
                    requests, f"l'utilisateur {username} a été créé avec succès")
                return redirect('/settings/manage-users')
        else:
            messages.error(
                requests, "veuillez saisir des correct informations")
            return redirect('/settings/manage-users')
    else:
        return HTTP_404(requests)

########################################################


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
        return render(requests,'Events/All-History.html',context)
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
        return render(requests,'Settings/global-settings.html',context)
    elif requests.method == 'POST':
        ICE = str(requests.POST['ICE']).strip().upper()
        TVATAUX = requests.POST['TVATAUX']
        Place = requests.POST['place']
        if ICE and TVATAUX and Place:
            if settings:
                settings.Company_ICE = ICE
                settings.Company_Place = Place
                settings.Company_TVATAUX = TVATAUX
                settings.save()
                messages.info(requests,'Les paramètres ont été modifiés avec succès')
                return redirect('/settings/global-settings')
            elif not settings:
                APP_Settings.objects.create(Company_ICE=ICE,Company_TVATAUX=TVATAUX,Company_Place=Place)
                messages.info(requests, 'Les paramètres ont été créés avec succès')
                return redirect('/settings/global-settings')
        else :
            messages.info(
                requests, 'veuillez vérifier que toutes les informations sont correctes')
            return redirect('/settings/global-settings')
########################################################



########################################################
# Error Pages 
########################################################
@RequireLogin
def HTTP_404(request, exception=None, *args, **kwargs):
    response = render(request, "ErrorPages/404.html")
    response.status_code = 404
    return response

@RequireLogin
def HTTP_500(request):
    context = {}
    response = render(request, "ErrorPages/500.html", context=context)
    response.status_code = 500
    return response

@RequireLogin
def HTTP_403(request, context=None, *args, **kwargs):
    response = render(request, "ErrorPages/403.html", context=context)
    response.status_code = 403
    return response
########################################################