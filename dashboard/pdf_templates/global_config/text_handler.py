from num2words import num2words
import textwrap
import arabic_reshaper
from bidi.algorithm import get_display


def chunks(l, n):
    n = max(1, n)
    return (l[i:i+n] for i in range(0, len(l), n))

def ReshapeArabic(txt):
    txt = arabic_reshaper.reshape(txt)
    txt = get_display(txt)
    return txt

def draw_wrapped_line(canvas, text, length, x_pos, y_pos, y_offset):
    if len(text) > length:
        wraps = textwrap.wrap(text, length)
        for x in range(len(wraps)):
            canvas.drawCentredString(x_pos, y_pos, wraps[x])
            y_pos -= y_offset
        y_pos += y_offset  # add back offset after last wrapped line
    else:
        canvas.drawCentredString(x_pos, y_pos, text)
    return y_pos

def Number2Letter(number):
    if ',' in str(number):
        number = number.replace(',', '')
    elif '.' in str(number):
        number = round(float(number), 2)
        number = str(number).split('.')
        # Befor point
        part01 = str(num2words(int(number[0]), lang='fr')+' Dirhams')
        # After point
        part02 = str(num2words(int(number[1]), lang='fr')+' Centimes')

        if int(number[1]) == 0 :
            allNumber_Parts = part01
        elif int(number[1]) != 0 :
            allNumber_Parts = part01 +' Et '+ part02
        
        return allNumber_Parts.title()
    else:
        number = num2words(int(number), lang='fr')+' Dirhams'
        return number.title()