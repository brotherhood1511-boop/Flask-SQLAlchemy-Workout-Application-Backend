from marshmallow import Schema, fields, validate, validates_schema, ValidationError

from models import EXERCISE_CATEGORIES


class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    category = fields.String(required=True, validate=validate.OneOf(EXERCISE_CATEGORIES))
    equipment_needed = fields.Boolean(load_default=False)

    # Workouts this exercise appears in, without their nested exercises
    workouts = fields.List(
        fields.Nested(lambda: WorkoutSchema(exclude=('workout_exercises',))),
        dump_only=True,
    )


class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(dump_only=True)
    reps = fields.Int(allow_none=True, validate=validate.Range(min=1))
    sets = fields.Int(allow_none=True, validate=validate.Range(min=1))
    duration_seconds = fields.Int(allow_none=True, validate=validate.Range(min=1))

    exercise = fields.Nested(lambda: ExerciseSchema(exclude=('workouts',)), dump_only=True)

    @validates_schema
    def validate_has_measure(self, data, **kwargs):
        # An exercise in a workout is measured by reps or by time
        if data.get('reps') is None and data.get('duration_seconds') is None:
            raise ValidationError('Provide reps or duration_seconds.', field_name='_schema')
        if data.get('sets') is not None and data.get('reps') is None:
            raise ValidationError('sets requires reps.', field_name='sets')


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(required=True, validate=validate.Range(min=1, max=600))
    notes = fields.String(allow_none=True, validate=validate.Length(max=500))

    workout_exercises = fields.List(fields.Nested(WorkoutExerciseSchema), dump_only=True)
