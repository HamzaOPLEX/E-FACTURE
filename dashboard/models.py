from django.db import models


class APP_User(models.Model):
    genderchoices = (
        ('homme', 'homme'),
        ('femme', 'femme'),
    )
    userperm = (
        ('Admin', 'Admin'),
        ('Normal', 'Normal'),
    )
    status = (
        ('Suspendu', 'Suspendu'),
        ('Active', 'Active'),
    )
    username = models.CharField(max_length=20)
    userpermission = models.CharField(max_length=20, default='Normal', choices=userperm)
    # Admin (Edit(all),Remove(all),Add,See History(event history),Change Other Users passwords,Show All Users,Show All Created Users,List All Created)
    # Normal (Add,Edit (his own),change(his own pwd),List All Created)
    password = models.CharField(max_length=255)
    gender = models.CharField(max_length=30, choices=genderchoices, blank=False)
    ProfileFolderPath = models.TextField(editable=False)
    account_status = models.CharField(max_length=30, choices=status, blank=False, default='Suspendu')
    def __str__(self):
        return str(self.username)

# Facture Tables
########################################
class APP_Created_Facture(models.Model):
    choose_bywhatpaid = (
        ('Espèces', 'Espèces'),
        ('Chèque', 'Chèque'),
        ('Cart', 'Cart'),
    )
    choose_ispaid = (
        ('Oui','Oui'),
        ('Non','Non')
    )
    number = models.IntegerField(unique=True)
    Client_Name = models.TextField()
    ICE = models.CharField(max_length=255)
    Date = models.DateField(max_length=255)
    Place = models.CharField(max_length=255)
    CreatedBy = models.ForeignKey(APP_User, on_delete=models.SET_NULL, null=True, editable=False)
    isPaid = models.CharField(choices=choose_ispaid,max_length=5, default='Non')
    Paiment_Mathod = models.CharField(max_length=255,choices=choose_bywhatpaid, default='aucun', null=False)
    def __str__(self):
        return str(self.facture_number)+'-'+self.Client_Name

    def clean(self):
        if self.isPaid == "Non":
            self.Paiment_Mathod = 'aucun'

class APP_Facture_items(models.Model):
    Qs = models.IntegerField(default=0)
    DESIGNATION = models.TextField(default=None)
    PU = models.IntegerField(default=0)
    PT = models.BigIntegerField(default=0)
    BelongToFacture = models.ForeignKey(
        APP_Created_Facture, on_delete=models.CASCADE, editable=False)

    def __str__(self):
        return self.DESIGNATION
########################################


# Devis Tables
########################################
class APP_Created_Devis(models.Model):
    number = models.IntegerField(unique=True)
    Client_Name = models.TextField()
    ICE = models.CharField(max_length=255)
    Date = models.DateField(max_length=255)
    Place = models.CharField(max_length=255)
    CreatedBy = models.ForeignKey(
        APP_User, on_delete=models.SET_NULL, null=True, editable=False)

    # def __str__(self):
    #     return str(self.number)+'-'+self.Client_Name

class APP_Devis_items(models.Model):
    Qs = models.IntegerField(default=0)
    DESIGNATION = models.TextField(default=None)
    PU = models.IntegerField(default=0)
    PT = models.BigIntegerField(default=0)
    BelongToDevis = models.ForeignKey(APP_Created_Devis, on_delete=models.CASCADE, editable=False)

    def __str__(self):
        return self.DESIGNATION
########################################


# BL Tables
########################################
class APP_Created_BL(models.Model):
    number = models.IntegerField(unique=True)
    Client_Name = models.TextField()
    ICE = models.CharField(max_length=255)
    Date = models.DateField(max_length=255)
    Place = models.CharField(max_length=255)
    CreatedBy = models.ForeignKey(APP_User, on_delete=models.SET_NULL, null=True, editable=False)
    def __str__(self):
        return str(self.BL_number)+'-'+self.Client_Name

class APP_BL_items(models.Model):
    Qs = models.IntegerField(default=0)
    DESIGNATION = models.TextField(default=None)
    PU = models.IntegerField(default=0)
    PT = models.BigIntegerField(default=0)
    BelongToBL = models.ForeignKey(
        APP_Created_BL, on_delete=models.CASCADE, editable=False)

    def __str__(self):
        return self.DESIGNATION
########################################

# Settings Tables
########################################
class APP_Products(models.Model):
    PU = models.IntegerField()
    DESIGNATION = models.TextField()
    Number_Of_Use = models.IntegerField(default=None, null=True)
    Date = models.DateField(auto_now=True)
    def __str__(self):
        return self.DESIGNATION

class APP_Clients(models.Model):
    Client_Name = models.TextField()
    ICE = models.CharField(max_length=255)
    City = models.CharField(max_length=255)
    Date = models.DateField(auto_now=True)
    Number_Of_Use = models.IntegerField(default=None,null=True)
    def __str__(self):
        return self.Client_Name

class APP_Settings(models.Model):
    Company_ICE = models.CharField(max_length=255,default='00000000000000')
    Company_TVATAUX = models.IntegerField(default=20)
    Company_Place = models.CharField(max_length=255,default='Tanger')

    def __str__(self):
        return self.Company_ICE
########################################



# Events Tables
########################################
class APP_Warning(models.Model):
    what = models.CharField(max_length=255)
    what_detail = models.TextField()
    What_DateTime = models.DateTimeField(
        max_length=255, auto_now=True, editable=False)
    Who = models.CharField(max_length=255)

class APP_History(models.Model):
    action = models.CharField(max_length=255)
    action_detail = models.TextField()
    DateTime = models.DateTimeField(max_length=255, auto_now=True)
    CreatedBy = models.ForeignKey(
        APP_User, on_delete=models.CASCADE, editable=False)

    def __str__(self):
        return self.action_detail
########################################
