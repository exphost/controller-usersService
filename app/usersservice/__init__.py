import os
from flask import Flask
from .dao import DAO
from . import users


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        LDAP_URI=os.environ.get("LDAP_URI", ""),
        LDAP_BASE=os.environ.get("LDAP_BASE", ""),
        LDAP_DN=os.environ.get("LDAP_DN", ""),
        LDAP_PASSWORD=os.environ.get("LDAP_PASSWORD", ""),
    )
    app.logger.info("LDAP configuration:")
    app.logger.info(" LDAP_URI="+app.config['LDAP_URI'])
    app.logger.info(" LDAP_BASE="+app.config['LDAP_BASE'])
    app.logger.info(" LDAP_DN="+app.config['LDAP_DN'])
    app.logger.info(" LDAP_PASSWORD="+str(bool(app.config['LDAP_PASSWORD'])))
    app.DAO = DAO(app)
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    @app.route('/hello')
    def hello():
        return "Hello, World!"

    app.register_blueprint(users.bp)

    return app