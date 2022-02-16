Changes
=======

0.1.6 (2021-09-09)
------------------
* Build dist

0.1.7 (2021-09-14)
------------------
* Create XFormSubmit dir if not present
* Adapt button Modify -> Edit

0.1.9 (2021-09-14)
------------------
* rm _set_today in model
* Add /odk to openrosa url

0.2.0 (2021-09-17)
------------------
* Remove dependency on lxml
* Remove modifications on xml_content field
* Rebuild initial migration
* Add admin management
* Add use of AUTH_USER_MODEL in settings.py
* Add delete button on submitted forms

0.2.1 (2021-10-05)
------------------
* Add migrations on PyPi
* Add is_odk_admin property on user model

0.2.2 (2021-10-05)
------------------
* Add locale fr
* Remove AVAILABLE_TXT and SUBMITTED_TXT from settings
* Replace self.headers by self.setdefault in odk.openrosa.view_pull

0.2.3 (2021-10-06)
------------------
* Adapt locale fr
* Launch migration in EN

0.2.4 (2021-11-24)
------------------
* rm xform FK from submit model

0.2.5 (2021-11-25)
------------------
* rm xform from html
* change input type submit to button type

0.2.6 (2022-02-16)
------------------
* add md5: string in <hash> tag of xformsList.xml