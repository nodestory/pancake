#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import timedelta
from flask import current_app
from pancake.models import Subscription, Contact


def _event_context(event):
    data = event.pop('data', {})
    event.update(data)
    return event


def on_inserted_event(items):
    for event in items:
        subscriptions = Subscription.objects(
            user_id=event['user_id'],
            event=event['event'],
            level__lte=event['level'],
            start_time__lte=event['time'],
        )
        for s in subscriptions:
            end_time = s.end_time or event['time'] + timedelta(seconds=1)
            # the rule applies if end_time is not set
            if event['time'] < end_time:
                subscriber = s.media.contact
                if subscriber.rate_limit_reached():
                    current_app.logger.info(
                        'notification for contact %s muted because rate ' +
                        'limit reached: %d in %dsec',
                        subscriber, subscriber.notifications,
                        subscriber.interval)
                    continue
                ns = current_app.extensions['notification_service']
                context = _event_context(event)
                name = event['event']
                if s.media.type == 'email':
                    ns.notify_email(
                        address=s.media.address,
                        subject_template_name='%s.subject' % name,
                        txt_template_name='%s.txt' % name,
                        html_template_name='%s.html' % name,
                        context=context
                    )
                    current_app.logger.info(
                        'Notified %s via %s on %s', subscriber, s.media, event)
                elif s.media.type == 'sms':
                    ns.notify_sms(
                        address=s.media.address,
                        template_name='%s.sms' % name,
                        context=context
                    )
                    current_app.logger.info(
                        'Notified %s via %s on %s', subscriber, s.media, event)
                else:
                    current_app.logger.error(
                        'unexpected media type: %s', s.media.type)
