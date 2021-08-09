from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask import Flask
from flask_apispec.extension import FlaskApiSpec
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
app.config.update({
    "APISPEC_SPEC": APISpec(title="bank",
                            version="v1",
                            openapi_version="2.0",
                            plugins=[MarshmallowPlugin()]),
    "APISPEC_SWAGGER_URL": "/swagger/"
})

docs = FlaskApiSpec()

client = app.test_client()

engine = create_engine("sqlite:///bank/db.sqlite")
session = scoped_session(sessionmaker(autocommit=False,
                                      autoflush=False,
                                      bind=engine))

Base = declarative_base()
Base.query = session.query_property()
# importing here because of circular import error

Base.metadata.create_all(bind=engine)

# place for future

# importing here because of circular import error
from .applications.views import applications
from .users.views import users

app.register_blueprint(applications)
app.register_blueprint(users)

# setting here to include blueprints
docs.init_app(app)
