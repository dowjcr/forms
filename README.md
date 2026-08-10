<img src=https://www.jcr.dow.cam.ac.uk/themes/downingjcr/assets/images/logo_purple.png width=120>

# Downing College JCR Forms System

This system allows students to submit DCAC Annual Consumable Grant reimbursement forms online, and for the DCAC's junior and senior treasurers to give approval to ACG requests.

# Managing Forms Configuration (Academic Year & Budgets)

Over summer, you'll need to manually update the current academic year the forms website is set to, and the Treasurer may also at some point want you to open/close the website to budget submissions at their discretion.

Both of these variables are configured using environment variables. To change them, use the following instructions.

## Prerequisites
Navigate to the Forms project directory on the server (you may need to do `cd ..` first to get to `/home`):

```bash
cd /home/web/forms/forms
```

*(Note: You must use `sudo` for the following commands).*

## 1. Update the Variables
Use the Doppler CLI to update the specific variables. The project context is `-p forms` and the config environment is `-c prd`.

**To update the academic year:**
*(Set this to the starting year, e.g., "2026" for the 2026-2027 academic year)*

```bash
sudo doppler secrets set CURRENT_YEAR="2026" -p forms -c prd
```

**To open or close budget submissions:**

```bash
sudo doppler secrets set ALLOW_BUDGET="true" -p forms -c prd
```
*(Change `"true"` to `"false"` to close submissions).*

## 2. Regenerate the `.env` File
Docker Compose cannot see the variables until they are written to the `.env` file. Download the latest secrets from Doppler and overwrite the existing file:

```bash
sudo doppler secrets download --no-file --format docker -p forms -c prd | sudo tee .env > /dev/null
```

## 3. Apply Changes
Tell Docker Compose to recreate the container. This will force it to read the freshly generated `.env` file and apply your changes to the live application:

```bash
sudo docker compose up -d
```

Once this completes, the forms website should be updated as necessary.

# Installation

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
