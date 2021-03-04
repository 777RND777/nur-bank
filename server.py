from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask import Flask
from flask_apispec import marshal_with, use_kwargs
from flask_apispec.extension import FlaskApiSpec
from schemas import UserSchema
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
import sqlalchemy as db


app = Flask(__name__)
# app.config.update({
#     "APISPEC_SPEC": APISpec(title="bank",
#                             version="v1",
#                             openapi_version="2.0",
#                             plugins=[MarshmallowPlugin()]),
#     "APISPEC_SWAGGER_URL": "/swagger/"
# })
# docs = FlaskApiSpec()

client = app.test_client()

engine = create_engine("sqlite:///db.sqlite")
session = scoped_session(sessionmaker(autocommit=False,
                                      autoflush=False,
                                      bind=engine))

Base = declarative_base()
Base.query = session.query_property()
# importing here because of circular import error
from models import *
Base.metadata.create_all(bind=engine)


@app.route("/users", methods=["GET"])
@marshal_with(UserSchema(many=True))
def get_user_list():
    users = User.get_list()
    return users


@app.route("/users/<int:user_id>", methods=["GET"])
@marshal_with(UserSchema)
def get_user(user_id):
    user = User.get(user_id)
    return user


@app.route("/users", methods=["POST"])
@marshal_with(UserSchema)
@use_kwargs(UserSchema(only=("user_id", "first_name", "last_name")))
def add_user(**kwargs):
    user = User(**kwargs)
    user.save()
    return user


@app.route("/users/<int:user_id>", methods=["PUT"])
@marshal_with(UserSchema)
@use_kwargs(UserSchema)
def update_user(user_id, **kwargs):
    user = User.get(user_id)
    user.update(**kwargs)
    return user


@app.route("/users/<int:user_id>", methods=["DELETE"])
@marshal_with(UserSchema)
def remove_user(user_id):
    user = User.get(user_id)
    user.delete()
    return "", 204
