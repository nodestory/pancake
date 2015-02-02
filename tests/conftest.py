#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pancake.app import create_app
import pytest


@pytest.fixture(scope='session')
def app(request):
    application = create_app({
        'TESTING': True,
    })
    ctx = application.app_context()
    ctx.push()

    def clean():
        ctx.pop()

    request.addfinalizer(clean)
    return application