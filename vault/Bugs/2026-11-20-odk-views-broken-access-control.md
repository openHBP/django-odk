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

## Suivi (même jour) : CSRF + OpenRosa
- **CSRF** : `xls2xml`, `createmodel` (écrit du code Python) et `loaddata` s'exécutaient sur GET → un lien piégé suffisait à les faire déclencher par un admin connecté. Passés en POST (`post()` dans `XFormDetailView` / `XFormSubmitDetailView`, boutons → `<form method="post">` + `{% csrf_token %}`). GET sur ces URL → redirection vers le détail, sans effet.
- **OpenRosa** : `formList/` et `form/<form_id>/` (`openrosa/view_push.py`) décorés `@openrosa_basic_auth`, même opt-in `ODK_SUBMISSION_AUTH` que `submission` (Collect envoie les mêmes identifiants).
- Vérifié par un harnais Django jetable (scratchpad, hors dépôt) : 22 cas OK.

## Re-signalement (2026-11-23)
- Même rapport reçu à nouveau (centrespilotes.be : détail soumission lisible, suppression XForm/soumission, `POST /odk/add/` par un compte gratuit).
- Harnais Django jetable (scratchpad) rejoué sur deux versions :
  - **v1.2.1** (dernier tag) : vulnérable, rapport reproduit (200 sur détail, 302 + suppression effective sur delete/add).
  - **arbre courant (fix 1.2.2, commit `62013b2`)** : 403 sur les 8 routes pour un compte sans rôle ; contrôle positif (`view_xformsubmit` → 200) et anonyme → login OK.
- Conclusion : le site signalé tourne probablement en ≤ 1.2.1. 1.2.2 est commité mais **non tagué**. Il faut déployer ≥ 1.2.2.
- Point à vérifier côté projet hôte : `user.is_odk_admin` ne doit pas être vrai pour un simple abonné, sinon le contrôle est contourné par conception.
