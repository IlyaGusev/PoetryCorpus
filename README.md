# Поэтический корпус русского языка #

[![Build Status](https://travis-ci.org/IlyaGusev/PoetryCorpus.svg?branch=master)](https://travis-ci.org/IlyaGusev/PoetryCorpus)
[![Code Climate](https://codeclimate.com/github/IlyaGusev/PoetryCorpus/badges/gpa.svg)](https://codeclimate.com/github/IlyaGusev/PoetryCorpus)

### Статистика корпуса текстов с метаинформацией ###
* Символов:  13208090
* Слов:  2186827
* Стихотворений:  16694
* Стихотворений, протегированных темами:  3904
* Авторов:  195

### Установка зависимостей вручную ###
```
sudo apt-get install build-essential libssl-dev libffi-dev python-dev libxslt1-dev libxslt1.1 libxml2-dev libxml2 libssl-dev
sudo pip3 install -r requirements.txt
```

### Препроцессинг ###
```
# "Пауки", собирающие тексты с сайтов
scrapy runspider poetry/apps/corpus/spiders/klassika.py -o datasets/web/klassika.xml
scrapy runspider poetry/apps/corpus/spiders/strofa.py -o datasets/web/strofa.xml
scrapy runspider poetry/apps/corpus/spiders/themes.py -o datasets/web/themes.xml
scrapy runspider poetry/apps/corpus/spiders/rupoem.py -o datasets/web/rupoem.xml
# Скрипт объединения и дедупликации текстов, генерация xml и json версий корпуса текстов
python3 poetry/apps/corpus/scripts/unite.py
```
or
```
# Получить готовую версию корпуса
git lfs pull
```

### Для инициализации базы данных с разметкой по слогам и ударениям ###
```
sh reset_db.sh
```

### Запуск через Docker Compose  ###
```
# Установка Docker и docker-compose
curl -sSL https://get.docker.com/ | sh
curl -L "https://github.com/docker/compose/releases/download/1.10.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
# Запуск
docker-compose up
```

### Литература ###
* Брейдо, 1996, [Автоматический анализ метрики русского стиха](http://search.rsl.ru/ru/record/01000000124)
* Каганов, 1996, [Лингвистическое конструирование в системах искусственного интеллекта](http://lleo.me/soft/text_dip.htm)
* Козьмин, 2006, [Автоматический анализ стиха в системе Starling](http://www.dialog-21.ru/digests/dialog2006/materials/html/Kozmin.htm)
* Гришина, 2008, [Поэтический корпус в рамках НКРЯ: общая структура и перспективы использования](http://ruscorpora.ru/sbornik2008/05.pdf)
* Пильщиков, Старостин, 2012, [Автоматическое распознавание метра: проблемы и решения](http://www.academia.edu/11465228/%D0%90%D0%B2%D1%82%D0%BE%D0%BC%D0%B0%D1%82%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%BE%D0%B5_%D1%80%D0%B0%D1%81%D0%BF%D0%BE%D0%B7%D0%BD%D0%B0%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5_%D0%BC%D0%B5%D1%82%D1%80%D0%B0_%D0%BF%D1%80%D0%BE%D0%B1%D0%BB%D0%B5%D0%BC%D1%8B_%D0%B8_%D1%80%D0%B5%D1%88%D0%B5%D0%BD%D0%B8%D1%8F)
* Барахнин, 2015, [Алгоритмы комплексного анализа русских поэтических текстов с целью автоматизации процесса создания метрических справочников и конкордансов](http://ceur-ws.org/Vol-1536/paper21.pdf), [сама система](http://poem.ict.nsc.ru/)  
