from marshmallow import Schema, fields, validate


class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer()
    first_name = fields.String(validate=[validate.Length(max=250)])
    last_name = fields.String(validate=[validate.Length(max=250)])
    username = fields.String(validate=[validate.Length(max=250)])
    debt = fields.Float()
    requested = fields.Float()
    approving = fields.Float()
    # message = fields.String(dump_only=True)
