#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import defaultdict
from flask import current_app
from mongoengine import Q
from pancake.models import Subscription, Acknowledgement
from pancake.notification_service import NotificationServiceError


def _event_context(event):
    e = {
        'event': event['event'],
        'level': event['level'],
        'time': event['time'],
        'user_id': event['user_id']
    }
    if 'data' in event:
        e.update(event['data'])
    return e


def _notify(event, subscriber, media_address, media_type):
    ns = current_app.extensions['notification_service']
    context = _event_context(event)
    event_name = event['event']
    if media_type == 'email':
        try:
            ns.notify_email(
                address=media_address,
                subject_template_name='%s.subject' % event_name,
                txt_template_name='%s.txt' % event_name,
                html_template_name='%s.html' % event_name,
                context=context
            )
        except NotificationServiceError as e:
            current_app.logger.error(
                'Fail to send email notification: %s', e, exc_info=True
            )
        else:
            current_app.logger.info(
                'Notified %s via %s:%s on event[%s]',
                subscriber, media_type, media_address, event)
    elif media_type == 'sms':
        try:
            ns.notify_sms(
                address=media_address,
                template_name='%s.sms' % event_name,
                context=context
            )
        except NotificationServiceError as e:
            current_app.logger.error(
                'Fail to send sms notification: %s', e, exc_info=True
            )
        else:
            current_app.logger.info(
                'Notified %s via %s:%s on event[%s]',
                subscriber, media_type, media_address, event)
    else:
        current_app.logger.error(
            'unexpected media type: %s', media_type)


def on_inserted_event(items):
    for event in items:
        notifications = set()
        # handle subscriptions
        subscriptions = Subscription.objects(
            (Q(event=event['event']) | Q(event='*')) & Q(
                user_id=event['user_id'], level__lte=event['level'],
                start_time__lte=event['time'], end_time__gt=event['time'])
        ).order_by('-start_time')
        current_app.logger.info(
            'found %d subscriptions for event %s', len(subscriptions), event)
        # group subscriptions by subscribers
        subs_by_subscriber = defaultdict(list)
        for s in subscriptions:
            subscriber = s.media.contact
            if s.rate_limit_reached():
                current_app.logger.info(
                    'notification for contact %s muted because subscription ' +
                    'level rate limit reached: %d in %dsec',
                    subscriber, s.limit_notifications, s.limit_interval
                )
                continue
            if subscriber.rate_limit_reached():
                current_app.logger.info(
                    'notification for contact %s muted because contact ' +
                    'level rate limit reached: %d in %dsec',
                    subscriber, subscriber.notifications,
                    subscriber.interval)
                continue
            subs_by_subscriber[subscriber.user_id].append(s)
        # check if subscriber has acknowledged the event
        for user_id, subscriptions in subs_by_subscriber.iteritems():
            acknowledge = Acknowledgement.objects(
                (Q(event=event['event']) | Q(event='*')) & Q(
                    user_id=user_id, level__lte=event['level'],
                    start_time__lte=event['time'], end_time__gt=event['time'])
            ).first()
            if not acknowledge:  # not acknowledged
                for s in subscriptions:
                    # ensure only one notification is sent via a media
                    # for an event of a user
                    notifications.add((
                        event['event'], user_id, s.media.address, s.media.type
                    ))
                    current_app.logger.info(
                        'add %s of %s to notification list via %s',
                        event['event'], user_id, s.media)
        for n in notifications:
            _notify(event, *n[1:])
