# GitHub Setup

Project name:

```text
LY-Scope Ver.2
```

Current public repository:

```text
lyn0109-Toxi/ToxiGuard-NORA
```

## Repository Role

This repository should contain only the new Ver.2 application codebase and the Streamlit deployment entrypoint. The original LY-Scope Ver.1 repository should remain untouched.

Private Ver.1 reference files may exist locally inside:

```text
legacy/ver1-reference/
```

That folder is intentionally ignored for the public GitHub repository because it can include copied source, reports, and user-like sample data. Do not edit it as the source of truth for Ver.1.

## First GitHub Push

After creating the empty GitHub repository, connect this local project:

```bash
git init
git branch -M main
git add -- <confirmed project paths>
git commit -m "Initialize LY-Scope Ver.2 app base"
git remote add origin https://github.com/lyn0109-Toxi/ToxiGuard-NORA.git
git push -u origin main
```

## Local Verification

Run these before pushing changes:

```bash
npm run check
npm test
```

## GitHub Actions

The repository includes `.github/workflows/ci.yml`. GitHub will run syntax checks and tests on pushes and pull requests to `main`.

## Naming Convention

- Product name: `LY-Scope Ver.2`
- Repository slug: `ToxiGuard-NORA`
- Package name: `ly-scope-ver2`
- Main branch: `main`
