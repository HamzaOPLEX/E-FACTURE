import json
import os
import shutil
from datetime import datetime, timedelta
from urllib.parse import unquote

from dashboard.APPfunctions.APPfunctions import *
from dashboard.Handlers.AUTH_Handler import RequireLogin, RequirePermission
from dashboard.Handlers.ERROR_Handlers import *
from dashboard.models import *
from dashboard.pdf_templates.Invoice.Invoice import DrawNotechPdf
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.http import FileResponse, JsonResponse
from django.shortcuts import HttpResponse, get_object_or_404, redirect, render


@RequireLogin
def H_Create_New_Facture(requests):
    # Get Loged User Id from Session_id
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects, id=userid)
    # Get All Factures From DB And Work With them
    All_Factures_ID = [facture.number for facture in APP_Created_Facture.objects.all()]
    All_Factures = APP_Created_Facture.objects.all()
    new_facture_number = GetNewNumber(APP_Created_Facture)
    context = {
        'pagetitle': 'Nouvelle facture',
        'todaydate': datetime.today().strftime('%Y-%m-%d'),
        'new_facture_number': new_facture_number,
        'User': User,
        'selecteditem': 'facture'
    }
    settings = APP_Settings.objects.all().first()
    template_path = settings.APP_lang+'/CreateNew/Creat-New-Facture.html'
    if requests.method == "GET":
        context['setting'] = settings
        context['selectbody'] = GetClientsListWith_ID()
        context['selectproductbody'] = [
            product.DESIGNATION for product in list(APP_Products.objects.all())]
        return render(requests, template_path, context)
    elif requests.method == "POST":
        # Get Post Data
        datatable = json.loads(requests.POST['datatable'])['myrows']
        facture_number = requests.POST['facture_number']
        client = int(requests.POST['client_name'])
        date = requests.POST['date']
        isPaid = requests.POST['ispaid']
        TTTCorHT = requests.POST['TTTCorHT']
        # check if len(datatable)!=0 and all len() rows in that table != 4
        if len(datatable) != 0:
            datatable_status = 'not valid'
            for row in datatable:
                if row[list(row.keys())[0]] and row[list(row.keys())[1]] and row[list(row.keys())[2]] and row[list(row.keys())[3]]:
                    datatable_status = 'valid'
                else:
                    datatable_status = 'not valid'
                    break
        else:
            datatable_status = 'not valid'
        # Check All Required POST Data
        if datatable and facture_number and client and client != '-' and date and datatable_status == 'valid':
            if isPaid == 'Oui':
                paid_method = requests.POST['paiementmethod']
                try :
                    avance = round(float(requests.POST['avance']),2)
                except Exception:
                    avance = 0
                if paid_method not in ['Espèces', 'Chèque']:
                    messages.error(requests, "paid method erreur")
                    return redirect('/create-new-facture/')
            else:
                paid_method = 'aucun'
                avance = 0
                isPaid = 'Non'
            # Check if facture_number already Exist
            all_facture_numbers = [n.number for n in All_Factures]
            if int(facture_number) in all_facture_numbers:
                messages.error(requests, f"Une facture avec le même numéro ({facture_number}) existe déjà")
                return redirect('/create-new-facture/')
            if int(facture_number) not in all_facture_numbers:
                HT = 0
                TVA = 0
                TTC = 0

                # Created Facture With POST data if facture_number not found
                CLIENT = get_object_or_404(APP_Clients,id=client)
                facture = APP_Created_Facture.objects.create(
                    number=facture_number,
                    Client=CLIENT,
                    Date=date,
                    CreatedBy=User,
                    isPaid=isPaid,
                    Avance=avance,
                    Paiment_Mathod=paid_method,
                    HT=HT,
                    TVA=TVA,
                    TTC=TTC
                )
                # Turn Json Table Data into Python Dict-
                for data in datatable:
                    # For item in DataTable Create item
                    PT = data[list(data.keys())[3]]
                    HT = HT + float(PT)
                    APP_Facture_items.objects.create(
                        Qs=data[list(data.keys())[0]],
                        DESIGNATION=data[list(data.keys())[1]],
                        PU=data[list(data.keys())[2]],
                        PT=PT,
                        BelongToFacture=facture
                    )
                TVA = HT / 100 * float(settings.Company_TVATAUX)
                TTC = HT + TVA
                facture.HT = HT
                facture.TVA = TVA
                facture.TTC = TTC
                facture.TTCorHT = TTTCorHT
                facture.save()
                # Create a History
                actiondetail = f'{User.username} crée une nouvelle facture avec le numéro {facture_number} en {Fix_Date(str(datetime.today()))}'
                APP_History.objects.create(
                    CreatedBy=User,
                    action='créer une facture',
                    action_detail=actiondetail,
                )
                messages.info(
                    requests, f"La facture {facture_number} a été crée avec succès")
                return redirect(f'/list-all-facturs/')
        else:
            messages.error(requests, "Veuillez remplir toutes les données")
            return redirect('/create-new-facture/')

@RequireLogin
def H_Delete_Facture(requests, id):
    context = {'pagetitle': f'Supprimer une facture'}
    # remove delete/<id> from URL
    redirect_after_done = '/'.join(str(requests.get_full_path()).split('/')[0:-2])
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
                actionmsg = f'{User.username} Supprimer la facture {facture.number}'
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
        APP_Warning.objects.create(what='supprimer', what_detail=f'{User.username} essayez de supprimer la facture avec le nombre {facture.number}', Who=User.username)
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
    settings = APP_Settings.objects.all().first()
    templatepath = settings.APP_lang+'/Edit/edit_facture.html'
    # Get requests facture by id
    Facture = get_object_or_404(APP_Created_Facture, id=facture_id)
    # Edit Facture Require Admin Account or The Creator of this Facture
    if User.userpermission == 'Admin' or Facture.CreatedBy.id == userid:
        if requests.method == "GET":
            settings = APP_Settings.objects.all().first()
            context['setting'] = settings
            # Pass All Clients name in context to show them in select2
            context['selectbody'] = GetClientsListWith_ID()
            # Pass All Product name in context to show them in select2
            context['selectproductbody'] = [product.DESIGNATION for product in list(APP_Products.objects.all())]
            # Pass the Facture item
            context['facture'] = Facture
            # Pass the Date of Facture
            context['Date'] = Facture.Date.strftime('%Y-%m-%d')
            # Get All Facture items that belong to that Facture
            Facture_item = APP_Facture_items.objects.filter(BelongToFacture=Facture)
            # generate table of facture items and pass him in context
            table = generate_table_of_facture_items(Facture_item)
            context['tablebody'] = table
            # pass client name
            context['ClientID'] = Facture.Client.id
            context['len_item'] = len(Facture_item)
            context['TT_INFO'] = (Facture.HT,Facture.TVA,Facture.TTC)
            context['TTTCorHT'] = Facture.TTCorHT
          
            return render(requests, templatepath, context)
        elif requests.method == "POST":
            # Get Post Data
            # get datatable and convert it from json to python dict and get data from myrows
            datatable = json.loads(requests.POST['datatable'])['myrows']
            ClientID = int(requests.POST['client_name'])
            date = requests.POST['date']
            isPaid = requests.POST['ispaid']
            TTTCorHT = requests.POST['TTTCorHT']
            # check if len(datatable)!=0 and all len() rows in that table != 4
            if len(datatable) != 0:
                datatable_status = 'not valid'
                for row in datatable:
                    if row[list(row.keys())[0]] and row[list(row.keys())[1]] and row[list(row.keys())[2]] and row[list(row.keys())[3]]:
                        datatable_status = 'valid'
                    else:
                        datatable_status = 'not valid'
                        break
            else:
                datatable_status = 'not valid'
            # Check if all required values are in POST
            if datatable and ClientID and ClientID != '-' and date and datatable_status == 'valid':
                if isPaid == 'Oui':
                    paid_method = requests.POST['paiementmethod']
                    try :
                        avance = round(float(requests.POST['avance']),2)
                    except Exception:
                        avance = 0
                    if paid_method not in ['Espèces', 'Chèque']:
                        messages.error(requests, "paid method erreur")
                        return redirect('/create-new-facture/')
                else:
                    paid_method = 'aucun'
                    avance = 0
                    isPaid = 'Non'
                client = get_object_or_404(APP_Clients,id=ClientID)
                Facture.ClientID = client
                Facture.Date = date
                Facture.isPaid = isPaid
                Facture.Paiment_Mathod = paid_method
                Facture.Avance = avance
                actiondetail = f'{User.username} editer une facture avec le numéro {Facture.number} en {Fix_Date(str(datetime.today()))}'
                APP_History.objects.create(
                    CreatedBy=User,
                    action='editer une facture',
                    action_detail=actiondetail,
                    DateTime=str(datetime.today())
                )
                APP_Facture_items.objects.filter(BelongToFacture=Facture).delete()
                HT = 0
                for data in datatable:
                    try:
                        PT = data[list(data.keys())[3]]
                        HT = HT + float(PT)
                        APP_Facture_items.objects.create(
                            Qs=data[list(data.keys())[0]],
                            DESIGNATION=data[list(data.keys())[1]],
                            PU=data[list(data.keys())[2]],
                            PT=PT,
                            BelongToFacture=Facture
                        )                    
                    except Exception as err:
                        print(err)
                TVA = HT / 100 * float(settings.Company_TVATAUX)
                TTC = HT + TVA
                Facture.HT = HT
                Facture.TVA = TVA
                Facture.TTC = TTC     
                Facture.TTCorHT = TTTCorHT           
                Facture.save()
                messages.info(
                    requests, f"la facture {Facture.number} a été éditer avec succès")
                return redirect(f'/list-all-facturs/')
            else:
                messages.error(requests, "Veuillez remplir toutes les données")
                return redirect(f'/list-all-facturs/edit/{facture_id}')
    else:
        return PermissionErrMsg_and_Warning_Handler(requests, 'Éditer', f'{User.username} essayez de Éditer la facture avec le nombre {Facture.number}', User.username, context, templatepath)

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
        settings = APP_Settings.objects.all().first()
        template_path = str(settings.APP_lang)+'/List-All-Factures/Created-Facturs.html'
        context['setting'] = settings
        # Generate HTML Table and Pass it in context
        factures = list(APP_Created_Facture.objects.all())
        tablebody = generate_table_of_created_factures(factures=factures)
        context['tablebody'] = tablebody
        return render(requests, template_path, context)

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
            Facture_item = APP_Facture_items.objects.filter(BelongToFacture=Facture)
            Company_TVATAUX = APP_Settings.objects.all().first().Company_TVATAUX
            Company_City = APP_Settings.objects.all().first().Company_Place
            filepath = DrawNotechPdf(Facture, Facture_item, Company_TVATAUX,Company_City)
            return FileResponse(open(filepath, 'rb'), content_type='application/pdf')
        else:
            return HTTP_404(requests, context)
    except APP_Created_Facture.DoesNotExist:
        return HTTP_404(requests, context)
