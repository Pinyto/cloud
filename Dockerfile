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
COPY api /var/www/
COPY api_prototype /var/www/
COPY database /var/www/
COPY keyserver /var/www/
COPY pinytoCloud /var/www/
COPY service /var/www/
COPY webapps /var/www/
COPY manage.py /var/www/
COPY project_path.py /var/www/
COPY docker-setup/uwsgi-app.ini /etc/uwsgi/apps-enabled/uwsgi-app.ini
COPY docker-setup/init_and_run.sh /home/docker/init_and_run.sh
WORKDIR /home/docker/
RUN pip3 install -r requirements.txt
EXPOSE 3031
CMD ["/home/docker/init_and_run.sh"]
