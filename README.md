# Поэтический корпус русского языка (учебный проект) #

[![Build Status](https://travis-ci.org/IlyaGusev/PoetryCorpus.svg?branch=master)](https://travis-ci.org/IlyaGusev/PoetryCorpus)

### Статистика корпуса текстов с метаинформацией ###
Символов:  13208090
Слов:  2186827
Стихотворений:  16694
Стихотворений, протегированных темами:  3904
Авторов:  195

### Установка ###
```
sudo apt-get install build-essential libssl-dev libffi-dev python-dev libxslt1-dev libxslt1.1 libxml2-dev libxml2 libssl-dev
sudo pip3 install -r requirements.txt
```

### Запуск ###
```
scrapy runspider poetry/apps/corpus/spiders/klassika.py -o datasets/web/klassika.xml
scrapy runspider poetry/apps/corpus/spiders/strofa.py -o datasets/web/strofa.xml
scrapy runspider poetry/apps/corpus/spiders/themes.py -o datasets/web/themes.xml
scrapy runspider poetry/apps/corpus/spiders/rupoem.py -o datasets/web/rupoem.xml
cd poetry
python3 scripts/unite.py
```
or
```
git lfs pull
```

### Для корпус-менеджера ###
```
sudo pip3 install -r requirements.txt
sh reset_db.sh
```

### Литература ###
Полная акцентуированная парадигма по А. А. Зализняку (86839 статей, 2645347 форм)
