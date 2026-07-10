## User Prompt

> I am getting this error all over the place:
> Module not found: Can't resolve '@/lib/i18n' ... could you please finish the work that was intended here?

## Goals

1. Reproduce the frontend failure and confirm root cause.
2. Restore the missing shared `@/lib/i18n` module expected by frontend imports.
3. Ensure the module path is versioned so it does not disappear again.

## Changes

- Added `/home/runner/work/ai-video-studio/ai-video-studio/ai-pic-frontend/src/lib/i18n.ts`.
  - Exports `t`, `locale`, `displayLocale`, `formatDateTime`, `formatDateOnly`, and `formatRelativeTime`.
  - Locale source is `NEXT_PUBLIC_LOCALE` with default to English and Chinese detection for `zh*` values.
  - Uses `/src/locales/en.json` and `/src/locales/zh.json` for key lookups with fallback behavior.
- Updated `/home/runner/work/ai-video-studio/ai-video-studio/.gitignore`.
  - Added unignore rules for `ai-pic-frontend/src/lib/` so `src/lib/i18n.ts` can be tracked.

## Validation

Pre-change baseline (after installing frontend deps):
- `cd ai-pic-frontend && npm run lint` ❌
  - failed on existing parse/lint issues and unresolved `@/lib/i18n` imports.
- `cd ai-pic-frontend && npm run test` ❌
  - failed with repeated `Cannot find module '@/lib/i18n'` errors.
- `cd ai-pic-frontend && npm run build` ❌
  - failed with repeated `Module not found: Can't resolve '@/lib/i18n'` errors plus existing parse/font fetch issues.

Post-change:
- `cd ai-pic-frontend && npm run test` ❌
  - no more `@/lib/i18n` module-not-found errors; remaining failures are unrelated existing test failures.
- `cd ai-pic-frontend && npm run build` ❌
  - no more `@/lib/i18n` module-not-found errors; remaining failures are existing parse error in `ProductionCanvasMediaControls.tsx` and blocked font fetch.
- `cd ai-pic-frontend && npm run lint` ❌
  - no `@/lib/i18n` import resolution errors; remaining failures are pre-existing lint/parser issues.

## Next Steps

1. Fix the existing parse error in `ai-pic-frontend/src/components/features/canvas/ProductionCanvasMediaControls.tsx`.
2. Address remaining frontend test failures unrelated to i18n module restoration.
3. Optionally replace/avoid external Google font fetch in restricted environments for deterministic builds.

## Linked Commits

- `fix(frontend): unignore src/lib for i18n module`
