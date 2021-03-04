from django.urls import path
from . import views
from dashboard.Handlers import (
                                    Users_Handler,
                                    Facture_Handler,
                                    GETJsonINFO_Handler,
                                    Clients_Handler,
                                    Products_Handler,
                                    Profile_Handler,
                                    AUTH_Handler,
                                )
urlpatterns = [
    # Auth Urls 
    path('login/', AUTH_Handler.Login, name='Login'),
    path('logout/', AUTH_Handler.Logout, name='Logout'),

    # Dashboard Urls
    path('', views.Dashboard, name='Dashboard'),
    path('dashboard/', views.Dashboard, name='Dashboard'),

    # List All Facture Urls
    path('list-all-facturs/', Facture_Handler.H_List_All_Factures,
         name='Create New Facture'),
    path('list-all-facturs/delete/<int:id>',Facture_Handler.H_Delete_Facture, name='Delete Facture By Id'),
    path('list-all-facturs/edit/<int:facture_id>',
         Facture_Handler.H_Edit_Facture, name='Edit Facture By Id'),
    path('list-all-facturs/detail/open/<int:facture_id>',Facture_Handler.H_OpenPdf, name='Open  PDFFacture By Id'),

    # profile Urls
    path('profile/', Profile_Handler.Profile, name='Profile'),
    path('profile/changepwd/', Profile_Handler.Change_Password,
         name='Change My Account Password'),
    path('profile/delete/<int:id>', Facture_Handler.H_Delete_Facture,name='Delete Facture By Id'),
    path('deletemyacount/', Profile_Handler.Delete_My_Acount,
         name='Delete My Account'),

    # Settings Urls
    path('settings/', views.Settings, name='Settings'),
        # Globale Settings
    path('settings/global-settings', views.GlobaleSettings, name='Globale Settings'),
        # Manage Products
            # Facture Product
    path('settings/manage-products',Products_Handler.ManageProducts, name='Manage Products'),
    path('settings/manage-products/edit/<int:id>', Products_Handler.EditProduct, name='Manage Products'),
    path('settings/manage-products/delete/<int:id>',Products_Handler.DeleteProduct, name='Manage Products'),
        # Manage Clients
    path('settings/manage-clients/edit/<int:id>',
         Clients_Handler.EditClient, name='Delete Client By Id'),
    path('settings/manage-clients/delete/<int:id>',
         Clients_Handler.DeleteClient, name='Delete Client By Id'),
    path('settings/manage-clients',
         Clients_Handler.ManageClients, name='Manage Clients'),
        # Manage Users
    path('settings/manage-users', Users_Handler.ManageUsers, name='Manage User'),
    path('settings/manage-users/edit/<int:id>',
         Users_Handler.EditUser, name='Edit User'),
    path('settings/manage-users/edit/changepwd/<int:id>',
         Users_Handler.ChangeUserPassword, name='Change User Pwd'),
    path('settings/manage-users/profile/<int:id>',
         Users_Handler.ShowUserProfile, name='show  User profile'),
    path('settings/deleteacount/<int:id>',
         Users_Handler.DeleteUser, name='Delete User'),
    path('settings/adduser/', Users_Handler.AddUser, name='Add new User'),


    # Create Facture Urls
    path('create-new-facture/', Facture_Handler.H_Create_New_Facture,name='Create New Facture'),
    path('create-new-facture/getclientinfo/<str:clientname>',GETJsonINFO_Handler.GetClientInfoByName, name='Get Client Jsoninfo By Name'),
    path('create-new-facture/getproductinfo/<str:productname>',GETJsonINFO_Handler.GetProductInfoByName, name='Get Product Json-info By Name'),


    # List ALL Events (History & Warnning) : 
    path('All-Histories/', views.ShowAllHistory, name='Show All Histories'),

]   
