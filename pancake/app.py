import ast
import logging.config
import os
from eve import Eve
from eve_mongoengine import EveMongoengine
from flask.ext.admin import Admin
from pancake import config
from pancake.admin import model_views
from pancake.models import Media, Contact, Event, Subscription


def create_app(**kwargs):
    settings = get_settings(**kwargs)
    eve = Eve(__name__, settings=settings)
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


def configure_ext(app):
    ext = EveMongoengine(app)
    admin = Admin(app)
    for model_cls in (Media, Contact, Event, Subscription):
        ext.add_model(model_cls)
        model_view = getattr(model_views, '%sAdmin' % model_cls.__name__)
        admin.add_view(model_view(model_cls))
    return app


if __name__ == "__main__":
    create_app().run(debug=True, port=8080)
