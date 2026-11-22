#!/usr/bin/env python3

from flask import Flask, make_response
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models import db
from routes import api

migrate = Migrate()


def register_error_handlers(app):
    # Schema validation failures: field-by-field messages from Marshmallow
    @app.errorhandler(ValidationError)
    def handle_schema_error(error):
        return make_response({'errors': error.messages}, 400)

    # Model validation failures raised by @validates
    @app.errorhandler(ValueError)
    def handle_model_error(error):
        db.session.rollback()
        return make_response({'errors': [str(error)]}, 400)

    # Table constraint failures (unique, check, not null)
    @app.errorhandler(IntegrityError)
    def handle_constraint_error(error):
        db.session.rollback()
        return make_response({'errors': [str(error.orig)]}, 400)


def create_app(config=None):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.json.compact = False
    if config:
        app.config.update(config)

    db.init_app(app)
    migrate.init_app(app, db)
    app.register_blueprint(api)
    register_error_handlers(app)

    return app


app = create_app()

if __name__ == '__main__':
    app.run(port=5555, debug=True)
