import ast
import logging.config
import os
from eve import Eve
from eve_docs import eve_docs
from eve_mongoengine import EveMongoengine
from flask.ext.admin import Admin
from flask.ext.bootstrap import Bootstrap
from redis import StrictRedis
from pancake import config
from pancake.admin import model_views
from pancake.handlers import on_inserted_event
from pancake.models import Media, Contact, Event, Subscription
from pancake.notification_service import Client


def _get_ext_settings(settings, prefix):
    return {k.lstrip(prefix).lstrip('_'): v
            for k, v in settings.items() if k.startswith(prefix)}


def create_app(**kwargs):
    settings = get_settings(**kwargs)
    eve = Eve(__name__, settings=settings)
    eve = configure_hooks(eve)
    eve = configure_ext(eve)
    return eve


def get_settings(**kwargs):
    """
    Configuration priority(high -> low): config.py, kwargs, os env vars
    """
    settings = {}
    for key in dir(config):
        if key.isupper():
            settings[key] = getattr(config, key)
    settings.update(kwargs)
    # production config via env vars
    prefix = 'PANCAKE_'
    for k, v in os.environ.items():
        if k.startswith(prefix):
            try:
                v = ast.literal_eval(v)
            except (ValueError, SyntaxError):
                pass
            settings[k[len(prefix):]] = v
    # logging config
    logging_config = settings.get('LOGGING_CONFIG')
    if logging_config:
        logging.config.dictConfig(logging_config)
    return settings


def configure_hooks(app):
    app.on_inserted_event += on_inserted_event
    return app


def configure_ext(app):
    ext = EveMongoengine(app)
    admin = Admin(app)
    for model_cls in (Media, Contact, Event, Subscription):
        ext.add_model(
            model_cls,
            resource_methods=model_cls.resource_methods,
            item_methods=model_cls.item_methods)
        model_view = getattr(model_views, '%sAdmin' % model_cls.__name__)
        admin.add_view(model_view(model_cls))
    # configure redis for eve rate limit
    redis_settings = _get_ext_settings(app.settings, 'REDIS')
    redis_url = redis_settings.pop('URL')
    redis = StrictRedis.from_url(redis_url, **redis_settings)
    app.redis = redis
    # notification service
    ns = Client(app.settings['NOTIFICATION_API_URL'])
    app.extensions['notification_service'] = ns
    # docs
    Bootstrap(app)
    app.register_blueprint(eve_docs, url_prefix='/docs')
    return app


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 2:
        port = int(sys.argv[1])
    else:
        port = 8080
    create_app().run(debug=True, port=port)
