from django import template

register = template.Library()


@register.filter
def slice_url(value, position):
    group = value.split('/')
    while '' in group:
        group.remove('')
    return group[position]


@register.filter
def replace_url(value, pair):
    pair_slice = pair.split(',')
    value = str(value)
    print(value.replace('statistics', 'review'))
    new = value.replace(pair_slice[0], pair_slice[1])
    return new


@register.filter
def slice_filepath(value, position):
    value = str(value)
    group = value.split('/')
    while '' in group:
        group.remove('')
    return group[position]


@register.filter
def count_dict(value):
    length = len(value)
    return length


@register.filter
def count_grade(value, num):
    count = 0
    for grade in value:
        if grade['grade'] == num:
            count += 1
    return count
