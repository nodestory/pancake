#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask.ext.admin.contrib.mongoengine import ModelView


class MediaAdmin(ModelView):
    pass


class ContactAdmin(ModelView):
    pass


class EventAdmin(ModelView):
    pass


class SubscriptionAdmin(ModelView):
    pass
