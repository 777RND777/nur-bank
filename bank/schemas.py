from marshmallow import Schema, fields, validate


class ApplicationSchema(Schema):
    pk = fields.Integer(dump_only=True)
    id = fields.Integer()
    user_id = fields.Integer()
    value = fields.Integer()
    request_date = fields.String(validate=[validate.Length(max=50)])
    answer_date = fields.String(validate=[validate.Length(max=50)])
    approved = fields.Boolean()
    is_admin = fields.Boolean()
    # message = fields.String(dump_only=True)


class UserSchema(Schema):
    pk = fields.Integer(dump_only=True)
    id = fields.Integer()
    first_name = fields.String(validate=[validate.Length(max=250)])
    last_name = fields.String(validate=[validate.Length(max=250)])
    username = fields.String(validate=[validate.Length(max=250)])
    nickname = fields.String(validate=[validate.Length(max=250)])
    debt = fields.Integer()
    applications = fields.Nested(ApplicationSchema, many=True, dump_only=True)
    # message = fields.String(dump_only=True)
