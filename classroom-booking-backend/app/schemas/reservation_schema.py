from marshmallow import Schema, fields, validate


class ReservationCreateSchema(Schema):
    classroom_id = fields.Int(required=True)
    reserve_date = fields.Date(required=True)
    start_time = fields.Time(required=True)
    end_time = fields.Time(required=True)
    purpose = fields.Str(required=True, validate=validate.Length(max=255))


class ReservationUpdateSchema(Schema):
    classroom_id = fields.Int()
    reserve_date = fields.Date()
    start_time = fields.Time()
    end_time = fields.Time()
    purpose = fields.Str(validate=validate.Length(max=255))


class ApprovalSchema(Schema):
    result = fields.Int(required=True, validate=validate.OneOf([1, 2]))
    opinion = fields.Str(allow_none=True)


class PeriodicRuleSchema(Schema):
    classroom_id = fields.Int(required=True)
    weekday = fields.Int(required=True, validate=validate.Range(min=1, max=7))
    start_time = fields.Time(required=True)
    end_time = fields.Time(required=True)
    purpose = fields.Str(required=True, validate=validate.Length(max=255))
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
