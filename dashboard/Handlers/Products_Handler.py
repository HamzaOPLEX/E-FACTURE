from dashboard.APPfunctions.APPfunctions import Fix_Date,generate_table_of_products
from dashboard.Handlers.AUTH_Handler import RequireLogin, RequirePermission
from dashboard.Handlers.ERROR_Handlers import *
from dashboard.models import APP_Clients, APP_History, APP_User
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import get_object_or_404, redirect, render


@RequirePermission
def ManageProducts(requests):
    # Get Loged User Id from Session_id
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User.objects, id=userid)
    # Context
    context = {'pagetitle': 'Gérer Les Produits',
               'User': User, 'selecteditem': 'settings'}
    # path to Template
    templatepath = 'Settings/Manage-Products.html'
    if requests.method == "GET":
        # Generate Table Of Products and pass the Table in the context
        Products = list(APP_Products.objects.all())
        context['tablebody'] = generate_table_of_products(Products=Products)
        return render(requests, templatepath, context)
    elif requests.method == "POST":
        # Get ProductName and remove Any Space
        ProductName = str(requests.POST['ProductName']).strip().lower()
        PU = requests.POST['PU']
        if ProductName and PU:
            # Check if Exist if not Create new one
            try:
                APP_Products.objects.get(DESIGNATION=ProductName)
                messages.info(
                    requests, f'Le Produit "{ProductName}" existe déjà !')
                return redirect('/settings/manage-products')
            except APP_Products.DoesNotExist:
                APP_Products.objects.create(DESIGNATION=ProductName, PU=PU)
                actiondetail = f'{User.username} creé un nouveau produit avec le nome {ProductName}  en {Fix_Date(str(datetime.today()))}'
                APP_History.objects.create(
                    CreatedBy=User,
                    action='creé un nouveau produit',
                    action_detail=actiondetail,
                    DateTime=str(datetime.today())
                )
                messages.info(
                    requests, f'Le produit {ProductName} a été créé avec succès')
                return redirect('/settings/manage-products')
        else:
            messages.info(
                requests, f'veuillez remplir toutes les informations')
            return redirect('/settings/manage-products')


@RequirePermission
def DeleteProduct(requests, id):
    if requests.method == 'POST':
        userid = requests.session['session_id']
        User = get_object_or_404(APP_User, id=userid)
        pwd = requests.POST['password']
        products2delete = get_object_or_404(APP_Products, id=id)
        ProductName = products2delete.DESIGNATION
        if check_password(pwd, User.password):
            messages.error(
                requests, f"le Client {products2delete.DESIGNATION} a été supprimé avec succès")
            products2delete.delete()
            actiondetail = f'{User.username} supprimer un produit avec le nome {ProductName}  en {Fix_Date(str(datetime.today()))}'
            APP_History.objects.create(
                CreatedBy=User,
                action='supprimer un produit',
                action_detail=actiondetail,
                DateTime=str(datetime.today())
            )
            return redirect('/settings/manage-products')
        else:
            messages.error(requests, "Ooops ! Mot de passe incorrect")
            return redirect('/settings/manage-products')
    else:
        return HTTP_404(requests)


@RequirePermission
def EditProduct(requests, id):
    userid = requests.session['session_id']
    User = get_object_or_404(APP_User, id=userid)
    if requests.method == 'POST':
        ProductName = requests.POST['ProductName']
        PU = requests.POST['PU']
        if ProductName and PU:
            product = get_object_or_404(APP_Products, id=id)
            product.DESIGNATION = ProductName
            product.PU = PU
            product.save()
            actiondetail = f'{User.username} edité un produit avec le nome {ProductName}  en {Fix_Date(str(datetime.today()))}'
            APP_History.objects.create(
                CreatedBy=User,
                action='edité un produit',
                action_detail=actiondetail,
                DateTime=str(datetime.today())
            )
            messages.info(requests, 'Le produit a été mis à jour avec succès')
            return redirect('/settings/manage-products')
        else:
            messages.info(requests, 'Veuillez remplir toutes les informations')
            return redirect('/settings/manage-products')
    elif requests.method == 'GET':
        product = get_object_or_404(APP_Products, id=id)
        product_info = {
            'ProductName': product.DESIGNATION,
            'PU': product.PU,
        }
        return JsonResponse(product_info)
