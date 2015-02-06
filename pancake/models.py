#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from enum import Enum
from eve.methods.common import RateLimit
from mongoengine import Document, CASCADE, ValidationError
from mongoengine.fields import *
from pancake.misc import get_enum_choices, get_enum_values


__all__ = [
    'MediaTypes', 'EventLevels', 'Media', 'Contact', 'Event', 'Subscription',
    'Acknowledgement',
]


class MediaTypes(Enum):
    EMAIL = 'email'
    SMS = 'sms'


class EventLevels(Enum):
    UNKNOWN = 1
    OK = 2
    WARNING = 3
    CRITICAL = 4


class ResourceMixin(object):
    resource_methods = ['GET', 'POST']
    item_methods = ['GET', 'PATCH']


class Media(Document, ResourceMixin):
    address = StringField(required=True, help_text='address of the media')
    type = StringField(choices=get_enum_values(MediaTypes))
    contact = ReferenceField('Contact', help_text='owner of the media')

    meta = {
        'indexes': [
            'contact',
        ]
    }

    def __unicode__(self):
        return u'%s:%s' % (self.type, self.address)


class Contact(Document, ResourceMixin):
    """
    Represents an external user. Also bears user notification preference.
    """
    user_id = StringField(unique=True, required=True,
                          help_text='id of the external user')
    interval = IntField(
        default=86400,
        help_text='at most send n notifications in `interval` seconds. '
                  'Default to 1 day')
    notifications = IntField(default=0, help_text='send nothing by default')

    meta = {
        'indexes': [
            'user_id',
        ]
    }

    def rate_limit_reached(self):
        key = 'rl:%s' % self.user_id
        limit = RateLimit(key, self.notifications, self.interval, False)
        return limit.over_limit

    def __unicode__(self):
        return unicode(self.user_id)


class Event(Document, ResourceMixin):
    """
    represents an occurrence of an event to a user
    """
    user_id = StringField(required=True)
    event = StringField(required=True)
    level = IntField(choices=get_enum_values(EventLevels), required=True)
    time = DateTimeField(default=datetime.now)
    data = DictField(help_text="used when rendering notification content")

    def __unicode__(self):
        return u'event %s.%s.%s[data: %s]' % (
            self.user_id, self.event, self.level, self.data)


class Subscription(Document, ResourceMixin):
    """
    Subscribe to a user's event.

    Upon a new event, send a notification if all of the following meet:
     * event.event == subscription.event
     * event.level >= subscription.level
     * event.time >= subscription.start_time
     * event.time < subscription.end_time if subscription.end_time
     * rate limit of the subscriber is not reached

    If an event triggers multiple subscriptions, only one notification is
    sent per media type.
    """
    item_methods = ['GET', 'PATCH', 'DELETE']
    user_id = StringField(required=True)
    event = StringField(required=True, help_text='a event name or "*"')
    level = IntField(
        required=True, choices=get_enum_values(EventLevels),
        help_text="matches events with `level` and above.")
    media = ReferenceField(Media, required=True)
    start_time = DateTimeField(required=True)
    end_time = DateTimeField()

    meta = {
        'indexes': [
            ('user_id', 'event', 'level', 'start_time', 'end_time'),
        ],
    }

    def save(self, force_insert=False, validate=True, clean=True,
             write_concern=None,  cascade=None, cascade_kwargs=None,
             _refs=None, **kwargs):
        if not self.end_time:
            self.end_time = self.start_time + timedelta(days=365000)  # 100 y
        return super(Subscription, self).save(
            force_insert, validate, clean, write_concern, cascade,
            cascade_kwargs, _refs, **kwargs)

    def __unicode__(self):
        return "%s subscribes to %s.%s.%s" % (
            self.media, self.user_id, self.event, self.level)


class Acknowledgement(Document, ResourceMixin):
    """
    If an event of interest triggered during a subscriber's acknowledgement,
    no notification is sent, like a blacklist.

    The acknowledgement is effective from `start_time` to `end_time`.
    """
    item_methods = ['GET', 'PATCH', 'DELETE']

    user_id = StringField(required=True)
    start_time = DateTimeField(required=True)
    end_time = DateTimeField()
    event = StringField(required=True)
    level = IntField(required=True)

    def save(self, force_insert=False, validate=True, clean=True,
             write_concern=None,  cascade=None, cascade_kwargs=None,
             _refs=None, **kwargs):
        if not self.end_time:
            self.end_time = self.start_time + timedelta(days=365000)
        return super(Acknowledgement, self).save(
            force_insert, validate, clean, write_concern, cascade,
            cascade_kwargs, _refs, **kwargs)
