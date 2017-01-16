python3 manage.py migrate
python3 manage.py loaddata datasets/themes_django.json
python3 manage.py loaddata datasets/all_django.json
python3 manage.py createinitialrevisions
python3 manage.py createsuperuser