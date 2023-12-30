from django import template
from source import host
from function import get_role,db

register = template.Library()

@register.simple_tag
def role(request):
    try:
        return get_role(request,'role')
    except:
        return 'muslin'

@register.simple_tag
def department(request):
    return get_role(request,'department')

@register.simple_tag
def get_host():
    return host

@register.simple_tag
def test():
    return 'test'

@register.simple_tag
def send_databasename():
    res = list(db.query("select department from store_api").fetchall())
    return [i[0] for i in res]

@register.filter
def get_idsell(s:str):
    first,second = s.split('-')
    if first[1].isalpha():
        first_char = first[1:]
    else:
        first_char = first[0:]
    num_char = first_char[1:]
    num_char = str(int(num_char))
    return first_char[0] + num_char