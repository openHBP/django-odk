---
created: 2026-11-20
type: bug
tags: [security, idor, access-control, views]
---

## Symptôme
Rapport bug bounty (centrespilotes.be) : un compte gratuit lit toute soumission (`GET /odk/submitted/<id>/` : PII, GPS, XML brut), supprime tout formulaire (`POST /odk/<id>/delete`) ou soumission (`POST /odk/submitted/<id>/delete`), crée des formulaires (`POST /odk/add/`). Ids séquentiels → énumération complète.

## Repro
Tout utilisateur connecté sans rôle → 200/302 sur ces routes. Les boutons étaient seulement masqués dans les templates via `user.is_odk_admin`.

## Cause
`views.py` n'utilisait que `LoginRequiredMixin` / `@login_required` : authentification sans autorisation. Contrôle de rôle uniquement côté UI.
Bug annexe : `XFormSubmitDelView.delete()` jamais appelé avec Django ≥ 4 (`DeleteView.post()` → `form_valid()`), fichiers xml/photos orphelins.

## Fix
- Nouveau `django_odk/odk/permissions.py` : accès si superuser, `user.is_odk_admin` vrai (attribut/propriété/méthode), ou permission modèle Django (`odk.view_/add_/change_/delete_xform[submit]`).
- Toutes les vues de gestion protégées ; actions GET à effet de bord vérifiées en ligne (`xls2xml` → change_xform, `loaddata` → change_xformsubmit, `createmodel` → superuser seul car écrit du code Python).
- Anonyme → redirection login, connecté sans droit → 403.
- `delete()` → `form_valid()` dans `XFormSubmitDelView`.
- Vérifié par un script de test hors dépôt (24 cas OK).
- Rupture : liste/détail XForm exigent maintenant `view_xform` (ou le rôle).

## Liens
- [[2026-11-16-odk-submission-path-traversal]]
- Dépendance non déclarée : `bs4` (importée par `odkdata/load_submit_data.py`, absente de `pyproject.toml`).
