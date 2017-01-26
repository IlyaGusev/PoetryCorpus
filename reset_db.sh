rm -r -f db.sqlite3
rm -r -f /data/poetry/
python3 manage.py migrate
python3 manage.py loaddata datasets/django/themes_django.json
python3 manage.py loaddata datasets/django/all_django.json
python3 manage.py createinitialrevisions
python3 manage.py create_superuser --email phoenixilya@gmail.com --password 123
python3 manage.py generate_markup_django
python3 manage.py loaddata datasets/django/markup_django.json
python3 manage.py rebuild_index --noinput
