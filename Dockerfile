FROM python:3.6
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install -y git sqlite3 nginx supervisor

RUN pip3 install -U pip
RUN pip3 install uwsgi

RUN mkdir /code
ADD . /code/
RUN rm -r -f /code/conf
WORKDIR /code

RUN mkdir /conf
ADD ./conf /conf/
RUN chmod -R 755 /conf/

RUN mkdir -p /logs

RUN echo "daemon off;" >> /etc/nginx/nginx.conf
RUN rm /etc/nginx/sites-enabled/default
RUN ln -s /conf/nginx-app.conf /etc/nginx/sites-enabled/
RUN ln -s /conf/supervisor-app.conf /etc/supervisor/conf.d/

RUN pip3 install -r /code/requirements.txt

VOLUME  ["/code/db"]
EXPOSE 80
EXPOSE 9200
CMD ["/conf/run.sh"]
 
