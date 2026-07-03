from marshmallow import Schema, fields, validate


class ClassroomCreateSchema(Schema):
    room_no = fields.Str(required=True, validate=validate.Length(max=50))
    floor = fields.Int(required=True, validate=validate.Range(min=1))
    capacity = fields.Int(required=True, validate=validate.Range(min=1))
    has_projector = fields.Int(load_default=0, validate=validate.OneOf([0, 1]))
    has_whiteboard = fields.Int(load_default=0, validate=validate.OneOf([0, 1]))
    facility_remark = fields.Str(allow_none=True)


class ClassroomUpdateSchema(Schema):
    room_no = fields.Str(validate=validate.Length(max=50))
    floor = fields.Int(validate=validate.Range(min=1))
    capacity = fields.Int(validate=validate.Range(min=1))
    has_projector = fields.Int(validate=validate.OneOf([0, 1]))
    has_whiteboard = fields.Int(validate=validate.OneOf([0, 1]))
    facility_remark = fields.Str(allow_none=True)
    status = fields.Int(validate=validate.OneOf([0, 1]))


class FreeClassroomQuerySchema(Schema):
    reserve_date = fields.Date(required=True)
    start_time = fields.Time(required=True)
    end_time = fields.Time(required=True)
    min_capacity = fields.Int(validate=validate.Range(min=1))
    has_projector = fields.Int(validate=validate.OneOf([0, 1]))
    has_whiteboard = fields.Int(validate=validate.OneOf([0, 1]))
