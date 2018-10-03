from django import template
from django.contrib.auth.models import Group
from ..models import Subject

register = template.Library()

@register.simple_tag
def get_subjects():
    subjects = Subject.objects.all()
    return subjects

@register.filter(name='add_class')
def add_class(field, class_name):
    return field.as_widget(attrs={"class": class_name})

@register.filter(name='is_in_group')
def is_in_group(user, group_name):
    return user.groups.filter(name=group_name).exists()
