## User Prompt

Backend fails on `alembic upgrade head` with:
`pymysql.err.ProgrammingError: (1146, "Table 'ai_video_studio.video_generation_tasks' doesn't exist")`
during migration `b7f9e6d3c2a1 -> 9c1a2b3c4d5e, expand video provider task id length`.

## Goals

Fix the Alembic migration dependency so `9c1a2b3c4d5e` runs after the table it modifies is created.

## Changes

- `ai-pic-backend/alembic/versions/9c1a2b3c4d5e_expand_video_provider_task_id.py`:
  Changed `down_revision` from `"b7f9e6d3c2a1"` to `"6b747471077a"`.

**Root cause:** Both `6b747471077a` (creates `video_generation_tasks`) and `9c1a2b3c4d5e`
(alters `provider_task_id` in that table) declared `down_revision = "b7f9e6d3c2a1"`, making
them siblings in the DAG. Alembic could execute `9c1a2b3c4d5e` before `6b747471077a`,
causing the "table doesn't exist" error. Setting `9c1a2b3c4d5e`'s parent to `6b747471077a`
ensures linear ordering.

## Validation

Migration DAG is now:
`b7f9e6d3c2a1` → `6b747471077a` (create table) → `9c1a2b3c4d5e` (expand column)

The merge head `e1f2a3b4c5d6` still depends on `("8848b61e51a8", "9c1a2b3c4d5e")` and
`fcb18d8c3fab` still depends on `6b747471077a` — no other migration dependencies broken.

## Next Steps

Restart the backend container to verify `alembic upgrade head` completes successfully.

## Linked Commits

See PR for commit SHA.
