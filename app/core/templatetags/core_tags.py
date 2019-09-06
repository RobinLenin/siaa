"""
Tags a ser incluidos a nivel global
"""
from django import template
from django.apps import apps

register = template.Library()

@register.filter
def verbose_name(clase):
    model = apps.get_model(clase)
    return model._meta.verbose_name


@register.filter
def verbose_name_plural(clase):
    model = apps.get_model(clase)
    return model._meta.verbose_name_plural