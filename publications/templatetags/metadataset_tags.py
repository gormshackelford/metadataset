from django import template
from ..models import Subject

register = template.Library()

@register.simple_tag
def get_subjects():
    subjects = Subject.objects.all()
    return subjects
