from datetime import datetime
from flask import Blueprint
from flask_apispec import marshal_with, use_kwargs
from bank import docs
from bank.models import Application
from bank.schemas import ApplicationSchema


applications = Blueprint("applications", __name__)


@applications.route("/applications", methods=["GET"])
@marshal_with(ApplicationSchema(many=True))
def get_application_list():
    application_list = Application.get_list()
    return application_list


@applications.route("/users/<int:user_id>/applications", methods=["GET"])
@marshal_with(ApplicationSchema(many=True))
def get_user_application_list(user_id):
    application_list = Application.get_user_list(user_id)
    return application_list


@applications.route("/applications", methods=["POST"])
@marshal_with(ApplicationSchema)
@use_kwargs(ApplicationSchema(only=("user_id", "value")))
def create_application(**kwargs):
    request_date = datetime.now()
    application = Application(request_date=request_date, **kwargs)
    application.save()
    return application


@applications.route("/users/<int:user_id>/applications/<int:application_id>", methods=["PUT"])
@marshal_with(ApplicationSchema)
@use_kwargs(ApplicationSchema)
def update_application(user_id, application_id, **kwargs):
    application = Application.get(user_id, application_id)
    application.update(**kwargs)
    return application


@applications.route("/users/<int:user_id>/applications/<int:application_id>", methods=["DELETE"])
@marshal_with(ApplicationSchema)
def remove_application(user_id, application_id):
    application = Application.get(user_id, application_id)
    application.delete()
    return "", 204


docs.register(get_application_list, blueprint="applications")
docs.register(get_user_application_list, blueprint="applications")
docs.register(create_application, blueprint="applications")
docs.register(update_application, blueprint="applications")
docs.register(remove_application, blueprint="applications")
