import json
import os
import shutil
from datetime import datetime, timedelta
from urllib.parse import unquote

from dashboard.APPfunctions.APPfunctions import *
from dashboard.Handlers.AUTH_Handler import RequireLogin, RequirePermission
from dashboard.Handlers.ERROR_Handlers import *
from dashboard.models import *
from dashboard.pdf_templates.BL.bl import DrawNotechPdf
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.http import FileResponse, JsonResponse
from django.shortcuts import HttpResponse, get_object_or_404, redirect, render


@RequireLogin
def H_Create_New_BL(requests):
    # Get Loged User Id from Session_id
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects, id=userid)
    # Get All BLs From DB And Work With them
    All_BLs = APP_Created_BL.objects.all()
    context = {
        'pagetitle': 'Nouvelle BL',
        'todaydate': datetime.today().strftime('%Y-%m-%d'),
        'new_BL_number': len(All_BLs) + 1,
        'User': User,
        'selecteditem': 'BL'
    }
    if requests.method == "GET":
        context['selectbody'] = [
            clientname.Client_Name for clientname in list(APP_Clients.objects.all())]
        context['selectproductbody'] = [
            product.DESIGNATION for product in list(APP_Products.objects.all())]
        return render(requests, 'CreateNew/Creat-New-BL.html', context)
    elif requests.method == "POST":
        # Get Post Data
        datatable = json.loads(requests.POST['datatable'])['myrows']
        BL_number = requests.POST['BL_number']
        client_name = requests.POST['client_name']
        ICE = requests.POST['ICE']
        place = requests.POST['place']
        date = requests.POST['date']

        # check if len(datatable)!=0 and all len() rows in that table != 4
        if len(datatable) != 0:
            datatable_status = 'not valid'
            for row in datatable:
                if row['DESIGNATION'] and row['P.T'] and row['P.U'] and row['Qs']:
                    datatable_status = 'valid'
                else:
                    datatable_status = 'not valid'
                    break
        else:
            datatable_status = 'not valid'
        # Check All Required POST Data
        if datatable and BL_number and client_name and client_name != '-' and ICE and place and date and datatable_status == 'valid':
            # Check if BL_number already Exist
            all_BL_numbers = [n.number for n in All_BLs]
            if int(BL_number) in all_BL_numbers:

                messages.error(
                    requests, f"un BL avec le même numéro ({BL_number}) existe déjà")
                return redirect('/create-new-bl/')
            if int(BL_number) not in all_BL_numbers:
                # Created BL With POST data if BL_number not found
                BL = APP_Created_BL.objects.create(
                    number=BL_number,
                    Client_Name=client_name,
                    ICE=ICE,
                    Place=place,
                    Date=date,
                    CreatedBy=User,
                )
                # Create a History
                actiondetail = f'{User.username} crée un nouvelle BL avec le numéro {BL_number} en {Fix_Date(str(datetime.today()))}'
                APP_History.objects.create(
                    CreatedBy=User,
                    action='créer un BL',
                    action_detail=actiondetail,
                )
                # Turn Json Table Data into Python Dict
                for data in datatable:
                    # For item in DataTable Create item
                    APP_BL_items.objects.create(
                        Qs=data['Qs'],
                        DESIGNATION=data['DESIGNATION'],
                        PU=data['P.U'],
                        PT=data['P.T'],
                        BelongToBL=BL
                    )
                messages.info(
                    requests, f"Le BL {BL_number} a été crée avec succès")
                return redirect(f'/list-all-bl/')
        else:
            messages.error(requests, "Veuillez remplir toutes les données")
            return redirect('/create-new-bl/')


@RequireLogin
def H_Delete_BL(requests, id):
    context = {'pagetitle': f'Supprimer un BL'}
    # remove delete/<id> from URL
    redirect_after_done = '/list-all-bl/'
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User, id=userid)
    context['User'] = User
    BL = get_object_or_404(APP_Created_BL, id=id)
    context['BL'] = BL
    if User.userpermission == 'Admin':
        if requests.method == "POST" and requests.POST['password']:
            password = requests.POST['password']
            if check_password(password, User.password):
                BL_items = APP_BL_items.objects.filter(
                    BelongToBL=BL)
                BL_items.delete()
                BL.delete()
                actionmsg = f'{User.username} Supprimer Le BL {BL.number}'
                APP_History.objects.create(
                    CreatedBy=User, action='Supprimer un BL', action_detail=actionmsg)
                messages.info(
                    requests, "Le BL a été supprimée avec succès")
                return redirect(redirect_after_done)
            else:
                messages.error(requests, "Oops, Mot de passe incorrect !")
                return redirect(redirect_after_done)
        elif requests.method == "GET":
            return HTTP_404(requests)
    else:
        APP_Warning.objects.create(
            what='supprimer', what_detail=f'{User.username} essayez de supprimer Le BL avec le nombre {BL.BL_number}', Who=User.username)
        return HTTP_403(request=requests, context=context)


@RequireLogin
# Require Login || Admin || author Permission
def H_Edit_BL(requests, BL_id):
    # Get Loged User Id from Session_id
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects, id=userid)
    # Context
    context = {'pagetitle': 'Edité Le BL',
               'User': User, 'selecteditem': 'list-all-BLs'}
    # template Path
    templatepath = 'Edit/edit_BL.html'
    # Get requests BL by id
    BL = get_object_or_404(APP_Created_BL, id=BL_id)
    # Edit BL Require Admin Account or The Creator of this BL
    if User.userpermission == 'Admin' or BL.CreatedBy.id == userid:
        if requests.method == "GET":
            # Pass All Clients name in context to show them in select2
            context['selectbody'] = [
                clientname.Client_Name for clientname in list(APP_Clients.objects.all())]
            # Pass All Product name in context to show them in select2
            context['selectproductbody'] = [
                product.DESIGNATION for product in list(APP_Products.objects.all())]
            # Pass the BL item
            context['BL'] = BL
            # Pass the Date of BL
            context['Date'] = BL.Date.strftime('%Y-%m-%d')
            # Get All BL items that belong to that BL
            BL_item = APP_BL_items.objects.filter(
                BelongToBL=BL)
            # generate table of BL items and pass him in context
            table = generate_table_of_BL_items(BL_items=BL_item)
            context['tablebody'] = table
            # pass client name
            context['client'] = BL.Client_Name
            return render(requests, templatepath, context)
        elif requests.method == "POST":
            # Get Post Data
            # get datatable and convert it from json to python dict and get data from myrows
            datatable = json.loads(requests.POST['datatable'])['myrows']
            BL_number = requests.POST['BL_number']
            client_name = requests.POST['client_name']
            ICE = requests.POST['ICE']
            place = requests.POST['place']
            date = requests.POST['date']
            # check if len(datatable)!=0 and all len() rows in that table != 4
            if len(datatable) != 0:
                datatable_status = 'not valid'
                for row in datatable:
                    if row['DESIGNATION'] and row['P.T'] and row['P.U'] and row['Qs']:
                        datatable_status = 'valid'
                    else:
                        datatable_status = 'not valid'
                        break
            else:
                datatable_status = 'not valid'
            # Check if all required values are in POST
            if datatable and BL_number and client_name and ICE and place and date and datatable_status == 'valid':
                BL.Client_Name = client_name
                BL.ICE = ICE
                BL.Place = place
                BL.Date = date
                actiondetail = f'{User.username} editer un BL avec le numéro {BL_number} en {Fix_Date(str(datetime.today()))}'
                APP_History.objects.create(
                    CreatedBy=User,
                    action='editer un BL',
                    action_detail=actiondetail,
                    DateTime=str(datetime.today())
                )
                APP_BL_items.objects.filter(BelongToBL=BL).delete()
                for data in datatable:
                    try:
                        APP_BL_items.objects.create(
                            Qs=data['Qs'], DESIGNATION=data['DESIGNATION'], PU=data['P.U'], PT=data['P.T'], BelongToBL=BL)
                    except Exception as err:
                        print(err)
                BL.save()
                messages.info(
                    requests, f"Le BL {BL_number} a été éditer avec succès")
                return redirect(f'/list-all-bl/')
            else:
                messages.error(requests, "Veuillez remplir toutes les données")
                return redirect(f'/list-all-bl/edit/{BL_id}')
    else:
        return PermissionErrMsg_and_Warning_Handler(requests, 'Éditer', f'{User.username} essayez de Éditer Le BL avec le nombre {BL.BL_number}', User.username, context, templatepath)


@RequireLogin
# All BLs Table
def H_List_All_BL(requests):
    # Get Loged User Id from Session_id
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects, id=userid)
    # context
    context = {'pagetitle': 'Lister Toutes Les BL',
               'User': User, 'selecteditem': 'list-all-BLs'}
    if requests.method == "GET":
        # Generate HTML Table and Pass it in context

        # For each client get his BL's :
        all_bl_clients = list(set([(clientobj.Client_Name,clientobj.ICE,clientobj.Place) for clientobj in  APP_Created_BL.objects.all()]))
        all_stuff = []
        n = 0
        for client in  all_bl_clients:
            BLs = APP_Created_BL.objects.filter(Client_Name=client[0],ICE=client[1],Place=client[2])
            tablebody = generate_table_of_BL(BL=BLs), client[0], n
            all_stuff.append(tablebody)
            n = n + 1
        context['all_stuff'] = all_stuff
        return render(requests, 'List-All-Factures/Created-BL.html', context)


@RequireLogin
def H_OpenPdf(requests, BL_id):
    context = {'pagetitle': 'PDF BL'}
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects, id=userid)
    context['User'] = User
    try:
        BL = APP_Created_BL.objects.get(id=BL_id)
        context['BL'] = BL
        if requests.method == "GET":
            BL_item = APP_BL_items.objects.filter(BelongToBL=BL)
            try:
                CalculedTOTAL = Calcule_TVA_TOTAL_TTC(BL_item)
                Company_City = APP_Settings.objects.all().first().Company_Place
                filepath = DrawNotechPdf(BL, BL_item, CalculedTOTAL, Company_City)
            except AttributeError:
                return render(requests, 'ErrorPages/COMPANY_INFORMATIONS_ERR.html', context)
            return FileResponse(open(filepath, 'rb'), content_type='application/pdf')
        else:
            return HTTP_404(requests, context)
    except APP_Created_BL.DoesNotExist:
        return HTTP_404(requests, context)
