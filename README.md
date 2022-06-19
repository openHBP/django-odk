# django-odk
Django data collection tool using [ODK-collect](https://play.google.com/store/apps/details?id=org.odk.collect.android&hl=en_US&gl=US) mobile app.


## Prerequisite
- Django web site up and running
- Smartphone or tablet with [ODK-Collect installed](https://play.google.com/store/apps/details?id=org.odk.collect.android&hl=en_US&gl=US)
- Set of forms in [Xforms](https://xlsform.org/en/) format available in xml. Use https://getodk.org/xlsform/ to validate and export your forms in xml format.
- Database up & running **with vector geodatabase functionality** (if your ODK form use geopoint): PostGIS, Oracle Spatial, SQLite/SpatiaLite


## Installation
* Run

```bash
$ pip install django-odk
$ python manage.py migrate
$ python manage.py createsuperuser
```

* Add odk and odkdata to your INSTALLED_APPS settings
```py
INSTALLED_APPS = (
    ...
    'odk',
    'odkdata',
)
```

* Add LOCALE_PATHS and appropriate language_code in settings

```py
LOCALE_PATHS = [os.path.join(BASE_DIR, 'odk', 'locale')]

LANGUAGE_CODE = 'en'
# LANGUAGE_CODE = 'fr'
# possible LANGUAGE_CODE on 05/10/2021 are: en, fr
```

* Add appropriate AUTH_USER_MODEL in settings.py
```py
AUTH_USER_MODEL = 'auth.user'
```

* For a more interactive app, configure **logging** as explained in [Lincoln Loop](https://lincolnloop.com/blog/django-logging-right-way/) and **messages** as explained in [Django](https://docs.djangoproject.com/en/4.0/ref/contrib/messages/)


* Add **is_odk_admin** property to your AUTH_USER_MODEL (django.contrib.auth.models file or specific accounts.models)
```py
    @property
    def is_odk_admin(self):
        return self.groups.filter(name='odk-admin').exists()
```


* Add odk.urls to the main urls.py file:
```py
urlpatterns = [
    ...
    path('odk/', include('odk.urls'), name='odk'),
]
```

* Add menu or buttons to access **Available form**
```py
# bootstrap5 menu item example
<li><a class="dropdown-item" href="{% url 'odk:xform_list' %}">{% trans "ODK available forms" %}</a></li>
```

* Add menu or buttons to access **Submitted form**
```py
# bootstrap5 menu item example
<li><a class="dropdown-item" href="{% url 'odk:xformsubmit_list' %}">{% trans "ODK submitted forms" %}</a></li>
```

## Connect to the Django admin site
* create a group 'odk-admin' with create, read, update access on odk objects
* Associate this group to the appropriate users

## XForm Create & Load
Connect to django-odk => **Available form** => Add and follow 4 steps:

1. Build an XLSForm file with 3 tabs 'survey', 'choices', 'settings' [Cfr documentation](https://docs.getodk.org/xlsform/)

2. Upload xlsx file (XForm) by clicking on 'Choose file' and Save

3. Convert xlsx file to xml XForm compatible file

From this point, you are ready to go with form encoding on your smartphone!

> Follow [ODK instructions](https://docs.getodk.org/collect-connect/#configure-server-manually) to configure the connexion to the server

> Get, fill-in and submit data [using ODK Collect](https://docs.getodk.org/collect-using/)

4. If you want to get your data back in a model instead of XML content you can run the **CreateModel** step. It will create a model to get your submitted data in a model formatted like your xlsx form. Thanks [pyxform](https://github.com/XLSForm/pyxform)! Model creation is done into `odkdata` app.

## Get submitted data on server
Go to **Submitted form** menu of your server to see submitted data in XML format.

Insert submitted data through admin module.

Select record or set of records and choose action 'Load Submitted Data'



