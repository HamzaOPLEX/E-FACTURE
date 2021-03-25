from django.shortcuts import redirect, get_object_or_404
from dashboard.APPfunctions.APPfunctions import *
from dashboard.models import APP_User, APP_History
from django.contrib.auth.hashers import check_password, make_password
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404


# Function Of Decorator That Will Check If User is Loged in  if not redirect him to login
def RequireLogin(viewfunc):
    def Check_User_Login(*args, **kwargs):
        requests = args[0]
        if requests.session.session_key and requests.session.exists(requests.session.session_key):
            try:
                userid = requests.session['session_id']
                Userstatus = get_object_or_404(
                    APP_User.objects, id=userid).account_status
            except KeyError:
                requests.session.flush()
                messages.info(requests, 'Votre session a expiré veuillez vous connecter pour continuer')
                return redirect('/login/')
            if Userstatus == 'Active':
                return viewfunc(*args, **kwargs)
            else:
                return Your_Account_Has_Been_Suspended(requests, *args, **kwargs)
        else:
            return Login_To_Continue_Handler(*args, **kwargs)
    return Check_User_Login

# Function Of Decorator That Will Check If User is Loged in  if not redirect him to login
# And Check if User is Admin


def RequirePermission(viewfunc):
    def Check_User_Permission(*args, **kwargs):
        requests = args[0]
        if requests.session.session_key and requests.session.exists(requests.session.session_key):
            try:
                userid = requests.session['session_id']
                User = get_object_or_404(APP_User.objects, id=userid)
            except KeyError:
                requests.session.flush()
                messages.info(requests, 'Votre session a expiré veuillez vous connecter pour continuer')
                return redirect('/login/')
            if User.account_status == 'Active':
                if User.userpermission == 'Admin':
                    return viewfunc(*args, **kwargs)
                elif User.userpermission != 'Admin':
                    context = {'pagetitle': '403'}
                    context['User'] = User
                    return HTTP_403(requests, context, *args, **kwargs)
            else:
                return Your_Account_Has_Been_Suspended(requests, *args, **kwargs)
        else:
            return Login_To_Continue_Handler(*args, **kwargs)
    return Check_User_Permission


# Authentication : Login
def Login(requests):
    context = {}
    if requests.method == "GET":
        if requests.session.session_key and requests.session.exists(requests.session.session_key):
            return redirect('/dashboard')
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
                    raise APP_User.DoesNotExist(
                        'APP_User matching query does not exist.')
            else:
                return Your_Account_Has_Been_Suspended(requests)
        except APP_User.DoesNotExist or Exception:
            messages.error(
                requests, f"Mot de passe ou nom d'utilisateur incorrect")
            return render(requests, 'Authentication/login.html', context)


@RequireLogin
def Logout(requests):
    if requests.session.get('session_id'):
        requests.session.flush()
    return redirect('/login/')
