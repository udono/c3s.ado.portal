from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .security.request import RequestWithUserAttribute
from .security import (
    Root,
    groupfinder
)

from .models import (
    DBSession,
    Base,
)

from pyramid_beaker import session_factory_from_settings
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    session_factory = session_factory_from_settings(settings)

    authn_policy = AuthTktAuthenticationPolicy(
        's0secret!!',
        callback=groupfinder,)
    authz_policy = ACLAuthorizationPolicy()

    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings,
                          authentication_policy=authn_policy,
                          authorization_policy=authz_policy,
                          session_factory=session_factory,
                          root_factory=Root)
    # using a custom request with user information
    config.set_request_factory(RequestWithUserAttribute)

    config.include('cornice')
    config.include('pyramid_chameleon')
    config.include('pyramid_mailer')
    config.add_static_view('static', 'static', cache_max_age=3600)
    # subscriber
    config.add_subscriber(
        'c3sadoportal.subscribers.add_base_bootstrap_template',
        'pyramid.events.BeforeRender')
    config.add_subscriber('c3sadoportal.subscribers.add_locale_to_cookie',
                          'pyramid.events.NewRequest')
    # routes
    config.add_route('home', '/')
    config.add_route('login', '/login')
    config.add_route('logged_in', '/logged_in')
    config.add_route('logout', '/logout')
    config.add_route('register', '/register')
    config.scan()
    return config.make_wsgi_app()
