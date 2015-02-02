#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from mongoengine import Document, CASCADE, ValidationError
from mongoengine.fields import *


__all__ = [
    'MEDIA_TYPES', 'EVENT_LEVELS', 'Media', 'Contact', 'Event', 'Subscription',
]

MEDIA_TYPES = ['email', 'sms']
EVENT_LEVELS = ('0-unknown', '1-ok', '2-warning', '3-critical')



class Media(Document):
    address = StringField(required=True)
    type = StringField(choices=MEDIA_TYPES)
    contact = ReferenceField('Contact')

    def __unicode__(self):
        return u'%s:%s' % (self.type, self.address)


class Contact(Document):
    user_id = StringField(unique=True, required=True)
    media = ListField(ReferenceField(Media))
    interval = IntField(
        default=86400,
        help_text='at most send n notifications in `interval` seconds. '
                  'Default to 1 day')
    notifications = IntField(default=0, help_text='send nothing by default')

    def __unicode__(self):
        return unicode(self.user_id)


class Event(Document):
    """
    represents an occurrence of an event to a user
    """
    contact = ReferenceField(Contact, required=True)
    event = StringField(required=True)
    level = StringField(choices=EVENT_LEVELS, required=True)
    time = DateTimeField(default=datetime.now)
    data = DictField(help_text="used when rendering notification content")

    def __unicode__(self):
        return u'event %s of %s is %s; data: %s' % (
            self.event, self.contact, self.level, self.data)


class Subscription(Document):
    """
    For `contact`, On `level` of `event`, between `start_time` and `end_time`,
    notify `subscriber` via `media`
    """
    contact = ReferenceField(Contact, required=True,
                             reverse_delete_rule=CASCADE)
    event = StringField(required=True, help_text='a event name or "*"')
    level = StringField(
        required=True, choices=EVENT_LEVELS,
        help_text="matches events with `level` and above.")
    media = ReferenceField(Media, required=True)
    start_time = DateTimeField(required=True)
    end_time = DateTimeField()
    subscriber = ReferenceField(Contact, required=True)

    def validate(self, clean=True):
        super(Subscription, self).validate(clean)
        if self.end_time <= self.start_time:
            raise ValidationError(
                "Subscription ValidationError", errors={
                    'end_time': ValidationError(
                        'end_time must be later than start_time')
                })

    def __unicode__(self):
        return "%s subscribes to %s.%s.%s via %s" % (
            self.subscriber, self.contact, self.event, self.level, self.media
        )
