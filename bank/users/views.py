from flask import Blueprint
from flask_apispec import marshal_with, use_kwargs
from bank import docs
from bank.models import User
from bank.schemas import UserSchema

users = Blueprint("users", __name__)


@users.route("/users", methods=["GET"])
@marshal_with(UserSchema(many=True))
def get_user_list() -> list:
    user_list = User.get_list()
    return user_list


@users.route("/users/<int:user_id>", methods=["GET"])
@marshal_with(UserSchema)
def get_user(user_id: int):
    user = User.get(user_id)
    return user


@users.route("/users", methods=["POST"])
@marshal_with(UserSchema)
@use_kwargs(UserSchema(only=("id", "first_name", "last_name", "username")))
def create_user(**kwargs):
    user = User(**kwargs)
    user.save()
    return user


@users.route("/users/<int:user_id>", methods=["PUT"])
@marshal_with(UserSchema)
@use_kwargs(UserSchema)
def update_user(user_id: int, **kwargs):
    user = User.get(user_id)
    user.update(**kwargs)
    return user


@users.route("/users/<int:user_id>", methods=["DELETE"])
@marshal_with(UserSchema)
def remove_user(user_id: int) -> (str, int):
    user = User.get(user_id)
    user.delete()
    return "", 204


docs.register(get_user_list, blueprint="users")
docs.register(get_user, blueprint="users")
docs.register(create_user, blueprint="users")
docs.register(update_user, blueprint="users")
docs.register(remove_user, blueprint="users")
