from marshmallow import Schema, fields, validate, validates, ValidationError


class RegisterSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    password = fields.Str(required=True, validate=validate.Length(min=6, max=128), load_only=True)
    email = fields.Email(required=True)


class LoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class ChangePasswordSchema(Schema):
    old_password = fields.Str(required=True, load_only=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=6, max=128), load_only=True)
