import os
import shutil
from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import HttpResponse, redirect, render, get_object_or_404
from django.http import FileResponse, JsonResponse
from dashboard.models import *
from dashboard.APPfunctions.APPfunctions import *
from dashboard.pdf_templates.Invoice.Invoice import DrawNotechPdf
from urllib.parse import unquote
import json
from dashboard.Handlers.AUTH_Handler import RequireLogin,RequirePermission

@RequireLogin
def H_Create_New_Facture(requests):
    # Get Loged User Id from Session_id
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects, id=userid)
    # Get All Factures From DB And Work With them
    All_Factures = APP_Created_Facture.objects.all()
    context = {
        'pagetitle': 'Nouvelle facture',
        'todaydate': datetime.today().strftime('%Y-%m-%d'),
        'new_facture_number': len(All_Factures) + 1,
        'User': User,
        'selecteditem': 'facture'
    }
    if requests.method == "GET":
        context['selectbody'] = [
            clientname.Client_Name for clientname in list(APP_Clients.objects.all())]
        context['selectproductbody'] = [
            product.DESIGNATION for product in list(APP_Products.objects.all())]
        return render(requests, 'CreateNew/Creat-New-Facture.html', context)
    elif requests.method == "POST":
        # Get Post Data
        datatable = json.loads(requests.POST['datatable'])['myrows']
        facture_number = requests.POST['facture_number']
        client_name = requests.POST['client_name']
        ICE = requests.POST['ICE']
        place = requests.POST['place']
        date = requests.POST['date']
        isPaid = requests.POST['ispaid']

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
        if datatable and facture_number and client_name and client_name != '-' and ICE and place and date and datatable_status == 'valid':
            if isPaid == 'Oui':
                paid_method = requests.POST['paiementmethod']
                if paid_method not in ['Cart', 'Espèces', 'Chèque']:
                    messages.error(requests, "paid method erreur")
                    return redirect('/create-new-facture/')
            else:
                paid_method = 'aucun'
                isPaid = 'Non'
            # Check if facture_number already Exist
            all_facture_numbers = [n.facture_number for n in All_Factures]
            if int(facture_number) in all_facture_numbers:
                messages.error(
                    requests, f"Une facture avec le même numéro ({facture_number}) existe déjà")
                return redirect('/create-new-facture/')
            if int(facture_number) not in all_facture_numbers:
                # Created Facture With POST data if facture_number not found
                facture = APP_Created_Facture.objects.create(
                    facture_number=facture_number,
                    Client_Name=client_name,
                    ICE=ICE,
                    Place=place,
                    Date=date,
                    CreatedBy=User,
                    isPaid=isPaid,
                    Paiment_Mathod=paid_method
                )
                # Create a History
                actiondetail = f'{User.username} crée une nouvelle facture avec le numéro {facture_number} en {Fix_Date(str(datetime.today()))}'
                APP_History.objects.create(
                    CreatedBy=User,
                    action='créer une facture',
                    action_detail=actiondetail,
                )
                # Turn Json Table Data into Python Dict
                for data in datatable:
                    # For item in DataTable Create item
                    APP_Facture_items.objects.create(
                        Qs=data['Qs'],
                        DESIGNATION=data['DESIGNATION'],
                        PU=data['P.U'],
                        PT=data['P.T'],
                        BelongToFacture=facture
                    )
                messages.info(
                    requests, f"La facture {facture_number} a été crée avec succès")
                return redirect(f'/list-all-facturs/')
        else:
            messages.error(requests, "Veuillez remplir toutes les données")
            return redirect('/create-new-facture/')

@RequireLogin
def Delete_Facture(requests, id):
    context = {'pagetitle': f'Supprimer une facture'}
    # remove delete/<id> from URL
    redirect_after_done = '/'.join(str(requests.get_full_path()
                                       ).split('/')[0:-2])
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User, id=userid)
    context['User'] = User
    facture = get_object_or_404(APP_Created_Facture, id=id)
    context['facture'] = facture
    if User.userpermission == 'Admin':
        if requests.method == "POST" and requests.POST['password']:
            password = requests.POST['password']
            if check_password(password, User.password):
                facture_items = APP_Facture_items.objects.filter(
                    BelongToFacture=facture)
                facture_items.delete()
                facture.delete()
                actionmsg = f'{User.username} Supprimer la facture {facture.facture_number}'
                APP_History.objects.create(
                    CreatedBy=User, action='Supprimer une facture', action_detail=actionmsg)
                messages.info(
                    requests, "La facture a été supprimée avec succès")
                return redirect(redirect_after_done)
            else:
                messages.error(requests, "Oops, Mot de passe incorrect !")
                return redirect(redirect_after_done)
        elif requests.method == "GET":
            return HTTP_404(requests)
    else:
        APP_Warning.objects.create(
            what='supprimer', what_detail=f'{User.username} essayez de supprimer la facture avec le nombre {facture.facture_number}', Who=User.username)
        return HTTP_403(request=requests, context=context)

@RequireLogin
# Require Login || Admin || author Permission
def H_Edit_Facture(requests, facture_id):
    # Get Loged User Id from Session_id
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects, id=userid)
    # Context
    context = {'pagetitle': 'Edité La facture',
               'User': User, 'selecteditem': 'list-all-factures'}
    # template Path
    templatepath = 'Edit/edit_facture.html'
    # Get requests facture by id
    Facture = get_object_or_404(APP_Created_Facture, id=facture_id)
    # Edit Facture Require Admin Account or The Creator of this Facture
    if User.userpermission == 'Admin' or Facture.CreatedBy.id == userid:
        if requests.method == "GET":
            # Pass All Clients name in context to show them in select2
            context['selectbody'] = [
                clientname.Client_Name for clientname in list(APP_Clients.objects.all())]
            # Pass All Product name in context to show them in select2
            context['selectproductbody'] = [
                product.DESIGNATION for product in list(APP_Products.objects.all())]
            # Pass the Facture item
            context['facture'] = Facture
            # Pass the Date of Facture
            context['Date'] = Facture.Date.strftime('%Y-%m-%d')
            # Get All Facture items that belong to that Facture
            Facture_item = APP_Facture_items.objects.filter(
                BelongToFacture=Facture)
            # generate table of facture items and pass him in context
            table = generate_table_of_facture_items(Facture_item)
            context['tablebody'] = table
            # pass client name
            context['client'] = Facture.Client_Name
            return render(requests, templatepath, context)
        elif requests.method == "POST":
            # Get Post Data
            # get datatable and convert it from json to python dict and get data from myrows
            datatable = json.loads(requests.POST['datatable'])['myrows']
            facture_number = requests.POST['facture_number']
            client_name = requests.POST['client_name']
            ICE = requests.POST['ICE']
            place = requests.POST['place']
            date = requests.POST['date']
            isPaid = requests.POST['ispaid']
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
            if datatable and facture_number and client_name and ICE and place and date and datatable_status == 'valid':
                if isPaid == 'Oui':
                    paid_method = requests.POST['paiementmethod']
                    if paid_method not in ['Cart', 'Espèces', 'Chèque']:
                        messages.error(
                            requests, "Veuillez remplir toutes les données")
                        return redirect('/create-new-facture/')
                else:
                    paid_method = "aucun"
                    isPaid = 'Non'
                Facture.Client_Name = client_name
                Facture.ICE = ICE
                Facture.Place = place
                Facture.Date = date
                Facture.isPaid = isPaid
                Facture.Paiment_Mathod = paid_method
                actiondetail = f'{User.username} editer une facture avec le numéro {facture_number} en {Fix_Date(str(datetime.today()))}'
                APP_History.objects.create(
                    CreatedBy=User,
                    action='editer une facture',
                    action_detail=actiondetail,
                    DateTime=str(datetime.today())
                )
                APP_Facture_items.objects.filter(
                    BelongToFacture=Facture).delete()
                FactureFilePath = APP_Facture_File_Path.objects.filter(
                    BelongTo=Facture)
                for data in datatable:
                    try:
                        APP_Facture_items.objects.create(
                            Qs=data['Qs'], DESIGNATION=data['DESIGNATION'], PU=data['P.U'], PT=data['P.T'], BelongToFacture=Facture)
                    except Exception as err:
                        print(err)
                Facture.save()
                messages.info(
                    requests, f"la facture {facture_number} a été éditer avec succès")
                return redirect(f'/list-all-facturs/')
            else:
                messages.error(requests, "Veuillez remplir toutes les données")
                return redirect(f'/list-all-facturs/edit/{facture_id}')
    else:
        return PermissionErrMsg_and_Warning_Handler(requests, 'Éditer', f'{User.username} essayez de Éditer la facture avec le nombre {Facture.facture_number}', User.username, context, templatepath)

@RequireLogin
# All Factures Table
def H_List_All_Factures(requests):
    # Get Loged User Id from Session_id
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects, id=userid)
    # context
    context = {'pagetitle': 'Lister Toutes Les facture',
               'User': User, 'selecteditem': 'list-all-factures'}
    if requests.method == "GET":
        # Generate HTML Table and Pass it in context
        factures = list(APP_Created_Facture.objects.all())
        tablebody = generate_table_of_created_factures(factures=factures)
        context['tablebody'] = tablebody
        return render(requests, 'List-All-Factures/Created-Facturs.html', context)

@RequireLogin
def H_OpenPdf(requests, facture_id):
    context = {'pagetitle': 'PDF Facture'}
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects, id=userid)
    context['User'] = User
    try:
        Facture = APP_Created_Facture.objects.get(id=facture_id)
        context['facture'] = Facture
        if requests.method == "GET":
            Facture_item = APP_Facture_items.objects.filter(
                BelongToFacture=Facture)
            try:
                CalculedTOTAL = Calcule_TVA_TOTAL_TTC(Facture_item)
                Company_TVATAUX = APP_Settings.objects.all().first().Company_TVATAUX
                Company_ICE = APP_Settings.objects.all().first().Company_ICE
                Company_City = APP_Settings.objects.all().first().Company_Place
                filepath = DrawNotechPdf(
                    Facture, Facture_item, CalculedTOTAL, Company_TVATAUX, Company_ICE, Company_City)
            except AttributeError:
                return render(requests, 'ErrorPages/COMPANY_INFORMATIONS_ERR.html', context)
            return FileResponse(open(filepath, 'rb'), content_type='application/pdf')
        else:
            return HTTP_404(requests, context)
    except APP_Created_Facture.DoesNotExist:
        return HTTP_404(requests, context)


