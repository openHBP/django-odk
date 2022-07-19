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

1.0.0 (2022-06-18)
------------------
* rm modified_on & modified_by field
* add convert xls 2 xml (use of pxforms)
* new odkdata app with 2 methods: create_model (use of xlsconv) & load_submit_data
* add datetime fields in XForm & XFormSubmit to check data convert & data load_submit_data
* modify view for Odk load with 4 steps (cfr. README file)

1.0.1 (2022-06-21)
------------------
* make xml_content and created_by field as null in order to upload and then process!
* force odkdata/migrations & odkdata/models to git
* add is_odk_admin check in template
* change message when error App does not exist in model

1.0.2 (2022-06-21)
------------------
* Add 'doc' and 'xform_sample' folder

1.1.1 (2022-06-27)
------------------
* ReadMe corrections
* Add xfs OneToOneField field between final model and odk.XFormSubmit
* Add 'doc' and 'xform_sample' folder
* Bug in odk.admin for action: xformsubmit_load_data
* Add post-save signal on XFormSubmit model
* Change gettext into gettext_lazy in odk.models
* Add functions in odkdata.create_model
* Adapt messages for Submitted forms query set (odk.admin.py)

1.1.4 (2022-06-29)
------------------
* Issues with PyPi new version not visisble
* load_submit_data Issues
* Add blank line in create_model methods
* Add post-save signal @ XForm creation to set all xml_fields: xml_content, form_id, version & title
* Adapt _set methods of XForm

1.1.5 (2022-07-18)
------------------
* date format in template
* model ordering
* add DB error catch in load_submit_data

1.1.6 (2022-07-19)
------------------
* rm signal on xform to allow upload xls and convert xls to xml
* redirect page after xls2xml done