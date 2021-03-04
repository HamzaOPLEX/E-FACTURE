from django.shortcuts import redirect, get_object_or_404

from dashboard.APPfunctions.APPfunctions import *



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
                messages.info(
                    requests, 'Votre session a expiré veuillez vous connecter pour continuer')
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
                messages.info(
                    requests, 'Votre session a expiré veuillez vous connecter pour continuer')
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
