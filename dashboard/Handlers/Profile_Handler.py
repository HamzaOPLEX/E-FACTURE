from dashboard.Handlers.AUTH_Handler import RequireLogin, RequirePermission
from dashboard.Handlers.ERROR_Handlers import *
from dashboard.models import APP_User, APP_History, APP_Created_Facture
from django.contrib.auth.hashers import check_password, make_password
from datetime import datetime, timedelta
from django.contrib import messages
from django.shortcuts import HttpResponse, redirect, render, get_object_or_404
from dashboard.APPfunctions.APPfunctions import Fix_Date

@RequireLogin
def Profile(requests):
    context = {'pagetitle': 'User Profile'}
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects, id=userid)
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
    User = get_object_or_404(APP_User.objects, id=userid)
    context['User'] = User
    if requests.method == "POST":
        password = requests.POST['password']
        if password and check_password(password, User.password):
            User.delete()
            requests.session.flush()
            messages.error(requests, "votre compte a été supprimé avec succès")
            return redirect('/login/')
        else:
            messages.error(requests, "Oops, Mot de passe incorrect !")
            return redirect('/profile/')
    else:
        return HTTP_404(requests, context)


@RequireLogin
def Change_Password(requests):
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects, id=userid)
    if requests.method == "POST":
        oldpwd = requests.POST['oldpwd']
        newpwd = requests.POST['newpwd']
        retypednewpwd = requests.POST['retypednewpwd']
        if check_password(oldpwd, User.password) and newpwd == retypednewpwd:
            User.password = make_password(newpwd)
            User.save()
            actionmsg = f'{User.username} changer son mot de passe'
            APP_History.objects.create(
                CreatedBy=User, action='Changer mot de pass', action_detail=actionmsg)
            messages.error(requests, 'mot de passe changé avec succès :)')
            return redirect('/profile/')
        else:
            messages.error(
                requests, 'Oooops ! Ancien mot de passe incorrect :( ')
            return redirect('/profile/')
    else:
        return HTTP_404(requests)
