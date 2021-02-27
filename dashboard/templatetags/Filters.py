from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def CreateTableBody(tablebody):
    alltr_tags = []
    for data in tablebody:
        tr_tag = '<tr>here</tr>'
        for k, v in data.items():
            if k == 'DT':
                td_tag = f'<td>{v}</td>\nhere'
            else:
                td_tag = f'<td>{v}</td>\nhere'            
            tr_tag = tr_tag.replace('here', td_tag)
        tr_tag = tr_tag.replace('here', '')
        alltr_tags.append(tr_tag.strip())
    return mark_safe('\n'.join(alltr_tags))


@register.filter
def CreateTableBody_FactureItems(tablebody):
    alltr_tags = []
    for data in tablebody:
        tr_tag = '<tr>here</tr>'
        for k, v in data.items():
            if k == 'Action':
                td_tag = f'<td style="text-align:center;">{v}</td>\nhere'
            else:
                td_tag = f'<td>{v}</td>\nhere'

            tr_tag = tr_tag.replace('here', td_tag)
        tr_tag = tr_tag.replace('here', '')
        alltr_tags.append(tr_tag.strip())
    return mark_safe('\n'.join(alltr_tags))


@register.filter
def CreateHTMLSelectOptions(selectbody):
    body = []
    body.append('<option value="-">-</option>')
    for i in selectbody:
        option_tag = f'<option value="{i}">{i}</option>'
        body.append(option_tag)
    return mark_safe('\n'.join(body))


@register.filter
def CreateHTMLSelectOptionsWith_ID(selectbody):
    body = []
    body.append('<option value="-">-</option>')
    for i in selectbody:
        option_tag = f'<option value="{i[1]}">{i[0]}</option>'
        body.append(option_tag)
    return mark_safe('\n'.join(body))
