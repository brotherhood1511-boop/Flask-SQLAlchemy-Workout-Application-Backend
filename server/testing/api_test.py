import pytest
from sqlalchemy.exc import IntegrityError

from models import db, Exercise, Workout, WorkoutExercise


def create_exercise(client, **overrides):
    body = {'name': 'Push-Up', 'category': 'strength', 'equipment_needed': False, **overrides}
    return client.post('/exercises', json=body)


def create_workout(client, **overrides):
    body = {'date': '2026-11-21', 'duration_minutes': 45, 'notes': 'Upper body', **overrides}
    return client.post('/workouts', json=body)


class TestExercises:
    def test_create_and_get(self, client):
        response = create_exercise(client)
        assert response.status_code == 201
        exercise = response.get_json()
        assert exercise['name'] == 'Push-Up'

        assert client.get('/exercises').get_json()[0]['id'] == exercise['id']
        assert client.get(f"/exercises/{exercise['id']}").status_code == 200

    def test_get_missing(self, client):
        assert client.get('/exercises/999').status_code == 404

    def test_schema_rejects_bad_category(self, client):
        response = create_exercise(client, category='swimming')
        assert response.status_code == 400
        assert 'category' in response.get_json()['errors']

    def test_schema_requires_name(self, client):
        response = client.post('/exercises', json={'category': 'cardio'})
        assert response.status_code == 400
        assert 'name' in response.get_json()['errors']

    def test_unique_name_constraint(self, client):
        create_exercise(client)
        response = create_exercise(client)
        assert response.status_code == 400

    def test_delete(self, client):
        exercise_id = create_exercise(client).get_json()['id']
        assert client.delete(f'/exercises/{exercise_id}').status_code == 204
        assert client.get(f'/exercises/{exercise_id}').status_code == 404


class TestWorkouts:
    def test_create_and_get(self, client):
        response = create_workout(client)
        assert response.status_code == 201
        workout = response.get_json()
        assert workout['date'] == '2026-11-21'

        assert len(client.get('/workouts').get_json()) == 1
        assert client.get(f"/workouts/{workout['id']}").get_json()['workout_exercises'] == []

    def test_get_missing(self, client):
        assert client.get('/workouts/999').status_code == 404

    def test_schema_rejects_bad_duration(self, client):
        response = create_workout(client, duration_minutes=0)
        assert response.status_code == 400
        assert 'duration_minutes' in response.get_json()['errors']

    def test_schema_rejects_bad_date(self, client):
        assert create_workout(client, date='not-a-date').status_code == 400

    def test_delete_cascades_to_workout_exercises(self, client):
        workout_id = create_workout(client).get_json()['id']
        exercise_id = create_exercise(client).get_json()['id']
        client.post(f'/workouts/{workout_id}/exercises/{exercise_id}/workout_exercises',
                    json={'reps': 10, 'sets': 3})

        assert client.delete(f'/workouts/{workout_id}').status_code == 204
        assert WorkoutExercise.query.count() == 0
        assert client.get(f'/exercises/{exercise_id}').status_code == 200


class TestWorkoutExercises:
    def test_add_exercise_to_workout(self, client):
        workout_id = create_workout(client).get_json()['id']
        exercise_id = create_exercise(client).get_json()['id']

        response = client.post(
            f'/workouts/{workout_id}/exercises/{exercise_id}/workout_exercises',
            json={'reps': 12, 'sets': 3},
        )
        assert response.status_code == 201
        assert response.get_json()['exercise']['name'] == 'Push-Up'

        workout = client.get(f'/workouts/{workout_id}').get_json()
        assert workout['workout_exercises'][0]['reps'] == 12

        exercise = client.get(f'/exercises/{exercise_id}').get_json()
        assert exercise['workouts'][0]['id'] == workout_id

    def test_requires_reps_or_duration(self, client):
        workout_id = create_workout(client).get_json()['id']
        exercise_id = create_exercise(client).get_json()['id']
        response = client.post(
            f'/workouts/{workout_id}/exercises/{exercise_id}/workout_exercises', json={},
        )
        assert response.status_code == 400

    def test_missing_workout_or_exercise(self, client):
        exercise_id = create_exercise(client).get_json()['id']
        response = client.post(
            f'/workouts/999/exercises/{exercise_id}/workout_exercises', json={'reps': 5},
        )
        assert response.status_code == 404


class TestModelValidations:
    def test_exercise_name_required(self, client):
        with pytest.raises(ValueError):
            Exercise(name='  ', category='cardio')

    def test_exercise_category_allowed(self, client):
        with pytest.raises(ValueError):
            Exercise(name='Rowing', category='water')

    def test_workout_duration_positive(self, client):
        with pytest.raises(ValueError):
            Workout(duration_minutes=-5)

    def test_workout_exercise_reps_positive(self, client):
        with pytest.raises(ValueError):
            WorkoutExercise(reps=0)


class TestTableConstraints:
    def test_check_constraint_on_workout_duration(self, client):
        # Bypass the model validator to hit the database CHECK constraint directly
        with pytest.raises(IntegrityError):
            db.session.execute(db.text(
                "INSERT INTO workouts (date, duration_minutes) VALUES ('2026-11-21', 0)"
            ))
        db.session.rollback()

    def test_not_null_exercise_name(self, client):
        with pytest.raises(IntegrityError):
            db.session.execute(db.text(
                "INSERT INTO exercises (category, equipment_needed) VALUES ('cardio', 0)"
            ))
        db.session.rollback()
