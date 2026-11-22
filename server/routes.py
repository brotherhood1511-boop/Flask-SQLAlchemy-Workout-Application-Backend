from flask import Blueprint, request, make_response

from models import db, Workout, Exercise, WorkoutExercise
from schemas import WorkoutSchema, ExerciseSchema, WorkoutExerciseSchema

api = Blueprint('api', __name__)

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True, exclude=('workout_exercises',))
exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True, exclude=('workouts',))
workout_exercise_schema = WorkoutExerciseSchema()


def not_found(model_name, id):
    return make_response({'error': f'{model_name} {id} not found'}, 404)


# ---------- Workouts ----------

@api.get('/workouts')
def get_workouts():
    return make_response(workouts_schema.dump(Workout.query.all()), 200)


@api.get('/workouts/<int:id>')
def get_workout(id):
    workout = db.session.get(Workout, id)
    if not workout:
        return not_found('Workout', id)
    return make_response(workout_schema.dump(workout), 200)


@api.post('/workouts')
def create_workout():
    data = workout_schema.load(request.get_json() or {})
    workout = Workout(**data)
    db.session.add(workout)
    db.session.commit()
    return make_response(workout_schema.dump(workout), 201)


@api.delete('/workouts/<int:id>')
def delete_workout(id):
    workout = db.session.get(Workout, id)
    if not workout:
        return not_found('Workout', id)
    # Cascade removes this workout's WorkoutExercise rows
    db.session.delete(workout)
    db.session.commit()
    return make_response('', 204)


# ---------- Exercises ----------

@api.get('/exercises')
def get_exercises():
    return make_response(exercises_schema.dump(Exercise.query.all()), 200)


@api.get('/exercises/<int:id>')
def get_exercise(id):
    exercise = db.session.get(Exercise, id)
    if not exercise:
        return not_found('Exercise', id)
    return make_response(exercise_schema.dump(exercise), 200)


@api.post('/exercises')
def create_exercise():
    data = exercise_schema.load(request.get_json() or {})
    exercise = Exercise(**data)
    db.session.add(exercise)
    db.session.commit()
    return make_response(exercise_schema.dump(exercise), 201)


@api.delete('/exercises/<int:id>')
def delete_exercise(id):
    exercise = db.session.get(Exercise, id)
    if not exercise:
        return not_found('Exercise', id)
    # Cascade removes this exercise from every workout it was in
    db.session.delete(exercise)
    db.session.commit()
    return make_response('', 204)


# ---------- Adding an exercise to a workout ----------

@api.post('/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises')
def add_exercise_to_workout(workout_id, exercise_id):
    workout = db.session.get(Workout, workout_id)
    if not workout:
        return not_found('Workout', workout_id)
    exercise = db.session.get(Exercise, exercise_id)
    if not exercise:
        return not_found('Exercise', exercise_id)

    data = workout_exercise_schema.load(request.get_json() or {})
    workout_exercise = WorkoutExercise(workout=workout, exercise=exercise, **data)
    db.session.add(workout_exercise)
    db.session.commit()
    return make_response(workout_exercise_schema.dump(workout_exercise), 201)
