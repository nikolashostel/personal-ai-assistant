-- Running Coach: keep only source metrics needed for training analysis.
-- Run once against the existing personal_ai database as a database administrator.

ALTER TABLE running_workouts
    DROP COLUMN IF EXISTS calories,
    DROP COLUMN IF EXISTS feeling;
