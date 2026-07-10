# Agent Chat: i18n English Default + Migration Fix

## User Prompt

> can you please add english translations and make it the default language (configured with env var). Also, please address the following error when running docker/dev_in_docker.sh:
> pymysql.err.OperationalError: (1054, "Unknown column 'scripts.episode_business_id' in 'field list'")
> (in migration c4a1cbf0d7c2 Backfill story structure tables from script JSON)

## Goals

1. Fix the Alembic migration `c4a1cbf0d7c2` that crashes on fresh Docker start
2. Add English translations to the frontend
3. Make English the default UI language, configurable via `NEXT_PUBLIC_LOCALE` env var

## Changes

### Backend – Migration Fix

**File:** `ai-pic-backend/alembic/versions/c4a1cbf0d7c2_backfill_story_structure.py`

**Root cause:** The migration's `upgrade()` used `session.query(Script).all()` which
causes SQLAlchemy ORM to generate `SELECT scripts.episode_business_id, ...`.
That column (along with `is_deleted`, `business_id`) is added by *later* migrations
(`b9b5c7e3a8d1`, `dc3d7b9b2c41`) that run after `c4a1cbf0d7c2` in the chain.
On a fresh database, those columns do not yet exist → `Unknown column` error.

**Fix:**
- Removed `from app.models.script import Script` and `from sqlalchemy.orm import Session`
- Removed `load_live_payloads` import (no longer needed)
- Added `_load_payloads_raw(connection, script_id)` which uses `sa.text()` raw SQL
  to SELECT only the columns present at this migration step
- Replaced `session.query(Script).all()` with
  `bind.execute(sa.text("SELECT id FROM scripts"))` to list script IDs

### Frontend – i18n Infrastructure

**New files:**
- `src/lib/i18n.ts` – translation utility: `t()`, `formatDateTime()`, `formatDateOnly()`,
  `formatRelativeTime()`, `locale`, `displayLocale`
- `src/locales/en.json` – English translations (658 keys, growing)
- `src/locales/zh.json` – Chinese translations (mirror)

**Design:**
- `NEXT_PUBLIC_LOCALE` env var (baked in at build time, works in both Server and
  Client Components)
- Default: `"en"` when env var is absent or empty
- Locale `"zh"` or `"zh-CN"` triggers Chinese; anything else → English
- No external dependency added; uses static `require()` for locale JSON

**Updated files (partial list):**
- `src/app/layout.tsx` – `<html lang={locale}>`, translated metadata
- `src/utils/scriptGenerationDefaults.ts` – `language: locale`
- `src/utils/auth.ts` – date formatting uses `displayLocale`
- All `zh-CN` toLocaleDateString/toLocaleString calls → `displayLocale`
- Key feature components (canvas, episodes, stories, virtual-ip, scripts, workbench,
  environments, admin) – hardcoded Chinese strings → `t()` calls

### Docker env templates

Added `NEXT_PUBLIC_LOCALE=en` (with comment) to:
- `docker/.env.example`
- `docker/.env.lite.example`
- `docker/.env.prod.example`

## Validation

- Migration syntax verified: `python3 -m py_compile c4a1cbf0d7c2_backfill_story_structure.py` ✓
- `zh-CN` locale strings removed from all non-locale `.ts`/`.tsx` files ✓
- `NEXT_PUBLIC_LOCALE` default is `"en"` ✓
- `lint` not runnable in this environment (eslint not installed at agent level)

## Next Steps

- Full `npm run lint` + `npm run build` on a real dev machine to catch any
  TypeScript / import errors introduced by translations
- Run `docker/dev_in_docker.sh` to confirm migration completes without error
- Review remaining Chinese strings in API utility files (comments only, not UI)

## Linked Commits

See git log for commits pushed by this agent session.
