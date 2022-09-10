from django.db import models

########################################
# Settings Tables
########################################
class APP_Products(models.Model):
    PU = models.FloatField()
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
    Number_Of_Use = models.IntegerField(default=None, null=True)

    def __str__(self):
        return self.Client_Name


class APP_Settings(models.Model):
    langs = (
        ('fr', 'fr'),
        ('ar', 'ar'),
        ('en', 'en'),
    )
    Company_ICE = models.CharField(max_length=255, default='00000000000000')
    Company_TVATAUX = models.FloatField(default=20)
    Company_Place = models.CharField(max_length=255, default='earth')
    APP_lang = models.CharField(
        max_length=3, choices=langs, default='fr', blank=False)
    Invoice_Color = models.CharField(max_length=255, default='#000000')

    def __str__(self):
        return self.Company_ICE
########################################


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
    userpermission = models.CharField(
        max_length=20, default='Normal', choices=userperm)
    # Admin (Edit(all),Remove(all),Add,See History(event history),Change Other Users passwords,Show All Users,Show All Created Users,List All Created)
    # Normal (Add,Edit (his own),change(his own pwd),List All Created)
    password = models.CharField(max_length=255)
    gender = models.CharField(
        max_length=30, choices=genderchoices, blank=False)
    ProfileFolderPath = models.TextField(editable=False)
    account_status = models.CharField(
        max_length=30, choices=status, blank=False, default='Suspendu')

    def __str__(self):
        return str(self.username)


########################################
# Devis Tables
########################################
class APP_Created_Devis(models.Model):
    number = models.IntegerField(unique=True)
    Client = models.ForeignKey(
        APP_Clients, on_delete=models.RESTRICT, default=False, null=False, editable=True)
    Date = models.DateField(max_length=255)
    CreatedBy = models.ForeignKey(
        APP_User, on_delete=models.SET_NULL, null=True, editable=False)
    HT = models.FloatField()

    def __str__(self):
        Year = self.Date.strftime('%Y')
        Serie = str(self.number).zfill(3)+'/'+str(Year)
        return 'Devis : '+Serie


class APP_Devis_items(models.Model):
    Qs = models.FloatField(default=0)
    DESIGNATION = models.TextField(default=None)
    PU = models.FloatField(default=0)
    PT = models.FloatField(default=0)
    BelongToDevis = models.ForeignKey(
        APP_Created_Devis, on_delete=models.CASCADE, editable=False)

    def __str__(self):
        return self.DESIGNATION

########################################
# BL Tables
########################################
class APP_Created_BL(models.Model):
    number = models.IntegerField(unique=True)
    Client = models.ForeignKey(APP_Clients, on_delete=models.RESTRICT, default=False, null=False, editable=True)
    Date = models.DateField(max_length=255)
    HT = models.FloatField()
    CreatedBy = models.ForeignKey(APP_User, on_delete=models.SET_NULL, null=True, editable=False)

    def __str__(self):
        Year = self.Date.strftime('%Y')
        Serie = str(self.number).zfill(3)+'/'+str(Year)
        return 'Bon De Livraison : '+Serie


class APP_BL_items(models.Model):
    Qs = models.FloatField(default=0)
    DESIGNATION = models.TextField(default=None)
    PU = models.FloatField(default=0)
    PT = models.FloatField(default=0)
    BelongToBL = models.ForeignKey(
        APP_Created_BL, on_delete=models.CASCADE, editable=False)
    Date = models.DateField(auto_now=True)

    def __str__(self):
        return self.DESIGNATION


########################################
# Facture Tables
########################################
class APP_Created_Facture(models.Model):
    choose_bywhatpaid = (
        ('Espèces', 'Espèces'),
        ('Chèque', 'Chèque'),
        ('Letter', 'Letter'),
        ('Virement', 'Virement'),
    )
    choose_ispaid = (
        ('Oui', 'Oui'),
        ('Non', 'Non')
    )
    choose_TTTCorHT = (
        ('HT', 'HT'),
        ('TTC', 'TTC')
    )
    number = models.IntegerField(unique=True)
    Client = models.ForeignKey(
        APP_Clients, on_delete=models.RESTRICT, default=False, null=False, editable=True)
    Date = models.DateField(max_length=255)
    HT = models.FloatField()
    TVA = models.FloatField()
    TTC = models.FloatField()
    TTCorHT = models.CharField(max_length=3,default='TTC',choices=choose_TTTCorHT)
    CreatedBy = models.ForeignKey(APP_User, on_delete=models.SET_NULL, null=True, editable=False)
    isPaid = models.CharField(choices=choose_ispaid,max_length=5, default='Non')
    Avance = models.FloatField(default=0)
    Paiment_Mathod = models.CharField(max_length=255, choices=choose_bywhatpaid, default='aucun', null=False)
    ConvertedFromDevis = models.ForeignKey(APP_Created_Devis, on_delete=models.SET_NULL, null=True, editable=False)
    ConvertedFromBLs = models.TextField(default=False, editable=False, null=True)

    def __str__(self):
        Year = self.Date.strftime('%Y')
        Serie = str(self.number).zfill(3)+'/'+str(Year)
        return 'Facture : '+Serie

    def clean(self):
        if self.isPaid == "Non":
            self.Paiment_Mathod = 'aucun'
            self.Avance = 0

class APP_Facture_items(models.Model):
    Qs = models.FloatField(default=0)
    DESIGNATION = models.TextField(default=None)
    PU = models.FloatField(default=0)
    PT = models.FloatField(default=0)
    BelongToFacture = models.ForeignKey(
        APP_Created_Facture, on_delete=models.CASCADE, editable=False)
    Date = models.DateField(auto_now=True)

    def __str__(self):
        return self.DESIGNATION
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
