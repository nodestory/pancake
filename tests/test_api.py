#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
import pytest
from pancake.models import EventLevels, Subscription


def test_create_contact(app):
    with app.test_client() as c:
        # create contact
        r = c.post('/contact', json={
            'user_id': '1',
            'interval': 86400,
            'notifications': 1,
        })
        assert r.status_code == 201, r.json
        contact = r.json
        # create media for contact
        r = c.post('/media', json=[{
            'type': 'email',
            'address': 'blurrcat@gmail.com',
            'contact': contact['_id']
        }, {
            'type': 'sms',
            'address': '+6584517800',
            'contact': contact['_id']
        }])
        assert r.status_code == 201, r.json
        print r.json


@pytest.mark.parametrize(
    "case,notifications,s_notifications,sub_level,event_level,event_time," +
    "notified", [
        ('contact rate limit reached -> no-notify',
         0, 10, EventLevels.OK.value, EventLevels.OK.value,
         datetime(1970, 3, 1), False),
        ('contact rate limit ok -> notify',
         1, 10, EventLevels.OK.value, EventLevels.OK.value,
         datetime(1970, 3, 1), True),
        ('subscription rate limit reached -> no-notify',
         1, 0, EventLevels.OK.value, EventLevels.OK.value,
         datetime(1970, 3, 1), False),
        ('subscription level > event level -> no notify',
         1, 10, EventLevels.CRITICAL.value, EventLevels.OK.value,
         datetime(1970, 3, 1), False),
        ('subscription level = event level -> notify',
         1, 10, EventLevels.CRITICAL.value, EventLevels.CRITICAL.value,
         datetime(1970, 3, 1), True),
        ('subscription level < event level -> notify',
         1, 10, EventLevels.OK.value, EventLevels.CRITICAL.value,
         datetime(1970, 3, 1), True),
        ('event time earlier then subscription start_time -> no notify',
         1, 10, EventLevels.OK.value, EventLevels.OK.value,
         datetime(1970, 1, 1), False),
        ('event time later than subscription end_time -> no notify',
         1, 10, EventLevels.OK.value, EventLevels.OK.value,
         datetime(1971, 1, 1), False),
    ]
)
def test_event(
    app, contact, media, subscription, notification_service, case,
    notifications, s_notifications, sub_level, event_level, event_time,
    notified,
):
    """
    Test notification rules.
    """
    contact.notifications = notifications
    contact.save()
    subscription.level = sub_level
    subscription.media = media
    subscription.limit_notifications = s_notifications
    subscription.save()
    event_json = {
        'event': subscription.event,
        'level': event_level,
        'user_id': contact.user_id,
        'time': event_time,
        'data': {
            'username': 'test'
        }
    }
    with app.test_client() as c:
        r = c.post('/event', json=event_json)
        assert r.status_code == 201, r.json
        notify_transport = getattr(
            notification_service, 'notify_%s' % media.type)
        assert notify_transport.called == notified, case
        if notified:
            assert media.address in str(notify_transport.call_args)


def test_multiple_subscription(app, contact, subscription,
                               notification_service):
    contact.notifications = 10
    contact.save()
    subscription2 = subscription
    del subscription2.id
    subscription2.save()
    assert len(Subscription.objects()) == 2
    with app.test_client() as c:
        r = c.post('/event', json={
            'event': subscription.event,
            'level': subscription.level,
            'user_id': subscription.user_id,
            'time': subscription.start_time,
        })
        assert r.status_code == 201, r.json
        # 2 subscription with the same subscriber matches
        # shall only send one notification
        assert notification_service.notify_email.call_count == 1
        assert subscription.event in str(
            notification_service.notify_email.call_args)


@pytest.mark.parametrize(
    "case,sub_s,sub_e,ack_s,ack_e,event_time,notified", [
        ('event time is in subscription but not in ack -> notify',
         5, 10, 8, 12, 6, True),
        ('event time is in both subscription and ack -> no notify',
         5, 10, 8, 12, 9, False),
    ]
)
def test_acknowledgement(
        app, subscription, acknowledgement, notification_service,
        case, sub_s, sub_e, ack_s, ack_e, event_time, notified
):
    subscription.start_time = datetime(1970, sub_s, 1)
    subscription.end_time = datetime(1970, sub_e, 1)
    subscription.save()
    acknowledgement.start_time = datetime(1970, ack_s, 1)
    acknowledgement.end_time = datetime(1970, ack_e, 1)
    acknowledgement.save()
    with app.test_client() as c:
        r = c.post('/event', json={
            'event': subscription.event,
            'level': subscription.level,
            'user_id': subscription.user_id,
            'time': datetime(1970, event_time, 1)
        })
        assert r.status_code == 201
        assert notification_service.notify_email.called == notified, case
