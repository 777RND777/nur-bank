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


@applications.route("/applications", methods=["POST"])
@marshal_with(ApplicationSchema)
@use_kwargs(ApplicationSchema(only=("user_id", "value")))
def create_application(**kwargs):
    request_date = datetime.now()
    application = Application(request_date=request_date, **kwargs)
    application.save()
    return application


# @applications.route("/users", methods=["POST"])
# @marshal_with(ApplicationSchema)
# @use_kwargs(ApplicationSchema(only=("user_id", "first_name", "last_name")))
# def create_user(**kwargs):
#     user = User(**kwargs)
#     user.save()
#     return user
#
#
# @applications.route("/users/<int:user_id>", methods=["PUT"])
# @marshal_with(ApplicationSchema)
# @use_kwargs(ApplicationSchema)
# def update_user(user_id, **kwargs):
#     user = User.get(user_id)
#     user.update(**kwargs)
#     return user
#
#
# @applications.route("/users/<int:user_id>", methods=["DELETE"])
# @marshal_with(ApplicationSchema)
# def remove_user(user_id):
#     user = User.get(user_id)
#     user.delete()
#     return "", 204
#
#
# docs.register(get_user_list, blueprint="users")
# docs.register(get_user, blueprint="users")
# docs.register(create_user, blueprint="users")
# docs.register(update_user, blueprint="users")
# docs.register(remove_user, blueprint="users")
