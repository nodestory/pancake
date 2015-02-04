#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from mongoengine import ValidationError
import pytest
from pancake.models import Subscription


def test_subscription(contact, media, event):
    # end time earlier than start time
    s = Subscription(
        user_id='1',
        start_time=datetime(1971, 1, 1),
        end_time=datetime(1970, 1, 1),
        media=media,
        level=event.level,
        event=event.event,
    )
    with pytest.raises(ValidationError) as exc_info:
        s.save()
    assert 'end_time' in exc_info.value.message
