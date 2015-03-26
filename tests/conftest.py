#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
import uuid
from flask import json
from flask.testing import FlaskClient
from mock import MagicMock
from pancake.app import create_app
import pytest
from pancake.models import (
    Contact, Media, Subscription, Event, EventLevels, Acknowledgement)


class APIClient(FlaskClient):
    def open(self, *args, **kwargs):
        try:
            data = kwargs.pop('json')
        except KeyError:
            pass
        else:
            kwargs['data'] = json.dumps(data)
            headers = kwargs.setdefault('headers', {})
            headers['content-type'] = 'application/json'
        r = super(APIClient, self).open(*args, **kwargs)
        r.json = json.loads(r.data)
        return r


@pytest.fixture(scope='session', autouse=True)
def app(request):
    dbname = 'pancake_test'
    application = create_app(
        TESTING=True,
        MONGO_DBNAME=dbname,
        REDIS_URL='redis://localhost/1'
    )
    application.test_client_class = APIClient
    ctx = application.app_context()
    ctx.push()
    # clear mongodb
    db = application.extensions['pymongo']['MONGO'][1]
    db.connection.drop_database(dbname)

    request.addfinalizer(ctx.pop)
    return application


def model_factory(request, o):
    o.save()
    unicode(o)
    request.addfinalizer(o.__class__.objects().delete)
    return o


@pytest.fixture
def contact(request):
    return model_factory(request, Contact(
        user_id=uuid.uuid4().hex, notifications=10, interval=20))


@pytest.fixture(params=[
    ('email', 'blurrcat@gmail.com'),
    ('sms', '+8684517800')])
def media(request, contact):
    type_, address = request.param
    return model_factory(request, Media(
        type=type_, address=address, contact=contact))


@pytest.fixture
def media_email(request, contact):
    result = Media.objects(type='email', contact=contact).first()
    if result is None:
        result = model_factory(request, Media(
            type='email', address='blurrcat@gmail.com', contact=contact
        ))

    return result


@pytest.fixture
def event(request, contact):
    return model_factory(
        request,
        Event(user_id=contact.user_id, event='test',
              level=EventLevels.WARNING.value))


@pytest.fixture
def subscription(request, contact, event, media_email):
    return model_factory(
        request,
        Subscription(
            user_id=contact.user_id, event=event.event, level=event.level,
            media=media_email, start_time=datetime(1970, 2, 1),
            end_time=datetime(1970, 10, 1), limit_interval=1,
            limit_notifications=10))


@pytest.fixture
def acknowledgement(request, contact, event, media_email):
    return model_factory(
        request,
        Acknowledgement(
            user_id=contact.user_id, event=event.event, level=event.level,
            media=media_email, start_time=datetime(1970, 3, 1),
            end_time=datetime(1970, 5, 1),
        )
    )


@pytest.fixture
def notification_service(monkeypatch, app):
    ns = MagicMock()
    monkeypatch.setitem(app.extensions, 'notification_service', ns)
    return ns
