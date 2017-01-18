rm -r -f db.sqlite3
python3 manage.py migrate
python3 manage.py loaddata datasets/django/themes_django.json
python3 manage.py loaddata datasets/django/all_django.json
python3 manage.py createinitialrevisions
python3 manage.py create_superuser --email phoenixilya@gmail.com --password 123
python3 manage.py generate_markup_django --count 100
python3 manage.py loaddata datasets/django/markup_django.json