# Markdown Rendering Strategy

## Objective

Maintain one coherent cognition shell across HTML and Markdown surfaces without duplicating navigation logic.

## Direction

1. Keep `docs/notebooklm_public/assets/global.css` as the shared visual baseline.
2. Keep HTML index pages as the canonical navigation shell.
3. Introduce a lightweight static rendering step that converts selected Markdown docs into shell-wrapped HTML pages.
4. Inject shared components at build time:
   - global top navigation
   - breadcrumbs
   - related sections
   - shared footer
5. Preserve original Markdown files as source-of-truth content.

## Proposed Pipeline

1. Source docs: `docs/notebooklm_public/**/*.md`
2. Render markdown to HTML body.
3. Wrap body with shared shell template.
4. Emit to parallel `*.rendered.html` (or mirrored `/site/` output).
5. Publish shell-rendered pages for GitHub Pages navigation.

## Navigation Injection Rules

- All rendered pages receive global nav links.
- All rendered pages include ontology map and live demo links.
- Section-aware breadcrumbs are generated from path.
- Related-section blocks are generated from a mapping table.

## Consistency Rules

- No per-page custom color systems.
- No duplicate navigation variants.
- All pages keep the same tagline:
  - The approval remained.
  - The runtime changed.
  - Execution legitimacy diverged.

## Rollout Guidance

- Start with high-traffic docs (`FIRST_DEMO_WALKTHROUGH`, `EXECUTIVE_FIELD_OVERVIEW`, `WHAT_DETERMA_HAS_PROVEN`).
- Validate link integrity after each render batch.
- Keep markdown-only fallback links active during transition.

## Non-Goals (Current Pass)

- No full static-site framework migration.
- No ontology content expansion.
- No markdown content rewrite for style only.

## Outcome

A single cognition shell can span demo, index pages, and rendered markdown docs without fragmenting public experience.
