# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from django import template
from django.contrib.contenttypes.models import ContentType

from transmittals.models import OutgoingTransmittal
from categories.models import Category


register = template.Library()


@register.simple_tag(takes_context=True)
def diffclass(context, variable):
    revision = context['revision']
    trs_revision = context['trs_revision']

    if getattr(revision, variable) != getattr(trs_revision, variable):
        return 'warning'
    else:
        return ''


@register.simple_tag
def isnew_label(trs_revision):
    if trs_revision.is_new_revision:
        label_class = 'warning'
        label_text = 'New'
    else:
        label_class = 'primary'
        label_text = 'Updated'

    return '<span class="label label-{}">{}</span>'.format(
        label_class, label_text)


@register.assignment_tag
def get_outgoing_transmittal_categories():
    """Return categories with an "OutgoingTransmittal" content type"""
    ct = ContentType.objects.get_for_model(OutgoingTransmittal)
    categories = Category.objects \
        .select_related() \
        .filter(category_template__metadata_model=ct)
    return categories
