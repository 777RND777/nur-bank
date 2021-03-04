from marshmallow import Schema, fields, validate


class ApplicationSchema(Schema):
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(dump_only=True)
    value = fields.Float()
    request_date = fields.Date()
    answer_date = fields.Date()
    approved = fields.Boolean()


class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer()
    first_name = fields.String(validate=[validate.Length(max=250)])
    last_name = fields.String(validate=[validate.Length(max=250)])
    username = fields.String(validate=[validate.Length(max=250)])
    debt = fields.Float()
    applications = fields.Nested(ApplicationSchema, many=True, dump_only=True)
    # message = fields.String(dump_only=True)
