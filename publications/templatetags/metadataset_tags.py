from django import template
from django.contrib.auth.models import Group
from django.db.models import Q
from ..models import Subject, UserSubject

register = template.Library()

@register.simple_tag
def public_subjects():
    subjects = Subject.objects.filter(is_public=True)
    return subjects

@register.simple_tag
def user_subjects(user):
    user_subjects = UserSubject.objects.filter(user=user)
    subjects = Subject.objects.filter(
        Q(usersubject__in=user_subjects) |
        Q(is_public=True)
    ).distinct()
    return subjects

@register.simple_tag
def user_subject(user, subject):
    return UserSubject.objects.filter(user=user, subject=subject).exists()

@register.simple_tag
def data_are_public(subject):
    return subject.data_are_public

@register.filter(name='add_class')
def add_class(field, class_name):
    return field.as_widget(attrs={"class": class_name})

@register.filter(name='is_in_group')
def is_in_group(user, group_name):
    return user.groups.filter(name=group_name).exists()
