-- Running Coach: keep only source metrics needed for training analysis.
-- Run once against the existing personal_ai database as a database administrator.

ALTER TABLE running_workouts
    DROP COLUMN IF EXISTS calories,
    DROP COLUMN IF EXISTS feeling;

-- The first Telegram test workout is duplicated in the Apple Health export.
-- Remove it before importing the historical data.
DELETE FROM running_workout_laps
WHERE workout_id = 1;

DELETE FROM running_workouts
WHERE id = 1;
