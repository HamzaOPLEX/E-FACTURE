
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from dashboard.models import APP_Clients,APP_Products
from dashboard.Handlers.AUTH_Handler import RequireLogin, RequirePermission
from urllib.parse import unquote
import json

@RequireLogin
def GetClientInfoByName(requests, clientname):
    if requests.method == 'GET':
        clientname = unquote(clientname)
        client = get_object_or_404(APP_Clients, Client_Name=str(clientname).strip())
        client_info = {
            'ICE': client.ICE,
            'City': client.City,
        }
        return JsonResponse(client_info)


@RequireLogin
def GetProductInfoByName(requests, productname):
    if requests.method == 'GET':
        productname = unquote(productname)
        product = get_object_or_404(APP_Products, DESIGNATION=str(productname).strip().lower())
        product_info = {
            'DESIGNATION': product.DESIGNATION,
            'PU': product.PU,
        }
        return JsonResponse(product_info)
