from django.views import View
from django.template.loader import get_template
from django.http import HttpResponse
import os
from django.contrib import messages
from django.shortcuts import redirect, render
from dashboard.models import *
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Table, SimpleDocTemplate, TableStyle, Spacer, Paragraph
from reportlab import platypus
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from num2words import num2words
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER, TA_RIGHT
from django.http import Http404
from datetime import datetime
import textwrap
import re

def Login_To_Continue_Handler(requests, *args, **kwargs):
    messages.error(requests, "S'il vous plait Connectez-vous d'abord : )")
    respond = redirect('/login/')
    respond.set_cookie('REDIRECT_AFTER_LOGIN',
                       requests.get_full_path(), max_age=60)
    return respond

def Your_Account_Has_Been_Suspended(requests, *args, **kwargs):
    messages.error(requests, "Votre compte utilisateur a été suspendu")
    requests.session.flush()
    return redirect('/login')

def PermissionErrMsg_and_Warning_Handler(requests, what, what_detail, Who, context, template):
    APP_Warning.objects.create(what=what, what_detail=what_detail, Who=Who)
    PermissionMessage = f"vous n'êtes pas autorisé à {what} cette facture, contactez l'administrateur<br>(cette action sera signalée à l'administrateur)"
    context['PermissionMessage'] = PermissionMessage
    return render(requests, template, context)

def generate_table_of_facture_items(factureitemsobj, showaction=True):
    tablebody = []
    for item in factureitemsobj:
        Qs = str(item.Qs).strip()
        DESIGNATION = str(item.DESIGNATION).strip()
        PU = str(item.PU).strip()
        PT = str(item.PT).strip()
        D = {}
        D['Qs'] = Qs
        D['DT'] = DESIGNATION
        D['PU'] = PU
        D['PT'] = PT
        if showaction == True:
            action = """
                        <button type="button" class="btn btn-danger btn-sm" onclick="DeleteSelectedRow(this);"><i class="fas fa-trash"></i></button>\n
                        <button type="button" id="editrow" class="btn btn-info btn-sm" style="margin-left: 12px;padding-right: 6px;" onclick="EditSelectedRow(this);"><i class="fas fa-edit"></i></button>
                    """
            D['Action'] = action
        tablebody.append(D)
    return tablebody

def generate_table_of_clients(showaction=True, allclients=''):
    tablebody = []
    for client in allclients:
        D = {}
        name = client.Client_Name
        ICE = client.ICE
        City = client.City
        NOS = client.Number_Of_Use
        if showaction:
            id = client.id
            D['id'] = id
            D['name'] = name
            D['ICE'] = ICE
            D['City'] = City
            D['Action'] = f"""<a class='btn btn-info  btn-sm' href='#' onclick='EditClient(\"/settings/manage-clients/edit/{id}\")' title='Edit' data-toggle='tooltip'>
                                                <i class='fas fa-pencil-alt'></i>\n</a>
                            <a class='btn btn-danger btn-sm' href='#' title='Delete' onclick='EnterPwdToDeletePopup(\"/settings/manage-clients/delete/{id}\");' data-toggle='tooltip'>
                                        <i class='fas fa-trash'></i></a>\n"""
        else:
            D['name'] = name
            D['ICE'] = ICE
            D['City'] = City

        tablebody.append(D)
    return tablebody

def generate_table_of_products(showaction=True, Products=''):
    tablebody = []
    for product in Products:
        D = {}
        name = product.DESIGNATION
        PU = product.PU
        D['name'] = name
        D['PU'] = PU
        if showaction == True:
            id = product.id
            D['id'] = id
            D['Action'] = f"""<a class='btn btn-info  btn-sm' href='#' onclick='EditProduct(\"/settings/manage-products/edit/{id}\")' title='Edit' data-toggle='tooltip'>
                                                <i class='fas fa-pencil-alt'></i>\n</a>
                                    <a class='btn btn-danger btn-sm' href='#' title='Delete' onclick='EnterPwdToDeletePopup(\"/settings/manage-products/delete/{id}\");' data-toggle='tooltip'>
                                                <i class='fas fa-trash'></i></a>\n"""
        tablebody.append(D)
    return tablebody

def generate_table_of_created_factures(showaction='all', factures=''):
    factures = list(factures)[::-1]
    tablebody = []
    for facture in factures:
        facture_number = facture.number
        client = facture.Client_Name
        date = facture.Date
        CreatedBy = facture.CreatedBy
        isPaid = facture.isPaid
        Paiment_Mathod = facture.Paiment_Mathod
        D = {}
        D['N'] = facture_number
        D['client'] = client
        D['date'] = date
        D['CreatedBy'] = CreatedBy
        D['isPaid'] = isPaid
        if showaction == 'all':
            D['Paiment_Mathod'] = Paiment_Mathod
            D['Action'] = f'''<a class="btn btn-info btn-sm" href="/list-all-facturs/edit/{facture.id}" title="Edit" data-toggle="tooltip">
                                    <i class="fas fa-pencil-alt"></i>\n</a> 
                                <a class="btn btn-danger btn-sm" href="#" onclick="EnterPwdToDeletePopup(\'/list-all-facturs/delete/{facture.id}\');" title="Delete" data-toggle="tooltip">
                                    <i class="fas fa-trash"></i></a>\n
                                <a href="/list-all-facturs/detail/open/{facture.id}" target="_blank" class="btn btn-success btn-sm"><i class="fas fa-eye"></i></a>
                                '''
        elif showaction == 'Detail-Edit':
            D['Action'] = f'''<a class="btn btn-info btn-sm" href="/list-all-facturs/edit/{facture.id}" title="Edit" target='_blank' data-toggle="tooltip">
                                    <i class="fas fa-pencil-alt"></i>\n</a> 
                                <a href="/list-all-facturs/detail/open/{facture.id}" target="_blank" class="btn btn-success btn-sm"><i class="fas fa-eye"></i></a>
                            '''
        tablebody.append(D)
    return tablebody

def generate_table_of_history(histories, simpletable=False):
    histories = list(histories)[::-1]
    tablebody = []
    for history in histories:
        D = {}
        actor = history.CreatedBy
        action = history.action
        date = history.DateTime
        D['actor'] = actor
        D['action'] = action
        D['date'] = Fix_Date(date)
        if simpletable == False:
            action_detail = history.action_detail
            D['action_detail'] = action_detail
        tablebody.append(D)
    return tablebody

def generate_table_of_devis(devis=''):
    devis = list(devis)[::-1]
    tablebody = []
    for dv in devis:
        Devis_number = dv.number
        client = dv.Client_Name
        date = dv.Date
        CreatedBy = dv.CreatedBy
        D = {}
        D['N'] = Devis_number
        D['client'] = client
        D['date'] = date
        D['CreatedBy'] = CreatedBy
        D['Action'] = f'''<a class="btn btn-info btn-sm" href="/list-all-devis/edit/{dv.id}" title="Edit" data-toggle="tooltip">
                                <i class="fas fa-pencil-alt"></i>\n</a> 
                            <a class="btn btn-danger btn-sm" href="#" onclick="EnterPwdToDeletePopup(\'/list-all-devis/delete/{dv.id}\');" title="Delete" data-toggle="tooltip">
                                <i class="fas fa-trash"></i></a>\n
                            <a href="/list-all-devis/detail/open/{dv.id}" target="_blank" class="btn btn-success btn-sm"><i class="fas fa-eye"></i></a>
                            '''
        tablebody.append(D)
    return tablebody

def generate_table_of_devis_items(Devis_items=''):
    tablebody = []
    for item in Devis_items:
        Qs = str(item.Qs).strip()
        DESIGNATION = str(item.DESIGNATION).strip()
        PU = str(item.PU).strip()
        PT = str(item.PT).strip()
        D = {}
        D['Qs'] = Qs
        D['DT'] = DESIGNATION
        D['PU'] = PU
        D['PT'] = PT
        action = """
                    <button type="button" class="btn btn-danger btn-sm" onclick="DeleteSelectedRow(this);"><i class="fas fa-trash"></i></button>\n
                    <button type="button" id="editrow" class="btn btn-info btn-sm" style="margin-left: 12px;padding-right: 6px;" onclick="EditSelectedRow(this);"><i class="fas fa-edit"></i></button>
                """
        D['Action'] = action
        tablebody.append(D)
    return tablebody

def Calcule_TVA_TOTAL_TTC(factureitemsobj):
    TOTAL = 0
    TVA_taux = int(APP_Settings.objects.all().first().Company_TVATAUX)
    for item in factureitemsobj:
        PT = float(item.PT)
        TOTAL = TOTAL + PT
    TVA = TOTAL / 100 * TVA_taux
    TTC = TOTAL + TVA
    return (TOTAL, TVA, TTC)

def Fix_Date(date):
    try:
        format = "%Y-%m-%d %H:%M:%S.%f%z"
        date = datetime.strptime(str(date), format)
    except Exception:
        format = "%Y-%m-%d %H:%M:%S.%f"
        date = datetime.strptime(str(date), format)
    format = "%Y-%m-%d %H:%M:%S"
    date = datetime.strftime(date, format)
    return date
