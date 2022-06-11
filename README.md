# neighbourfy

-----------------------------------------------------

## Github + Trello

When commiting changes use **3 - Kanban Dev Board** trello board.
add the #x at the start of every commit to signify card you are working on 

i.g.:

    > git commit -m "#1 inital commit to of the project"

-----------------------------------------------------

Required set up configurations:

Create a virtual environment in the neighbourfy/ folder using the following windows (or equivalent) terminal commands

    > py -m venv venv

    > venv\Scripts\activate

    > py -m pip install -r requirements.txt

note: if you do not activate the Venv before installing the requirements.txt,
then it will be installed to your main python directory

-----------------------------------------------------

Create a file in neighbourfy/main/ called 'config.py'

should follow this structure:

```python
from datetime import timedelta
secret_key = '<- add secret key here ->'
database_uri = 'mysql+pymysql://<- DB Username ->:<- DB Password ->@<- DB domain/IP (localhost normally) ->/<- DB Name ->'
debug_setting = True
remember_cookie_duration = timedelta(days=1)
sqlalchemy_track_modifications = False
```
*Note: replace the <- -> with the correct info*

- if on local computer then leave out ':<- DB Password ->'
to look something like this: 'mysql+pymysql://root@localhost/neighbourfy'


secret_key: Use the following commands to generate a secret key:

    > python

    >>> import os

    >>> os.urandom(24).hex()

-----------------------------------------------------

Once the models.py file is updated you can use the following commands
to add the tables to your local database for testing:

    > python

    >>> from main import db

    >>> db.create_all()

-----------------------------------------------------

## database must does

you must add user roles before any users can be added to the site

the minimum must be 

id: 1 -> User
id: 2 -> Admin

-----------------------------------------------------

## to run the site

use the 'passenger_wsgi.py'