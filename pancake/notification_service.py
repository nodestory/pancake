#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import json
from requests import Session, HTTPError


class NotificationServiceError(Exception):
    pass


class Client(Session):
    def __init__(self, url):
        super(Client, self).__init__()
        self.url = url

    @staticmethod
    def _check_response(response):
        try:
            response.raise_for_status()
        except HTTPError as e:
            raise NotificationServiceError(e.message)

    def _resource(self, *scopes):
        urls = [self.url]
        urls.extend(scopes)
        return '/'.join(urls)

    def notify_sms(self, address, template_name, context, media_urls=None):
        if media_urls:
            # Twilio
            context['media_urls'] = media_urls
        r = self.post(
            self._resource('sms', template_name, address),
            data={
                'context': json.dumps(context)
            }
        )
        self._check_response(r)

    def notify_email(self, address, subject_template_name, txt_template_name,
                     context, html_template_name=None):
        if html_template_name:
            templates = '%s,%s' % (txt_template_name, html_template_name)
        else:
            templates = txt_template_name
        r = self.post(
            url=self._resource(
                'email', subject_template_name, templates, address),
            data={
                'context': json.dumps(context)
            }
        )
        self._check_response(r)
