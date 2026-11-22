# Workout Application Backend

A Flask REST API for personal trainers to track workouts and the exercises in them. Exercises are reusable: the same exercise can be added to many workouts, each time with its own reps, sets, or duration.

Built with Flask, Flask-SQLAlchemy, Flask-Migrate, and Marshmallow.

## Data Model

| Model | Fields | Relationships |
|---|---|---|
| `Workout` | `id`, `date`, `duration_minutes`, `notes` | has many `WorkoutExercise`s; has many `Exercise`s through them |
| `Exercise` | `id`, `name`, `category`, `equipment_needed` | has many `WorkoutExercise`s; has many `Workout`s through them |
| `WorkoutExercise` | `id`, `workout_id`, `exercise_id`, `reps`, `sets`, `duration_seconds` | belongs to a `Workout` and an `Exercise` |

Deleting a workout or an exercise also deletes its `WorkoutExercise` rows.

## Validations

**Table constraints** (enforced by the database)
- `exercises.name` is required and unique, and can't be empty.
- `exercises.category` must be `strength`, `cardio`, `flexibility`, or `balance`.
- `workouts.date` and `workouts.duration_minutes` are required, and `duration_minutes` must be greater than 0.
- `workout_exercises.reps`, `sets`, and `duration_seconds` must be greater than 0 when present.

**Model validations** (SQLAlchemy `@validates`)
- `Exercise.name` can't be blank, and surrounding whitespace is stripped.
- `Exercise.category` must be one of the allowed categories.
- `Workout.duration_minutes` must be positive.
- `Workout.notes` can be at most 500 characters.
- `WorkoutExercise.reps`, `sets`, and `duration_seconds` must be positive.

**Schema validations** (Marshmallow)
- `ExerciseSchema`: `name` is required (1–100 characters), and `category` is required and must be an allowed category.
- `WorkoutSchema`: `date` is required and must be a valid ISO date, `duration_minutes` is required (1–600), and `notes` can be at most 500 characters.
- `WorkoutExerciseSchema`: each measurement must be at least 1, and a request must include `reps` or `duration_seconds`. `sets` can only be used together with `reps`.

Invalid requests return `400` with an `errors` object describing what failed.

## Installation

Requires Python 3.8.13+ and Pipenv.

```bash
git clone https://github.com/brotherhood1511-boop/Flask-SQLAlchemy-Workout-Application-Backend.git
cd Flask-SQLAlchemy-Workout-Application-Backend
pipenv install --dev
pipenv shell
```

Create the database and load the example data:

```bash
cd server
export FLASK_APP=app.py
flask db upgrade
python seed.py
```

## Running the App

From the `server` directory:

```bash
flask run --port 5555
```

The API is now available at `http://localhost:5555`.

Run the tests from the project root:

```bash
pytest
```

## Endpoints

### Workouts

| Method | Path | Description |
|---|---|---|
| `GET` | `/workouts` | List all workouts. |
| `GET` | `/workouts/<id>` | Get one workout, including each of its exercises with reps, sets, and duration. `404` if not found. |
| `POST` | `/workouts` | Create a workout. Body: `date` (`YYYY-MM-DD`), `duration_minutes`, and optional `notes`. Returns `201`. |
| `DELETE` | `/workouts/<id>` | Delete a workout and its workout exercises. Returns `204`, or `404` if not found. |

### Exercises

| Method | Path | Description |
|---|---|---|
| `GET` | `/exercises` | List all exercises. |
| `GET` | `/exercises/<id>` | Get one exercise, including the workouts it appears in. `404` if not found. |
| `POST` | `/exercises` | Create an exercise. Body: `name`, `category`, and optional `equipment_needed` (defaults to `false`). Returns `201`. |
| `DELETE` | `/exercises/<id>` | Delete an exercise and remove it from every workout. Returns `204`, or `404` if not found. |

### Adding an Exercise to a Workout

| Method | Path | Description |
|---|---|---|
| `POST` | `/workouts/<workout_id>/exercises/<exercise_id>/workout_exercises` | Add an exercise to a workout. Body: `reps` and/or `duration_seconds`, plus optional `sets`. Returns `201`, or `404` if the workout or exercise doesn't exist. |

Example:

```bash
curl -X POST http://localhost:5555/workouts/1/exercises/2/workout_exercises \
  -H "Content-Type: application/json" \
  -d '{"reps": 12, "sets": 3}'
```

## Project Structure

```
server/
├── app.py          # App factory, configuration, error handlers
├── models.py       # SQLAlchemy models, table constraints, model validations
├── schemas.py      # Marshmallow schemas: serialization and schema validations
├── routes.py       # API endpoints (Flask blueprint)
├── seed.py         # Example data for every model
├── migrations/     # Alembic migration scripts
└── testing/        # Pytest suite
```
