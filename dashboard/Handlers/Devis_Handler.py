import json
import os
import shutil
from datetime import datetime, timedelta
from urllib.parse import unquote

from dashboard.APPfunctions.APPfunctions import *
from dashboard.Handlers.AUTH_Handler import RequireLogin, RequirePermission
from dashboard.Handlers.ERROR_Handlers import *
from dashboard.models import *
from dashboard.pdf_templates.devis.devis import DrawNotechPdf
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.http import FileResponse, JsonResponse
from django.shortcuts import HttpResponse, get_object_or_404, redirect, render


@RequireLogin
def H_Create_New_Devis(requests):
    # Get Loged User Id from Session_id
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects, id=userid)
    # Get All Deviss From DB And Work With them
    All_Deviss = APP_Created_Devis.objects.all()
    context = {
        'pagetitle': 'Nouvelle Devis',
        'todaydate': datetime.today().strftime('%Y-%m-%d'),
        'new_Devis_number': len(All_Deviss) + 1,
        'User': User,
        'selecteditem': 'devis'
    }
    if requests.method == "GET":
        context['selectbody'] = [
            clientname.Client_Name for clientname in list(APP_Clients.objects.all())]
        context['selectproductbody'] = [
            product.DESIGNATION for product in list(APP_Products.objects.all())]
        return render(requests, 'CreateNew/Creat-New-Devis.html', context)
    elif requests.method == "POST":
        # Get Post Data
        datatable = json.loads(requests.POST['datatable'])['myrows']
        Devis_number = requests.POST['Devis_number']
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
        if datatable and Devis_number and client_name and client_name != '-' and ICE and place and date and datatable_status == 'valid':
            # Check if Devis_number already Exist
            all_Devis_numbers = [n.number for n in All_Deviss]
            if int(Devis_number) in all_Devis_numbers:

                messages.error(requests, f"un Devis avec le même numéro ({Devis_number}) existe déjà")
                return redirect('/create-new-Devis/')
            if int(Devis_number) not in all_Devis_numbers:
                # Created Devis With POST data if Devis_number not found
                Devis = APP_Created_Devis.objects.create(
                    number=Devis_number,
                    Client_Name=client_name,
                    ICE=ICE,
                    Place=place,
                    Date=date,
                    CreatedBy=User,
                )
                # Create a History
                actiondetail = f'{User.username} crée un nouvelle Devis avec le numéro {Devis_number} en {Fix_Date(str(datetime.today()))}'
                APP_History.objects.create(
                    CreatedBy=User,
                    action='créer un Devis',
                    action_detail=actiondetail,
                )
                # Turn Json Table Data into Python Dict
                for data in datatable:
                    # For item in DataTable Create item
                    APP_Devis_items.objects.create(
                        Qs=data['Qs'],
                        DESIGNATION=data['DESIGNATION'],
                        PU=data['P.U'],
                        PT=data['P.T'],
                        BelongToDevis=Devis
                    )
                messages.info(
                    requests, f"Le Devis {Devis_number} a été crée avec succès")
                return redirect(f'/list-all-devis/')
        else:
            messages.error(requests, "Veuillez remplir toutes les données")
            return redirect('/create-new-devis/')


@RequireLogin
def H_Delete_Devis(requests, id):
    context = {'pagetitle': f'Supprimer un Devis'}
    # remove delete/<id> from URL
    redirect_after_done = '/list-all-Devis/'
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User, id=userid)
    context['User'] = User
    Devis = get_object_or_404(APP_Created_Devis, id=id)
    context['Devis'] = Devis
    if User.userpermission == 'Admin':
        if requests.method == "POST" and requests.POST['password']:
            password = requests.POST['password']
            if check_password(password, User.password):
                Devis_items = APP_Devis_items.objects.filter(
                    BelongToDevis=Devis)
                Devis_items.delete()
                Devis.delete()
                actionmsg = f'{User.username} Supprimer Le Devis {Devis.number}'
                APP_History.objects.create(
                    CreatedBy=User, action='Supprimer un Devis', action_detail=actionmsg)
                messages.info(
                    requests, "Le Devis a été supprimée avec succès")
                return redirect(redirect_after_done)
            else:
                messages.error(requests, "Oops, Mot de passe incorrect !")
                return redirect(redirect_after_done)
        elif requests.method == "GET":
            return HTTP_404(requests)
    else:
        APP_Warning.objects.create(
            what='supprimer', what_detail=f'{User.username} essayez de supprimer Le Devis avec le nombre {Devis.Devis_number}', Who=User.username)
        return HTTP_403(request=requests, context=context)


@RequireLogin
# Require Login || Admin || author Permission
def H_Edit_Devis(requests, Devis_id):
    # Get Loged User Id from Session_id
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects, id=userid)
    # Context
    context = {'pagetitle': 'Edité Le Devis',
               'User': User, 'selecteditem': 'list-all-Deviss'}
    # template Path
    templatepath = 'Edit/edit_Devis.html'
    # Get requests Devis by id
    Devis = get_object_or_404(APP_Created_Devis, id=Devis_id)
    # Edit Devis Require Admin Account or The Creator of this Devis
    if User.userpermission == 'Admin' or Devis.CreatedBy.id == userid:
        if requests.method == "GET":
            # Pass All Clients name in context to show them in select2
            context['selectbody'] = [
                clientname.Client_Name for clientname in list(APP_Clients.objects.all())]
            # Pass All Product name in context to show them in select2
            context['selectproductbody'] = [
                product.DESIGNATION for product in list(APP_Products.objects.all())]
            # Pass the Devis item
            context['Devis'] = Devis
            # Pass the Date of Devis
            context['Date'] = Devis.Date.strftime('%Y-%m-%d')
            # Get All Devis items that belong to that Devis
            Devis_item = APP_Devis_items.objects.filter(
                BelongToDevis=Devis)
            # generate table of Devis items and pass him in context
            table = generate_table_of_devis_items(Devis_items=Devis_item)
            context['tablebody'] = table
            # pass client name
            context['client'] = Devis.Client_Name
            return render(requests, templatepath, context)
        elif requests.method == "POST":
            # Get Post Data
            # get datatable and convert it from json to python dict and get data from myrows
            datatable = json.loads(requests.POST['datatable'])['myrows']
            Devis_number = requests.POST['Devis_number']
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
            if datatable and Devis_number and client_name and ICE and place and date and datatable_status == 'valid':
                Devis.Client_Name = client_name
                Devis.ICE = ICE
                Devis.Place = place
                Devis.Date = date
                actiondetail = f'{User.username} editer un Devis avec le numéro {Devis_number} en {Fix_Date(str(datetime.today()))}'
                APP_History.objects.create(
                    CreatedBy=User,
                    action='editer un Devis',
                    action_detail=actiondetail,
                    DateTime=str(datetime.today())
                )
                APP_Devis_items.objects.filter(BelongToDevis=Devis).delete()
                for data in datatable:
                    try:
                        APP_Devis_items.objects.create(
                            Qs=data['Qs'], DESIGNATION=data['DESIGNATION'], PU=data['P.U'], PT=data['P.T'], BelongToDevis=Devis)
                    except Exception as err:
                        print(err)
                Devis.save()
                messages.info(
                    requests, f"Le Devis {Devis_number} a été éditer avec succès")
                return redirect(f'/list-all-Devis/')
            else:
                messages.error(requests, "Veuillez remplir toutes les données")
                return redirect(f'/list-all-Devis/edit/{Devis_id}')
    else:
        return PermissionErrMsg_and_Warning_Handler(requests, 'Éditer', f'{User.username} essayez de Éditer Le Devis avec le nombre {Devis.Devis_number}', User.username, context, templatepath)


@RequireLogin
# All Deviss Table
def H_List_All_Devis(requests):
    # Get Loged User Id from Session_id
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects, id=userid)
    # context
    context = {'pagetitle': 'Lister Toutes Les Devis',
               'User': User, 'selecteditem': 'list-all-Deviss'}
    if requests.method == "GET":
        # Generate HTML Table and Pass it in context
        Deviss = list(APP_Created_Devis.objects.all())
        tablebody = generate_table_of_devis(devis=Deviss)
        context['tablebody'] = tablebody
        return render(requests, 'List-All-Factures/Created-Devis.html', context)


@RequireLogin
def H_OpenPdf(requests, Devis_id):
    context = {'pagetitle': 'PDF Devis'}
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects, id=userid)
    context['User'] = User
    try:
        Devis = APP_Created_Devis.objects.get(id=Devis_id)
        context['Devis'] = Devis
        if requests.method == "GET":
            Devis_item = APP_Devis_items.objects.filter(BelongToDevis=Devis)
            try:
                CalculedTOTAL = Calcule_TVA_TOTAL_TTC(Devis_item)
                Company_TVATAUX = APP_Settings.objects.all().first().Company_TVATAUX
                Company_ICE = APP_Settings.objects.all().first().Company_ICE
                Company_City = APP_Settings.objects.all().first().Company_Place
                filepath = DrawNotechPdf(Devis, Devis_item, CalculedTOTAL, Company_TVATAUX, Company_ICE, Company_City)
            except AttributeError:
                return render(requests, 'ErrorPages/COMPANY_INFORMATIONS_ERR.html', context)
            return FileResponse(open(filepath, 'rb'), content_type='application/pdf')
        else:
            return HTTP_404(requests, context)
    except APP_Created_Devis.DoesNotExist:
        return HTTP_404(requests, context)
