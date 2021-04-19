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
    new_bl_number = GetNewNumber(APP_Created_BL)
    context = {
        'pagetitle': 'Nouvelle BL',
        'todaydate': datetime.today().strftime('%Y-%m-%d'),
        'new_BL_number': new_bl_number,
        'User': User,
        'selecteditem': 'BL'
    }
    settings = APP_Settings.objects.all().first()
    if requests.method == "GET":
        context['setting'] = settings
        context['selectbody'] = GetClientsListWith_ID()
        context['selectproductbody'] = [product.DESIGNATION for product in list(APP_Products.objects.all())]
        return render(requests, str(settings.APP_lang)+'/CreateNew/Creat-New-BL.html', context)
    elif requests.method == "POST":
        # Get Post Data
        try :
            datatable = json.loads(requests.POST['datatable'])['myrows']
        except json.decoder.JSONDecodeError :
            pass
        BL_number = requests.POST['BL_number']
        CLIENT_ID = int(requests.POST['client_name'])
        date = requests.POST['date']

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
        if datatable and BL_number and CLIENT_ID and CLIENT_ID != '-' and date and datatable_status == 'valid':
            # Check if BL_number already Exist
            all_BL_numbers = [n.number for n in All_BLs]
            if int(BL_number) in all_BL_numbers:
                return JsonResponse({'ERR_MSG':f"Un BL avec le même numéro ({BL_number}) existe déjà"}, status=400)

            if int(BL_number) not in all_BL_numbers:
                # Created BL With POST data if BL_number not found
                CLIENT = get_object_or_404(APP_Clients,id=CLIENT_ID)
                HT = 0
                BL = APP_Created_BL.objects.create(
                    number=BL_number,
                    Client=CLIENT,
                    Date=date,
                    CreatedBy=User,
                    HT=HT,
                )
                # Create a History
                actiondetail = f'{User.username} crée un nouvelle BL avec le numéro {BL_number} en {Fix_Date(str(datetime.today()))}'
                APP_History.objects.create(
                    CreatedBy=User,
                    action='créer un BL',
                    action_detail=actiondetail,
                )
                # Turn Json Table Data into Python Dict
                ITEMS = []
                for data in datatable:
                    # For item in DataTable Create item
                    HT = HT + float(data[list(data.keys())[3]])
                    theItem = APP_BL_items(
                        Qs=data[list(data.keys())[0]],
                        DESIGNATION=data[list(data.keys())[1]],
                        PU=data[list(data.keys())[2]],
                        PT=data[list(data.keys())[3]],
                        BelongToBL=BL,
                    )
                    ITEMS.append(theItem)
                BL.HT = HT
                BL.save()
                APP_BL_items.objects.bulk_create(ITEMS)
                MSG = f"Le BL {BL.number} a été crée avec succès"
                return JsonResponse({'MSG':MSG,'ID':BL.id,'ROOT_URL':'/list-all-bl/'}, status=200)
        else:
            return JsonResponse({'ERR_MSG':"Veuillez remplir toutes les données"}, status=400)


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
    settings = APP_Settings.objects.all().first()
    User = get_object_or_404(APP_User.objects, id=userid)
    # Context
    context = {'pagetitle': 'Edité Le BL',
               'User': User, 'selecteditem': 'list-all-BLs'}
    # template Path
    templatepath = str(settings.APP_lang)+'/Edit/edit_BL.html'
    # Get requests BL by id
    BL = get_object_or_404(APP_Created_BL, id=BL_id)
    # Edit BL Require Admin Account or The Creator of this BL
    if User.userpermission == 'Admin' or BL.CreatedBy.id == userid:
        if requests.method == "GET":
            context['setting'] = settings
            # Pass All Clients name in context to show them in select2
            context['selectbody'] = GetClientsListWith_ID()

            # Pass All Product name in context to show them in select2
            context['selectproductbody'] = [
                product.DESIGNATION for product in list(APP_Products.objects.all())]
            # Pass the BL item
            context['BL'] = BL
            # Pass the Date of BL
            context['Date'] = BL.Date.strftime('%Y-%m-%d')
            # Get All BL items that belong to that BL
            BL_item = APP_BL_items.objects.filter(BelongToBL=BL)
            # generate table of BL items and pass him in context
            table = generate_table_of_BL_items(BL_items=BL_item)
            context['tablebody'] = table
            # pass client name
            context['ClientID'] = BL.Client.id
            context['len_item'] = len(BL_item)
            context['TT_INFO'] = Calcule_TVA_TOTAL_TTC(BL_item)
            return render(requests, templatepath, context)
        elif requests.method == "POST":
            # Get Post Data
            # get datatable and convert it from json to python dict and get data from myrows
            try :
                datatable = json.loads(requests.POST['datatable'])['myrows']
            except json.decoder.JSONDecodeError :
                pass

            CLIENT_ID = int(requests.POST['client_name'])
            date = requests.POST['date']
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
            if datatable  and CLIENT_ID and CLIENT_ID != '-' and datatable_status == 'valid':
                BL.Client = get_object_or_404(APP_Clients,id=CLIENT_ID)
                BL.Date = date
                actiondetail = f'{User.username} editer un BL avec le numéro {BL.number} en {Fix_Date(str(datetime.today()))}'
                APP_History.objects.create(
                    CreatedBy=User,
                    action='editer un BL',
                    action_detail=actiondetail,
                    DateTime=str(datetime.today())
                )
                APP_BL_items.objects.filter(BelongToBL=BL).delete()
                HT = 0
                ITEMS = []
                for data in datatable:
                    try:
                        PT = data[list(data.keys())[3]]
                        HT = HT + float(PT)
                        theItem = APP_BL_items(
                            Qs=data[list(data.keys())[0]],
                            DESIGNATION=data[list(data.keys())[1]],
                            PU=data[list(data.keys())[2]],
                            PT=data[list(data.keys())[3]],
                            BelongToBL=BL
                        )
                        ITEMS.append(theItem)
                    except Exception as err:
                        pass
                BL.HT = HT
                BL.save()
                APP_BL_items.objects.bulk_create(ITEMS)
                MSG = f"Le BL {BL.number} a été édité avec succes"
                return JsonResponse({'MSG':MSG,'ID':BL.id,'ROOT_URL':'/list-all-bl/'}, status=200)
            else:
                return JsonResponse({'ERR_MSG':"Veuillez remplir toutes les données"}, status=400)

    else:
        return PermissionErrMsg_and_Warning_Handler(requests, 'Éditer', f'{User.username} essayez de Éditer Le BL avec le nombre {BL.BL_number}', User.username, context, templatepath)


@RequireLogin
# All BLs Table
def H_List_All_BL(requests):
    # Get Loged User Id from Session_id
    userid = requests.session['session_id']
    settings = APP_Settings.objects.all().first()
    User = get_object_or_404(APP_User.objects, id=userid)
    # context
    context = {'pagetitle': 'Lister Toutes Les BL',
               'User': User, 'selecteditem': 'list-all-BLs'}
    if requests.method == "GET":
        """
            set() : remove duplicated clients
            n : for increment by 1 for the colapss ID
        """

        # For each client get his BL's :
        all_bl_clients = list(set([client.Client  for client in  APP_Created_BL.objects.all()]))
        all_stuff = []
        n = 0
        for client in  all_bl_clients:
            BLs = APP_Created_BL.objects.filter(Client=client)
            tablebody = generate_table_of_BL(BL=BLs), client.Client_Name, n
            all_stuff.append(tablebody)
            n = n + 1
        context['all_stuff'] = all_stuff
        context['setting'] = settings
        return render(requests, str(settings.APP_lang)+'/List-All-Factures/Created-BL.html', context)


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
            Company_City = APP_Settings.objects.all().first().Company_Place
            filepath = DrawNotechPdf(BL, BL_item, Company_City)
            return FileResponse(open(filepath, 'rb'), content_type='application/pdf')
        else:
            return HTTP_404(requests, context)
    except APP_Created_BL.DoesNotExist:
        return HTTP_404(requests, context)



@RequireLogin
def BLsTOFacture(requests):
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects, id=userid)
    if requests.method == 'POST':
        selected_bls = requests.POST['SELECTEDBL']
        selected_bls = selected_bls.split(',')
        Selected_Bls_Ids = []
        ALL_BLs_Items = [] 
        for bl_id in selected_bls :
            BL = get_object_or_404(APP_Created_BL, id=bl_id)
            Selected_Bls_Ids.append(BL.id)
            BL_items = APP_BL_items.objects.filter(BelongToBL=BL)
            for bl_item in BL_items:
                ALL_BLs_Items.append(bl_item)

        # Check if BL is Already Converted
        isConvertred = APP_Created_Facture.objects.filter(ConvertedFromBLs=json.dumps(Selected_Bls_Ids)).first()
        if isConvertred :
            facture_serie = f"{str(isConvertred.number).zfill(3)}/{isConvertred.Date.strftime('%Y')}"
            messages.info(requests, f"ceux sélectionnés BLs sont déjà convertis en facture  <<{facture_serie}>>  veuillez supprimer cette facture afin que vous puissiez les convertir".title())
            return redirect(f'/list-all-bl/')
        if not isConvertred:
            HT = 0
            TVA = 0
            TTC = 0
            # List of item that should saved after facture creation
            ITEMS_NEED_TO_SAVE = []
            facture = APP_Created_Facture(
                                        number=GetNewNumber(APP_Created_Facture) ,
                                        Client=BL.Client,
                                        CreatedBy=User,
                                        Date=datetime.today(),
                                        HT=HT,
                                        TVA=TVA,
                                        TTC=TTC,
                                        ConvertedFromBLs=json.dumps(Selected_Bls_Ids)
                                    )
            for bl_item in ALL_BLs_Items:
                # For item in DataTable Create item
                PT = bl_item.PT
                HT = HT + float(PT)
                item = APP_Facture_items(
                    Qs=bl_item.Qs,
                    DESIGNATION=bl_item.DESIGNATION,
                    PU=bl_item.PU,
                    PT=PT,
                    BelongToFacture=facture
                )
                ITEMS_NEED_TO_SAVE.append(item)
            settings = APP_Settings.objects.all().first()
            TVA = HT / 100 * float(settings.Company_TVATAUX)
            TTC = HT + TVA
            facture.HT = HT
            facture.TVA = TVA
            facture.TTC = TTC
            facture.save()
            [it.save() for it in ITEMS_NEED_TO_SAVE]
            messages.info(requests, f"tous les Bon De Livraison ont été convertis avec succès en facture {facture.number}")
            return redirect(f'/list-all-facturs/')
        


