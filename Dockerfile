FROM debian
ENV LANG C.UTF-8
ENV PYTHONUNBUFFERED 1
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
	python3 \
	python3-dev \
	python3-setuptools \
	python3-pip \
	python3-psycopg2 \
	libcap-dev && \
	pip3 install uwsgi && \
    rm -rf /var/lib/apt/lists/*
COPY requirements.txt /home/docker/requirements.txt
COPY api /var/www/api
COPY api_prototype /var/www/api_prototype
COPY database /var/www/database
COPY keyserver /var/www/keyserver
COPY pinytoCloud /var/www/pinytoCloud
COPY service /var/www/service
COPY webapps /var/www/webapps
COPY manage.py /var/www/manage.py
COPY project_path.py /var/www/project_path.py
COPY docker-setup/uwsgi-app.ini /etc/uwsgi/apps-enabled/uwsgi-app.ini
COPY docker-setup/init_and_run.sh /home/docker/init_and_run.sh
WORKDIR /home/docker/
RUN pip3 install -r requirements.txt
EXPOSE 3031
CMD ["/home/docker/init_and_run.sh"]
