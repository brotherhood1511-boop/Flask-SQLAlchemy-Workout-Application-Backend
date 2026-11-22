#!/usr/bin/env python3

from datetime import date

from app import app
from models import db, Exercise, Workout, WorkoutExercise

with app.app_context():
    print('Clearing existing data...')
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()
    db.session.commit()

    print('Creating exercises...')
    squat = Exercise(name='Back Squat', category='strength', equipment_needed=True)
    pushup = Exercise(name='Push-Up', category='strength', equipment_needed=False)
    run = Exercise(name='Treadmill Run', category='cardio', equipment_needed=True)
    plank = Exercise(name='Plank', category='balance', equipment_needed=False)
    stretch = Exercise(name='Hamstring Stretch', category='flexibility', equipment_needed=False)
    db.session.add_all([squat, pushup, run, plank, stretch])

    print('Creating workouts...')
    leg_day = Workout(date=date(2026, 11, 16), duration_minutes=60, notes='Heavy lower body session.')
    cardio_day = Workout(date=date(2026, 11, 18), duration_minutes=45, notes='Steady-state cardio and core.')
    recovery = Workout(date=date(2026, 11, 20), duration_minutes=30)
    db.session.add_all([leg_day, cardio_day, recovery])

    print('Adding exercises to workouts...')
    db.session.add_all([
        WorkoutExercise(workout=leg_day, exercise=squat, reps=8, sets=5),
        WorkoutExercise(workout=leg_day, exercise=pushup, reps=15, sets=3),
        WorkoutExercise(workout=cardio_day, exercise=run, duration_seconds=1800),
        WorkoutExercise(workout=cardio_day, exercise=plank, duration_seconds=60),
        WorkoutExercise(workout=recovery, exercise=stretch, duration_seconds=120),
        WorkoutExercise(workout=recovery, exercise=plank, duration_seconds=45),
    ])

    db.session.commit()
    print('Seeding complete!')
