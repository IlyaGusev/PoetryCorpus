# Поэтический корпус русского языка (учебный проект) #

### Установка ###
```
sudo apt-get install build-essential libssl-dev libffi-dev python-dev libxslt1-dev libxslt1.1 libxml2-dev libxml2 libssl-dev
sudo pip3 install -r requirements.txt
```

### Запуск ###
```
scrapy runspider poetry_corpus/spiders/klassika.py -o datasets/klassika.xml
scrapy runspider poetry_corpus/spiders/strofa.py -o datasets/strofa.xml
scrapy runspider poetry_corpus/spiders/themes.py -o datasets/themes.xml
scrapy runspider poetry_corpus/spiders/rupoem.py -o datasets/rupoem.xml
cd poetry_corpus
python3 scripts/unite.py
```
or
```
git lfs pull
```

### Для корпус-менеджера ###
```
sudo pip3 install Django
python3 manage.py migrate
python3 manage.py createsuperuser
python3 manage.py loaddata datasets/themes_django.json
python3 manage.py loaddata datasets/all_django.json
python3 manage.py createinitialrevisions
python3 manage.py runserver
```

### Литература ###
Полная акцентуированная парадигма по А. А. Зализняку (86839 статей, 2645347 форм)
