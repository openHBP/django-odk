# ODK-Collect - by [CRA-W](https://www.cra.wallonie.be/en)

> Django Data collection tool using [ODK-collect](https://play.google.com/store/apps/details?id=org.odk.collect.android&hl=en_US&gl=US) mobile app



---

Unit: [CRA-W: Coordination and strategy](https://www.cra.wallonie.be/fr/direction-coordination-et-strategie)

Author: Patrick HOUBEN (p.houben@cra.wallonie.be)

---

## Prerequisite
[Git](https://gitforwindows.org/) - 
[Python](https://www.python.org/downloads/) -
[Pipenv](https://pipenv.pypa.io/en/latest/install/)

## A. Server side install

### A.1. Clone repo and configure python virtualenv
```bash
$ git clone git@github.com:openHBP/django-odk.git
$ cd django-odk
$ sudo mkdir .venv
$ pipenv install
$ pipenv shell
$ cd source
```

### A.2. Check django install
```bash
(django-odk) $ python -m django --version
# This should return django version number, 3.2 or upper
(django-odk) $ python manage.py check
```

### A.3. Run migrations
```bash
(django-odk) $ python manage.py migrate
```

### A.4. Create superuser
```bash
(django-odk) $ python manage.py createsuperuser
```

### A.5. Create a WiFi HotSpot and get IP server address
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```
Keep this IP address (ex: 10.12.108.3) for point B.2. Client connect

### A.5. Add IP to ALLOWED_HOSTS in settings.py
```py
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "10.12.108.3"]
```

### A.6. Launch site & login using superuser credentials
```bash
(django-odk) $ python manage.py runserver 10.10.108.3:8000
```

Launch server http://10.10.108.3:8000

## B. Xforms create & load

### B.1. XLSForm creation

#### Example
As a simple example using geo-location and pictures, use **picture_loop.xlsx** file located in 'media.sample' folder

#### XLSForm format
[What is an XLSForm?](https://xlsform.org/en/)

Build an [XLSForm](https://docs.getodk.org/xlsform/) file with 3 tabs 'survey', 'choices', 'settings'

### B.2. XLSForm submit xml file
1. Submit xlsx file on https://getodk.org/xlsform/
2. Check file correctness by using 'Preview in browser' button
3. Download the generated xml file on your computer
4. Upload the downloaded xml file throug the 'Choose file' button of "Server/Available form" menu
5. Click on save button

Once it is done, you are ready to go with form encoding on your smartphone!


## C. Client (smartphone) install

### C.1. Install ODK Collect
Install ODK Collect from [Google Play Store](https://play.google.com/store/apps/details?id=org.odk.collect.android&hl=en_US&gl=US)

For more informations read [ODK install instructions](https://docs.getodk.org/collect-install/#installing-from-google-play-store-recommended)

### C.2. Set up server connexion
Go to "Parameters/Server" and configure
- URL
- username
- password

For more info read [Configure server manually](https://docs.getodk.org/collect-connect/#configure-server-manually)

### B.3. ODK Collect: Download empty forms
Once server configuration is done and that your server is up and running you should see all created and uploaded forms (B.2.4) on your ODK Collect mobile app!

Select those you want to download by clicking on 'Download empty forms' on ODK Collect main board menu.

### B.4. Edit, complete and submit forms
Form edition and submission is quite intuitive. If you encounter some difficulties, follow [ODK documention](https://docs.getodk.org/collect-using/).

## D. Get back submitted data
Go to Submitted form menu of your server to see submitted data


---
Feel free to improve this code!

[Patrick HOUBEN - U13](p.houben@cra.wallonie.be) from [CRA-W](https://www.cra.wallonie.be/fr) 


