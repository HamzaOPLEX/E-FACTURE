from reportlab.platypus import Table, TableStyle
from colour import Color
from pathlib import Path
from reportlab.lib import colors
from efacture.models import APP_Settings


BASE_DIR = Path(__file__).resolve().parent
GLOBAL_CONFIG_PATH = str(str(BASE_DIR.parent)+"/global_config/")
Table_Color = Color(APP_Settings.objects.all().first().Invoice_Color)
Table_Color = Table_Color.rgb


def footer_info_table(tabledata):
    colwidths = (238, 140, 180)
    t = Table(tabledata, colwidths)
    t.hAlign = 'CENTER'
    GRID_STYLE = TableStyle(
        [
            ('ALIGN', (0, 0), (-1, -1), 'CENTER')
        ]
    )
    t.setStyle(GRID_STYLE)
    return t

def Status_Table(tabledata):
    colwidths = (105, 100)
    t = Table(tabledata, colwidths)
    t.hAlign = 'LEFT'
    GRID_STYLE = TableStyle(
        [('GRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ]
    )
    t.setStyle(GRID_STYLE)
    return t






def Info_Table(tabledata):
    colwidths = (210, 100, 200)
    t = Table(tabledata, colwidths)
    t.hAlign = 'CENTER'
    GRID_STYLE = TableStyle(
        [
            ('ALIGN', (0, 0), (-1, -1), 'CENTER')
        ]
    )
    t.setStyle(GRID_STYLE)
    return t
from reportlab.lib.units import mm

def TOTAL_table(tabledata):
    colwidths = (60, 60)
    t = Table(tabledata, colwidths)
    t.hAlign = 'RIGHT'
    GRID_STYLE = TableStyle(
        [('GRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ]
    )
    t.setStyle(GRID_STYLE)
    return t

# - End TOTAL,TVA,TTC Table Handler - ################################################
def DrawPageImages(canvas, doc):
    canvas.saveState()
    canvas.drawImage(GLOBAL_CONFIG_PATH+"invoice-bg.png", 0, 0, 600, 840)
    canvas.setFont("Helvetica", 10)
    canvas.drawRightString(205*mm, 5*mm, 'Page '+str(canvas.getPageNumber()))
    canvas.restoreState()
#create the table for our document
def myTable(tabledata,innergrid_index):
    colwidths = (40, 350, 60, 60)
    t = Table(tabledata, colwidths)
    t.hAlign = 'RIGHT'
    GRID_STYLE = TableStyle(
        [
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONT', (0, 0), (-1, -1), 'Arabic'),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('LINEBEFORE', (0, 1), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), Table_Color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('INNERGRID', (0, 0), (-1, innergrid_index+1), 0.25, colors.black),
        ]
    )
    t.setStyle(GRID_STYLE)
    return t