from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    # Auth Urls 
    path('login/', views.Login, name='Login'),
    path('logout/', views.Logout, name='Logout'),

    # Dashboard Urls
    path('', views.Dashboard, name='Dashboard'),
    path('dashboard/', views.Dashboard, name='Dashboard'),

    # List All Facture Urls
    path('list-all-facturs/', views.List_All_Factures, name='Create New Facture'),
    path('list-all-facturs/delete/<int:id>',views.Delete_Facture, name='Delete Facture By Id'),
    path('list-all-facturs/edit/<int:facture_id>',views.Edit_Facture, name='Edit Facture By Id'),
    path('list-all-facturs/detail/open/<int:facture_id>',views.OpenPdf, name='Open  PDFFacture By Id'),

    # profile Urls
    path('profile/', views.Profile, name='Profile'),
    path('profile/changepwd/', views.Change_Password,name='Change  My Account Password'),
    path('profile/delete/<int:id>', views.Delete_Facture,name='Delete Facture By Id'),
    path('deletemyacount/', views.Delete_My_Acount, name='Delete My Account'),

    # Settings Urls
    path('settings/', views.Settings, name='Settings'),
        # Globale Settings
    path('settings/global-settings', views.GlobaleSettings, name='Globale Settings'),
        # Manage Products
            # Facture Product
    path('settings/manage-products', views.ManageProducts, name='Manage Products'),
    path('settings/manage-products/edit/<int:id>', views.EditProduct, name='Manage Products'),
    path('settings/manage-products/delete/<int:id>', views.DeleteProduct, name='Manage Products'),
        # Manage Clients
    path('settings/manage-clients/edit/<int:id>', views.EditClient, name='Delete Client By Id'),
    path('settings/manage-clients/delete/<int:id>', views.DeleteClient, name='Delete Client By Id'),
    path('settings/manage-clients', views.ManageClients, name='Manage Clients'),
        # Manage Users
    path('settings/manage-users', views.ManageUsers, name='Manage User'),
    path('settings/manage-users/edit/<int:id>', views.EditUser, name='Edit User'),
    path('settings/manage-users/edit/changepwd/<int:id>',views.ChangeUserPassword, name='Change User Pwd'),
    path('settings/manage-users/profile/<int:id>', views.ShowUserProfile, name='show  User profile'),
    path('settings/deleteacount/<int:id>', views.DeleteUser, name='Delete User'),
    path('settings/adduser/', views.AddUser, name='Add new User'),





    # Create Facture Urls
    path('create-new-facture/', views.Create_New_Facture,name='Create New Facture'),
    path('create-new-facture/getclientinfo/<str:clientname>',views.GetClientInfoByName, name='Get Client Jsoninfo By Name'),
    path('create-new-facture/getproductinfo/<str:productname>',views.GetProductInfoByName, name='Get Product Json-info By Name'),


    # List ALL Events (History & Warnning) : 
    path('All-Histories/', views.ShowAllHistory, name='Show All Histories'),

]   
