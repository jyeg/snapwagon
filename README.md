# Snap Wagon

## Installation

### Project Directory

Create a project directory for Snap Wagon on your local machine. This is the structure I use:

```bash
Projects
└── snapwagon.io
    ├── media
    ├── source
    ├── static
    └── venv
```

The `media` and `static` directories hold all static asset files. User-created files are uploaded to `media` and assets created by our team live in `static`. All of the code lives in `source`. The virtual environment is housed in `venv`. We'll go into each of these directories more in depth in subsequent sections.

### Source

Clone the repository from GitHub using the following command. If you are using my directory structure, then clone the files in `source`.

```bash
$ git clone git@github.com:snapwagon/snapwagon.git
```

### Python

Snap Wagon requires Python 3. Install it with _Homebrew_ by running the following command in your terminal:

```bash
$ brew install python3
```

### Virtual Environment

Install _virtualenv_ to create virtual environments for Python. Create a new virtual environment for Snap Wagon. Make sure you change directories into `venv` first.

```bash
$ cd ~/Projects/snapwagon.io/venv
$ pip3 install virtualenv
$ virtualenv -p /usr/local/bin/python3 .
$ source ./bin/activate
```

Next, navigate to the `source` directory and run the following command to install all of the project dependencies. Your terminal should indicate that your virtual environment (venv) is activated.

```bash
(venv) $ pip install -r requirements/local.txt
```

### Environment Variables

Snap Wagon requires some environment variables to be configured in order to run the server. These variables include database credentials and API keys to _Sparkpost_ and _Stripe_. Enable these environment variables by executing the following command from the `source` directory.

```bash
(venv) $ source .env
```

### Database

Snap Wagon uses a PostgreSQL database. Install it with _Homebrew_ and then run the `psql` client.

```bash
(venv) $ brew install postgresql
(venv) $ psql postgres
psql (9.6.3)
Type "help" for help.

postgres=# 
```

Create a new username and a password and then quit `psql`. After you quit, you will be brought back to your normal terminal. 

```bash
postgres=# CREATE ROLE username WITH LOGIN PASSWORD 'password';
postgres=# ALTER ROLE username CREATEDB;
postgres=# \q
```

> Don't literally type the words `username` and `password`--replace them with a username and password of your choosing. Make sure the `DATABASE_USER` and `DATABASE_PASS` variables in your `.env` file match the PostgreSQL `username` and `password` you just chose. You will have to re-`source` your environment variables if you change them in your `.env` file.

Log back into `psql` with your new user and then create a new database for Snap Wagon.

```bash
(venv) $ psql postgres -U username
psql (9.6.3)
Type "help" for help.

postgres=# CREATE DATABASE snapwagon;
postgres=# GRANT ALL PRIVILEGES ON DATABASE snapwagon TO username;
postgres=# \connect snapwagon
snapwagon=#
```

Make sure all of your `DATABASE_` environment variables match up to the values you chose one last time.

### Django

Now that the database exists, migrate the schema configured in Django.

```bash
(venv) $ python manage.py migrate --settings=settings.local
```

> If you run `export DJANGO_SETTINGS_MODULE=settings.local` in your terminal, you can omit the `--settings` argument when running `manage.py`.

After you migrate your database schema, create a Django superuser. Superusers have access to the _admin_ portal.

```bash
(venv) $ python manage.py createsuperuser
```

As a final step, collect Snap Wagon's static files into the `static` directory. If you copied my directory structure, then the _settings_ file is already configured to point to the right location. Then, run your Django server. With the server running, you should be able to visit Snap Wagon in your browser at [http://localhost:8000](http://localhost:8000) and the Django _admin_ at [http://localhost:8000/admin/](http://localhost:8000/admin/). 

```bash
(venv) $ python manage.py collectstatic
(venv) $ python manage.py runserver 0.0.0.0:8000
```

One last thing. Execute the following code to run the server tests. Make sure your current directory is `/source/snapwagon/`.

```bash
(venv) $ python runtests.py
```
