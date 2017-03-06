rm -r -f db.sqlite3
rm -r -f /data/poetry/
python3 manage.py migrate
python3 manage.py loaddata datasets/django/themes_django.json
python3 manage.py loaddata datasets/django/all_django.json
python3 manage.py createinitialrevisions
python3 manage.py create_superuser --email phoenixilya@gmail.com --password 123

python3 manage.py generate_markup_django --from 0 --to 2000
python3 manage.py loaddata datasets/django/markup_django.json

python3 manage.py generate_markup_django --from 2000 --to 4000
python3 manage.py loaddata datasets/django/markup_django.json

python3 manage.py generate_markup_django --from 4000 --to 6000
python3 manage.py loaddata datasets/django/markup_django.json

python3 manage.py generate_markup_django --from 6000 --to 8000
python3 manage.py loaddata datasets/django/markup_django.json

python3 manage.py generate_markup_django --from 8000 --to 10000
python3 manage.py loaddata datasets/django/markup_django.json

python3 manage.py generate_markup_django --from 10000 --to 12000
python3 manage.py loaddata datasets/django/markup_django.json

python3 manage.py generate_markup_django --from 12000 --to 14000
python3 manage.py loaddata datasets/django/markup_django.json

python3 manage.py generate_markup_django --from 14000 --to 16000
python3 manage.py loaddata datasets/django/markup_django.json

python3 manage.py generate_markup_django --from 16000
python3 manage.py loaddata datasets/django/markup_django.json

python3 manage.py rebuild_index --noinput
