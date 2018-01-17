#!/bin/bash

rm /code/poetry/settings.py
cp /conf/prod_settings.py /code/poetry/settings.py
chmod 777 /code/poetry/settings.py

#python3 /code/manage.py migrate --noinput --fake-initial
sh /code/reset_db.sh
python3 /code/manage.py collectstatic --noinput

chown -R www-data:www-data /code/
chmod -R u+rwX,go+rX /code/

supervisord -n
