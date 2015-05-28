#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask.ext.admin.contrib.mongoengine import ModelView
from gettext import gettext
from flask_admin.contrib.mongoengine.filters import BaseMongoEngineFilter
from flask_admin.contrib.mongoengine.tools import parse_like_term
from pancake.misc import get_enum_choices
from pancake.models import MediaTypes, Contact, Media


class ContactLikeFilter(BaseMongoEngineFilter):
    def __init__(self, filter_column, reference_column, name, options=None, data_type=None):
        super(ContactLikeFilter, self).__init__(filter_column, name, options, data_type)
        self.reference_column = reference_column

    def apply(self, query, value):
        term, data = parse_like_term(value)

        flt = {}
        if self.column.name == Contact.id.name:
            flt = {'%s__%s' % (Contact.user_id.name, term): data}

            data = Contact.objects().filter(**flt).only('id').first()

            if data is not None:
                flt = {self.reference_column.name: data.id}
        return query.filter(**flt)

    def operation(self):
        return gettext('like')

    def validate(self, value):
        return True

    def clean(self, value):
        return value


def user_filter(reference_column):
    contacts = []
    results = []#Contact.objects().distinct(field="user_id")
    for result in results:
        contacts.append((result, result))
    return ContactLikeFilter(Contact.id, reference_column, 'Contact', options=contacts)


class MediaAdmin(ModelView):
    column_display_pk = True
    #column_searchable_list = ('address')
    form_args = {
        'type': {
            'choices': get_enum_choices(MediaTypes)
        }
    }
    column_filters = [
        user_filter(Media.contact)
    ]


class ContactAdmin(ModelView):
    column_display_pk = True
    column_searchable_list = ('user_id', 'alias')
    column_filters = [
        user_filter(Contact.id)
    ]



class EventAdmin(ModelView):
    column_searchable_list = ('user_id', 'event')
    form_args = {
        'level': {
            # 'coerce': int,
            # 'choices': get_enum_choices(EventLevels)
        }
    }


class SubscriptionAdmin(ModelView):
    column_searchable_list = ('user_id', 'event')


class AcknowledgementAdmin(ModelView):
    column_searchable_list = ('user_id', 'event')
