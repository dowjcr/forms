<img src=https://www.jcr.dow.cam.ac.uk/themes/downingjcr/assets/images/logo_purple.png width=120>

# Downing College JCR Forms System

This system allows students to submit DCAC Annual Consumable Grant reimbursement forms online, and for the DCAC's junior and senior treasurers to give approval to ACG requests.

## Installation

Change into the desired installation directory then clone this repository:

```bash
$ git clone https://github.com/dowjcr/forms
```

In line with best practice, create yourself a Python 3.5 `virtualenv`. Assuming you don't have `virtualenv` installed:

```bash
$ pip3 install virtualenv
$ mkdir virtualenvs
$ cd virtualenvs
$ virtualenv -p /usr/bin/python3 forms
$ source forms/bin/activate
```

Now you've activated the `virtualenv`, you can install the requirements:

```bash
$ cd ../forms/forms
$ pip install -r requirements.txt
```

Now configure Django's `settings.py`. An example configuration, `settings_example.py` has been included in the repo.
Simply rename and edit as per the TODOs.

```bash
$ cd forms
$ mv settings_example.py settings.py
```

Migrate and seed the database, then you're ready to run the test server:

```bash
$ cd ..
$ python manage.py makemigrations
$ python manage.py migrate
$ python manage.py seed
$ python manage.py runserver
```

Instructions on how to serve Django in production are widely available; `mod_wsgi` on Apache is to be recommended.

## Built With

- [**Django**](https://www.djangoproject.com/)
- [**django-ucamwebauth**](https://pypi.org/project/django-ucamwebauth/)
- [**jQuery**](https://jquery.com/)
- [**Bootstrap 4.1.1**](https://getbootstrap.com)
- [**Lookup API**](https://www.lookup.cam.ac.uk/doc/ws-doc/)

## Authors

- [**Cameron O'Connor**](https://github.com/cjoc), JCR President 2019-20

## Licence

This project is licensed under the MIT Licence - see LICENSE.md for more details.
