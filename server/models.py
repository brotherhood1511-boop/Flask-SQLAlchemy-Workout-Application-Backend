from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates

# Named constraints keep Alembic migrations stable on SQLite
metadata = MetaData(naming_convention={
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
})

db = SQLAlchemy(metadata=metadata)

EXERCISE_CATEGORIES = ('strength', 'cardio', 'flexibility', 'balance')


class Exercise(db.Model):
    __tablename__ = 'exercises'
    __table_args__ = (
        db.CheckConstraint("length(name) > 0", name='name_not_empty'),
        db.CheckConstraint(
            "category IN ('strength', 'cardio', 'flexibility', 'balance')",
            name='valid_category',
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    category = db.Column(db.String, nullable=False)
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)

    workout_exercises = db.relationship(
        'WorkoutExercise', back_populates='exercise', cascade='all, delete-orphan'
    )
    workouts = association_proxy('workout_exercises', 'workout')

    @validates('name')
    def validate_name(self, key, name):
        if not name or not name.strip():
            raise ValueError('Exercise name is required.')
        return name.strip()

    @validates('category')
    def validate_category(self, key, category):
        if category not in EXERCISE_CATEGORIES:
            raise ValueError(f'Category must be one of: {", ".join(EXERCISE_CATEGORIES)}.')
        return category

    def __repr__(self):
        return f'<Exercise {self.id}, {self.name}, {self.category}>'


class Workout(db.Model):
    __tablename__ = 'workouts'
    __table_args__ = (
        db.CheckConstraint('duration_minutes > 0', name='positive_duration'),
    )

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)

    workout_exercises = db.relationship(
        'WorkoutExercise', back_populates='workout', cascade='all, delete-orphan'
    )
    exercises = association_proxy('workout_exercises', 'exercise')

    @validates('duration_minutes')
    def validate_duration_minutes(self, key, duration_minutes):
        if duration_minutes is None or duration_minutes <= 0:
            raise ValueError('Workout duration must be a positive number of minutes.')
        return duration_minutes

    @validates('notes')
    def validate_notes(self, key, notes):
        if notes is not None and len(notes) > 500:
            raise ValueError('Workout notes must be 500 characters or fewer.')
        return notes

    def __repr__(self):
        return f'<Workout {self.id}, {self.date}, {self.duration_minutes} min>'


class WorkoutExercise(db.Model):
    __tablename__ = 'workout_exercises'
    __table_args__ = (
        db.CheckConstraint('reps IS NULL OR reps > 0', name='positive_reps'),
        db.CheckConstraint('sets IS NULL OR sets > 0', name='positive_sets'),
        db.CheckConstraint(
            'duration_seconds IS NULL OR duration_seconds > 0', name='positive_duration_seconds'
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    reps = db.Column(db.Integer)
    sets = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)

    workout = db.relationship('Workout', back_populates='workout_exercises')
    exercise = db.relationship('Exercise', back_populates='workout_exercises')

    @validates('reps', 'sets', 'duration_seconds')
    def validate_positive(self, key, value):
        if value is not None and value <= 0:
            raise ValueError(f'{key} must be greater than 0.')
        return value

    def __repr__(self):
        return (f'<WorkoutExercise {self.id}, workout {self.workout_id}, '
                f'exercise {self.exercise_id}>')
