import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Table, SimpleDocTemplate, TableStyle, Spacer, Paragraph,PageBreak
from reportlab.pdfbase import pdfmetrics
from efacture.models import APP_Settings
from reportlab import platypus
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from pathlib import Path
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfbase.ttfonts import TTFont
from colour import Color
from ..global_config.text_handler import *
from ..global_config.tables_handler import *



def DrawNotechPdf(FactureObj, FactureItemsObj, Company_TVATAUX,Company_City ):
    story = []
    BASE_DIR = Path(__file__).resolve().parent
    GLOBAL_CONFIG_PATH = str(str(BASE_DIR.parent)+"/global_config/")
    Date = FactureObj.Date.strftime('%d-%m-%Y')
    Year = FactureObj.Date.strftime('%Y')
    tabledata = []
    header = ('QS', 'DISIGNATION', 'P.U', 'PT')
    pdfmetrics.registerFont(TTFont('Arabic', GLOBAL_CONFIG_PATH+"Arabic.ttf"))





    # Styles ################################################################
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(name='TableContent',
                              alignment=TA_CENTER,
                              fontName='Arabic',
                              fontSize=9,
                              textColor=colors.black,
                              leading=13,
                              wordWrap='LTR',
                              splitLongWords=True,
                              spaceShrinkage=0.05,
                              backColor=None,
                              ))
    styles.add(ParagraphStyle(name='ClientSide',
                              alignment=TA_LEFT,
                              fontName='Arabic',
                              fontSize=9,
                              textColor=colors.black,
                              leading=13,
                              wordWrap='LTR',
                              splitLongWords=True,
                              spaceShrinkage=0.05,
                              backColor=None,
                              borderWidth=1,
                              borderPadding=10,
                              borderColor=colors.black,
                              borderRadius=5
                              ))
    styles.add(ParagraphStyle(name='CompanySide',
                              alignment=TA_LEFT,
                              fontName='Helvetica',
                              fontSize=10,
                              textColor=colors.black,
                              leading=13,
                              wordWrap='LTR',
                              splitLongWords=True,
                              spaceShrinkage=0.05,
                              backColor=None,
                              borderWidth=1,
                              borderPadding=10,
                              borderColor=colors.black,
                              borderRadius=5
                              ))
    styles.add(ParagraphStyle(name='HeaderDataStyle',
                              alignment=TA_LEFT,
                              fontName='Helvetica',
                              fontSize=10,
                              textColor=colors.black,
                              leading=13,
                              textTransform='uppercase',
                              wordWrap='LTR',
                              splitLongWords=True,
                              spaceShrinkage=0.05,
                              backColor=None,
                              borderWidth=1,
                              borderPadding=10,
                              borderColor=colors.black,
                              ))
    styles.add(ParagraphStyle(name='FooterMessage',
                              alignment=TA_CENTER,
                              fontName='Helvetica',
                              fontSize=11,
                              textColor=colors.black,
                              leading=13,
                              wordWrap='LTR',
                              splitLongWords=True,
                              spaceShrinkage=0.05,
                              ))

    HeaderDataStyle = styles['HeaderDataStyle']
    FooterMessage = styles['FooterMessage']
    ClientSide = styles['ClientSide']
    CompanySide = styles['CompanySide']
    TableContent = styles['TableContent']

    #############################################################################

    # - Start TOTAL,TVA,TTC Table Handler - ######################################
    TOTALint, TVA, TTC_int = (FactureObj.HT,FactureObj.TVA,FactureObj.TTC)
    TOTAL = ['TOTAL HT', round(TOTALint, 2)]
    if FactureObj.TTCorHT == 'TTC':
        TVA_TAUX = Company_TVATAUX
        TVA = [f'TVA {TVA_TAUX}%', round(TVA, 2)]
        TTC = ['TOTAL TTC', round(TTC_int, 2)]
        TOTALtableData = [TOTAL, TVA, TTC]
        TOTALletter = Number2Letter(str(TTC_int))
    elif FactureObj.TTCorHT == 'HT':
        TOTALtableData = [TOTAL]
        TOTALletter = Number2Letter(str(TOTALint))
    #############################################################################


    StatusTableData = []
    if FactureObj.Paiment_Mathod == 'Lettre' : 
        method = 'Lettre De Change'
    elif FactureObj.Paiment_Mathod == 'Virement':
        method = 'Virement Bancaire'
    else :
        method = FactureObj.Paiment_Mathod
    PaimentMethod_row = ['mode de paiement',method]
    StatusTableData.append(PaimentMethod_row)

    # TOP Header ################################################################
    company_side = f""" <b>Facture :</b> {str(FactureObj.number).zfill(3)}/{Year}<br/> <b>{str(Company_City).upper()} le :</b> {Date} """
    client_side = f""" <font name="HELVETICA"><b>Facturé pour :</b></font> {str(FactureObj.Client.Client_Name).title()}<br/> <font name="HELVETICA"><b>ICE :</b> {str(FactureObj.Client.ICE).upper()}<br/></font> """

    client_side = ReshapeArabic(client_side)
    client_company_table_data = [ [Paragraph(company_side, CompanySide),'',Paragraph(client_side, ClientSide)], ]
    client_company_table = Info_Table(client_company_table_data)
    #############################################################################


    TABLE_ROWS_NUMBER = 0

    for item in FactureItemsObj:
        Qs = Paragraph(ReshapeArabic(str(item.Qs).strip()), TableContent),
        DESIGNATION = Paragraph(ReshapeArabic(str(item.DESIGNATION).strip()), TableContent),
        PU = Paragraph(ReshapeArabic(str(item.PU).strip()), TableContent),
        PT = Paragraph(ReshapeArabic(str(item.PT).strip()), TableContent),
        if len(str(item.DESIGNATION).strip().title()) >= 60:
            L = len(textwrap.wrap(str(item.DESIGNATION).strip(),60))
            TABLE_ROWS_NUMBER += L 

        row = [
            Qs,
            DESIGNATION,
            PU,
            PT
        ]
        tabledata.append(row)

    # get len of tabledata to use it in internal grid 
    ROWS = 25

    # split table data to N_ROWS of chunks
    tabledata = list(chunks(tabledata,ROWS))
    # loop into chunks
    for chunk in tabledata :
        innergrid_index = len(chunk)
        if len(chunk) <= ROWS:
            emptyrows_needed = ROWS-int(len(chunk))
            for i in range(emptyrows_needed):
                empty_row = ['', '', '', '']
                chunk.append(empty_row)
        story.append(Spacer(1, .25*inch))
        story.append(client_company_table)
        story.append(Spacer(1, .25*inch))
        chunk.insert(0,header)
        table_style = myTable(chunk,innergrid_index)

        story.append(table_style)
        # check if chunk is last element in tabledata so add TOTAL info to the last table in pages
        if tabledata.index(chunk) == tabledata.index(tabledata[-1]):
            story.append(footer_info_table([[Status_Table(StatusTableData),'',TOTAL_table(TOTALtableData),]]))
            story.append(Spacer(1, .25*inch))
            Money_msg = f"Arrêté la présente facture à la somme de <b><i>{TOTALletter}</i></b>  {FactureObj.TTCorHT}"
            story.append(Paragraph(Money_msg,FooterMessage))
        story.append(PageBreak())

    filename = f'{FactureObj.Client.Client_Name}-{str(FactureObj.number).zfill(3)}-{Date}'
    filepath = os.path.join(BASE_DIR.parent.parent.parent,'static')+f"/PDF_FILES/{filename}.pdf"
    doc = SimpleDocTemplate(filepath, pagesize=A4, pagetitle='filename',rightMargin=43, leftMargin=43,topMargin=100, bottomMargin=23)
    doc.title = filename
    doc.author = 'E-FACTURE - Dev Team'
    doc.build(story, onFirstPage=DrawPageImages, onLaterPages=DrawPageImages)

    return filepath
