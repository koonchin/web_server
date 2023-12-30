from django import template

register = template.Library()

@register.simple_tag
def get_idsell(s:str):
    first,second = s.split('-')
    if first[1].isalpha():
        first_char = first[1:]
    else:
        first_char = first[0:]
    num_char = first_char[1:]
    num_char = str(int(num_char))
    return first_char[0] + num_char