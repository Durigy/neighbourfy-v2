# Required setup configurations for local development

## Create a virtual environment using the following:

### Windows commands

```
> python -m venv venv 

> venv\Scripts\activate

> python -m pip install -r requirements.txt
```

### Linux commands

```
> python3 -m venv venv

> source venv/bin/activate

> python3 -m pip install -r requirements.txt
```

``` Note: If you do not activate the 'venv' before installing the requirements.txt, then it will be installed to your main python directory ```

---

## Create a file in the ./main/ folder called 'config.py'

```Python
from datetime import timedelta
secret_key = '<- add secret key here ->'
database_uri = 'mysql+pymysql://<- DB Username ->:<- DB Password ->@<- DB domain/IP (localhost normally) ->/<- DB Name ->'
debug_setting = True
remember_cookie_duration = timedelta(days=1)
sqlalchemy_track_modifications = False
```
``` Note: Replace the <- -> with the correct info ```

### For local development leave out ':<- DB Password ->' to look something like this: 
```Python
mysql+pymysql://root@localhost/databasename
```

### To generate a secret_key, use the following commands:

```
> python

>>> import os

>>> os.urandom(24).hex()
```

``` Note: Environment variables should be used on a production server. The config.py file is for development use only ```

---

## To creating the database tables:
``` Note: Once the models.py file is updated you can use the following commands to add the tables to your local database for testing ```

```
> python

>>> from main import db

>>> db.create_all()
```

-----------------------------------------------------

## Database must do's

you must add user roles before any users can be added to the site

the minimum must be 

id: 1 -> User
id: 2 -> Admin

-----------------------------------------------------

## To run the site

use the 'passenger_wsgi.py'