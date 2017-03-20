rm -r -f db.sqlite3
rm -r -f /data/poetry/
python3 manage.py migrate
python3 manage.py loaddata datasets/django/themes_django.json
python3 manage.py loaddata datasets/django/all_django.json
python3 manage.py createinitialrevisions
python3 manage.py create_superuser --email phoenixilya@gmail.com --password 123
python3 manage.py generate_markups --db
python3 manage.py generate_markups --to 3000 --xml datasets/corpus/markup_dump.xml --raw datasets/corpus/markup_dump.txt
python3 manage.py rebuild_index --noinput
