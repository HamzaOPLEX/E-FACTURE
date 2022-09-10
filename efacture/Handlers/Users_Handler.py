from efacture.Handlers.AUTH_Handler import RequireLogin, RequirePermission
from efacture.Handlers.ERROR_Handlers import *
from efacture.models import APP_User, APP_History, APP_Created_Facture, APP_Settings
from django.contrib.auth.hashers import check_password, make_password
from datetime import datetime, timedelta
from django.contrib import messages
from django.shortcuts import HttpResponse, redirect, render, get_object_or_404
from Functions.APPfunctions import Fix_Date

@RequirePermission
def ManageUsers(requests):
    context = {'pagetitle': 'Gérer Vos Utilisateurs'}
    settings = APP_Settings.objects.all().first()
    templatepath = str(settings.APP_lang)+'/Settings/Manage-Users.html'
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects, id=userid)
    context['User'] = User
    context['selecteditem'] = 'settings'
    if requests.method == "GET":
        context['setting'] = settings        
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
                                                <i class='fas fa-trash'></i></a>\n"""
                tablebody.append(D)

        context['tablebody'] = tablebody
        return render(requests, templatepath, context)

@RequirePermission
def EditUser(requests, id):
    context = {'pagetitle': 'Edité un utilisateur'}
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects, id=userid)
    settings = APP_Settings.objects.all().first()
    context['selecteditem'] = 'settings'
    context['User'] = User
    if requests.method == 'POST':
        username = str(requests.POST['username']).strip().lower()
        gender = requests.POST['gender']
        type = requests.POST['Type']
        status = requests.POST['Status']
        if username and gender and type and status:
            user = get_object_or_404(APP_User, id=id)
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
            messages.info(
                requests, f"l'utilisateur {username} a été Edité avec succès")
            return redirect('/settings/manage-users')
        else:
            messages.error(
                requests, "veuillez saisir des correct informations")
            return redirect('/settings/manage-users')
    elif requests.method == 'GET':
        settings = APP_Settings.objects.all().first()
        context['setting'] = settings
        edit_user = get_object_or_404(APP_User, id=id)
        context['edituser'] = edit_user
        return render(requests, str(settings.APP_lang)+'/Settings/Edit-User.html', context)

@RequirePermission
def DeleteUser(requests, id):
    if requests.method == 'POST':  # if HTTP method is POST
        userid = requests.session['session_id']
        User = get_object_or_404(APP_User, id=userid)
        pwd = requests.POST['password']
        user2delete = get_object_or_404(APP_User, id=id)
        if check_password(pwd, User.password):
            messages.error(
                requests, f"l'utilisateur {user2delete.username} a été supprimé avec succès")
            user2delete.delete()
            actiondetail = f"{User.username} supprimer un utilisateur avec le nom {user2delete.username} {Fix_Date(str(datetime.today()))}"
            APP_History.objects.create(
                CreatedBy=User,
                action=f'supprimer un utilisateur',
                action_detail=actiondetail,
                DateTime=str(datetime.today())
            )
            return redirect('/settings/manage-users')
        else:
            messages.error(requests, "Ooops ! Mot de passe incorrect")
            return redirect('/settings/manage-users')
    else:
        return HTTP_404(requests)





@RequirePermission
def ChangeUserPassword(requests, id):
    context = {'pagetitle': 'Changer le mot de pass'}
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects, id=userid)
    context['selecteditem'] = 'settings'
    context['User'] = User
    settings = APP_Settings.objects.all().first()
    if requests.method == 'POST':
        fpwd = requests.POST['fpwd']
        spwd = requests.POST['spwd']
        if fpwd and spwd and fpwd == spwd:
            fpwd = make_password(fpwd)
            try:
                user = APP_User.objects.get(id=id)
                user.password = fpwd
                user.save()
                messages.info(
                    requests, f"Le mot de passe a été changé avec succès")
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
            return render(requests, str(settings.APP_lang)+'/Settings/changepwduser.html', context)
    elif requests.method == 'GET':
        
        settings = APP_Settings.objects.all().first()
        context['setting'] = settings
        try:
            edit_user = APP_User.objects.get(id=id)
            context['edituser'] = edit_user
            return render(requests, str(settings.APP_lang)+'/Settings/changepwduser.html', context)
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
                APP_User.objects.create(username=username, password=fpwd, gender=gender,userpermission=type, account_status=status)
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
