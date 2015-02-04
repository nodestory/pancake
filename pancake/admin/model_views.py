#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask.ext.admin.contrib.mongoengine import ModelView
from pancake.misc import get_enum_choices
from pancake.models import EventLevels, MediaTypes


class MediaAdmin(ModelView):
    form_args = {
        'type': {
            'choices': get_enum_choices(MediaTypes)
        }
    }


class ContactAdmin(ModelView):
    pass


class EventAdmin(ModelView):
    form_args = {
        'level': {
            # 'coerce': int,
            # 'choices': get_enum_choices(EventLevels)
        }
    }


class SubscriptionAdmin(ModelView):
    pass
