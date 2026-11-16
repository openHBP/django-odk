---
created: 2026-11-16
type: bug
tags: [security, path-traversal, openrosa, storage]
---

## Symptôme
Dossiers parasites dans `/var/www/cpilote/media` (`edenintigriti-trav`, `evilu12b3`) : charges utiles de scanner / bug bounty.

## Repro
POST anonyme sur `/odk/submission` (`@csrf_exempt`, sans auth) avec un `xml_submission_file` contenant `<data id="../edenintigriti-trav" ...>`.
Chemin calculé `XFormSubmit/../edenintigriti-trav/<date>/x.xml` → résolu sous `MEDIA_ROOT/edenintigriti-trav/`.

## Cause
- `ManageFile.save_file()` / `save_pictures()` (`odk/utils.py`) utilisent `form_id` (regex sur le XML, contrôlé par l'attaquant) et les noms de fichiers client tels quels.
- La vérification `get_xform_pk` (form connu) était désactivée depuis 2022.
- Django 4.2 `Storage.save()` n'appelle `validate_file_name` qu'**après** `_save()` → trop tard.
- `OverwriteStorage.get_available_name()` supprime la cible avant écriture → suppression/écrasement arbitraire de tout fichier sous `MEDIA_ROOT`.

## Fix
Release 1.2.0 :
- `form_id` validé (`[A-Za-z0-9_.-]{1,100}`, pas `.`/`..`) + doit exister dans `XForm`.
- Noms de fichiers → `get_valid_filename(os.path.basename(...))` (xml, photos, xls).
- `OverwriteMixin.get_available_name()` appelle `validate_file_name(name, allow_relative_path=True)` avant `delete()`.
- Auth Basic optionnelle `ODK_SUBMISSION_AUTH = True` (`odk/openrosa/auth.py`).
- `LoginRequiredMixin` / `@login_required` sur XFormList/Detail (xls2xml, createmodel) et `submittedfile_list`.
- Corrigés au passage : `LOG.error = msg`, `return Http404`, 500 sur méthodes ≠ HEAD/POST.

Testé (venv Django 4.2.30) : traversal bloqué, fichier victime intact, auth 401/OK.

## Liens
- [[2026-11-16-main-odk-submission-security-fix]]
