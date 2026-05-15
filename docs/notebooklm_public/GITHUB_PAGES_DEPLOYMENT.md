# GitHub Pages Deployment

## Purpose
Deploy the contradiction walkthrough as the default public repository entrypoint.

## Enable Pages
1. Open repository Settings.
2. Open **Pages**.
3. Under **Build and deployment**, set source to **Deploy from a branch**.
4. Select branch: `main`.
5. Select folder: `/ (root)`.
6. Save.

## Expected Public URL

```text
https://determaai.github.io/DETERMA-v0.1-Governed-Runtime-Proof-Baseline/
```

## Deployment Behavior
- Root `index.html` redirects immediately to `demo/index.html`.
- Public contradiction walkthrough becomes the live entry experience.

## Demo Deployment Path

```text
/demo/index.html
```

## Static Asset Expectations
- `demo/` contains walkthrough UI.
- `assets/` contains visual compression maps and screenshot inventory.
- `docs/notebooklm_public/` contains walkthrough and ontology guidance.

## Troubleshooting
- If page renders 404, verify source is `main` and folder is `/ (root)`.
- If redirect does not occur, confirm `index.html` exists at repository root.
- If stale content appears, wait for Pages rebuild and hard-refresh browser cache.
- If assets fail, verify relative links from `demo/index.html` to `../docs/...`.

Note: this document prepares deployment. It does not claim that Pages is already enabled.
