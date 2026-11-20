---
created: 2026-11-16
type: decision
tags: [packaging, uv, pypi]
---

## Contexte
Packages installés en top-level (`odk`, `odkdata`, `doc`, `xform_sample`) depuis `django_odk/` — l'ancien `package_dir={"": "django_odk"}`.

## Options
- uv_build : prévu pour un seul module, mal adapté à plusieurs packages top-level.
- setuptools via pyproject : fonctionne mais demande une liste explicite de package data.
- hatchling : `packages = ["django_odk/odk", ...]` retire le préfixe et inclut automatiquement les fichiers non-Python.

## Décision
Hatchling. Version statique dans pyproject.toml pour que `uv version --bump` fonctionne. `artifacts = ["*.mo"]` car les `.mo` sont dans le gitignore.

## Conséquences
`django-bootstrap5` est maintenant une dépendance runtime (les templates l'utilisent). `psycopg2-binary` est dans le groupe dev.
